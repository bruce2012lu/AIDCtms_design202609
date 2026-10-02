"""CP-B300 冷板 AI CAD 入口。

用法：
    python build.py check                     只跑规则，不建模
    python build.py build                     校验 + 建模 + 导出 STEP/STL/DXF
    python build.py build --backend neutral   只出中性格式
    python build.py macro                     产出 SOLIDWORKS VBA 宏
    python build.py sw                        实时 COM 驱动 SOLIDWORKS（需实机）
    python build.py build --params other.yaml --allow-warn

默认拒绝在有 ERROR 级规则未通过时建模——几何画得出来不等于做得出来。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PARAMS = ROOT / "params" / "cp_b300_jm01.yaml"
DEFAULT_OUT = ROOT / "out"

LEVEL_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}


def _report(findings, verbose: bool) -> tuple[int, int]:
    n_err = sum(1 for f in findings if f.level == "ERROR")
    n_warn = sum(1 for f in findings if f.level == "WARN")
    shown = [f for f in findings if verbose or f.level != "INFO"]
    for f in sorted(shown, key=lambda f: LEVEL_ORDER[f.level]):
        print(f"  {f.level:5} [{f.code}] {f.message}")
    n_info = len(findings) - n_err - n_warn
    print(f"\n  规则汇总：ERROR {n_err} · WARN {n_warn} · INFO {n_info}")
    return n_err, n_warn


def _load(args):
    from coldplate import load_spec, validate

    spec = load_spec(args.params)
    derived = spec.derive()
    findings = validate(spec, derived)
    print(f"\n参数集 {Path(args.params).name} · 型号 {spec.model} · "
          f"状态 {spec.raw['meta']['status']}\n")
    n_err, n_warn = _report(findings, args.verbose)
    return spec, derived, n_err, n_warn


def _gate(n_err: int, n_warn: int, args) -> None:
    if n_err:
        print("\n拒绝建模：存在 ERROR 级规则未通过。", file=sys.stderr)
        raise SystemExit(2)
    if n_warn and not args.allow_warn:
        print("\n拒绝建模：存在 WARN（参数已偏离设计报告 v1.0）。"
              "确认无误后加 --allow-warn。", file=sys.stderr)
        raise SystemExit(3)


def cmd_check(args) -> None:
    _spec, derived, n_err, n_warn = _load(args)
    print(f"\n  派生量：射流 {derived.jet_count} 孔 · 孔速 "
          f"{derived.jet_velocity_m_s:.3f} m/s · Re_D {derived.jet_reynolds:.0f}")
    print(f"          短槽 {derived.groove_count_total} 条并联 · "
          f"{derived.groove_velocity_m_s:.3f} m/s · Re {derived.groove_reynolds:.0f} · "
          f"分{derived.groove_segments}段 x {derived.groove_segment_length:.2f} mm")
    print(f"          HBM 槽速 {derived.hbm_channel_velocity_m_s:.3f} m/s · "
          f"温升 {derived.fluid_temp_rise_k:.2f} K · 出口 {derived.outlet_temp_c:.2f} C")
    raise SystemExit(2 if n_err else 0)


def cmd_build(args) -> None:
    spec, derived, n_err, n_warn = _load(args)
    _gate(n_err, n_warn, args)

    from coldplate import geometry

    print("\n建模中……")
    result = geometry.build(spec, derived)
    assembly = geometry.assemble(spec, result)

    bbox = assembly.bounding_box()
    print(f"  总装包围盒 {bbox.size.X:.2f} x {bbox.size.Y:.2f} x {bbox.size.Z:.2f} mm")
    expected = (float(spec.plate["width"]), float(spec.plate["height"]),
                float(spec.plate["thickness"]))
    if any(abs(a - b) > 1e-6 for a, b in
           zip((bbox.size.X, bbox.size.Y, bbox.size.Z), expected)):
        print(f"  警告：包围盒与声明外形 {expected} 不一致", file=sys.stderr)

    out_dir = Path(args.out)
    written: list[Path] = []
    if args.backend in ("all", "neutral"):
        from coldplate.backends import neutral
        written += neutral.export(spec, result, assembly, out_dir)
    if args.backend in ("all", "drawing"):
        from coldplate.backends import drawing
        written += drawing.export(spec, derived, out_dir)
    if args.backend in ("all", "preview"):
        from coldplate.backends import preview
        written += preview.export(spec, derived, out_dir)

    print("\n产物：")
    for p in written:
        print(f"  {p.relative_to(ROOT)}  ({p.stat().st_size / 1024:.0f} KB)")


def cmd_macro(args) -> None:
    spec, derived, n_err, n_warn = _load(args)
    _gate(n_err, n_warn, args)

    from coldplate.backends import solidworks

    written = solidworks.write_macro(spec, derived, Path(args.out))
    print("\n产物：")
    for p in written:
        print(f"  {p.relative_to(ROOT)}  ({p.stat().st_size / 1024:.0f} KB)")
    print("\n在装了 SOLIDWORKS 的机器上：工具 > 宏 > 编辑，粘贴后运行 main。"
          "\n本宏未经实机验证，首跑请核对 FeatureExtrusion3 / FeatureCut4 参数个数。")


def cmd_sw(args) -> None:
    spec, derived, n_err, n_warn = _load(args)
    _gate(n_err, n_warn, args)

    from coldplate.backends import solidworks

    if not solidworks.is_available():
        print("\n本机未检测到 SOLIDWORKS COM 服务。改用 `python build.py macro` "
              "产出宏，拿到实机运行。", file=sys.stderr)
        raise SystemExit(4)

    step = Path(args.out) / f"{spec.model}_assembly.step"
    if not step.exists():
        print(f"\n先跑 `python build.py build` 生成 {step.name}", file=sys.stderr)
        raise SystemExit(5)

    written = solidworks.drive(spec, derived, step, Path(args.out))
    print("\n产物：")
    for p in written:
        print(f"  {p.relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> None:
    # 公共参数放进 parent，这样 `build.py --verbose check` 和
    # `build.py check --verbose` 两种顺序都能用
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--params", default=str(DEFAULT_PARAMS), help="参数集 yaml")
    common.add_argument("--out", default=str(DEFAULT_OUT), help="产物目录")
    common.add_argument("--verbose", action="store_true", help="连 INFO 级对账一起打印")
    common.add_argument("--allow-warn", action="store_true", help="容忍 WARN 继续建模")

    ap = argparse.ArgumentParser(
        prog="build.py", parents=[common],
        description="CP-B300 微通道+冲击换热冷板 · 参数化 CAD")

    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", parents=[common], help="只跑规则校验")
    b = sub.add_parser("build", parents=[common], help="校验 + 建模 + 导出")
    b.add_argument("--backend",
                   choices=["all", "neutral", "drawing", "preview"], default="all")
    sub.add_parser("macro", parents=[common], help="产出 SOLIDWORKS VBA 宏")
    sub.add_parser("sw", parents=[common], help="实时 COM 驱动 SOLIDWORKS")

    args = ap.parse_args(argv)
    {"check": cmd_check, "build": cmd_build,
     "macro": cmd_macro, "sw": cmd_sw}[args.cmd](args)


if __name__ == "__main__":
    main()
