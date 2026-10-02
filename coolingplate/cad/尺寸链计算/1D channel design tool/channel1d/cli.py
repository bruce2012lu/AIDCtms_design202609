# -*- coding: utf-8 -*-
"""Command line for the rectangular-channel column screen."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from channel1d.bulk import evaluate
from channel1d.chain import ChainLimits, chain_sum, limit_failures
from channel1d.fluid import Fluid
from channel1d.solver import ColumnDesign, solve
from channel1d.sweep import sweep


def load_preset(path: Path) -> dict:
    """Read a preset JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def design_from_section(preset: dict, section_name: str) -> ColumnDesign:
    """Build a column design from one named section of a preset."""
    fluid_raw = preset["fluid"]
    section = preset["sections"][section_name]
    stacks = tuple((float(a), float(b)) for a, b in preset["stacks_m"])
    return ColumnDesign(
        fluid=Fluid(
            rho=float(fluid_raw["rho"]),
            cp=float(fluid_raw["cp"]),
            mu=float(fluid_raw["mu"]),
            k=float(fluid_raw["k"]),
        ),
        k_copper=float(preset["copper_k"]),
        tin_c=float(preset["inlet_c"]),
        flow_lpm=float(preset["flow_lpm"]),
        power_w=float(preset["power_w"]),
        column_width_m=float(preset["column_width_m"]),
        column_length_m=float(preset["column_length_m"]),
        heated_length_m=float(preset["heated_length_m"]),
        channel_height_m=float(preset["channel_height_m"]),
        base_m=float(preset["base_thickness_m"]),
        n=int(section["n"]),
        width_m=float(section["width_m"]),
        rib_m=float(section["rib_m"]),
        land_m=float(section["land_m"]),
        stacks_m=stacks,
        k_split=float(preset.get("k_split", 1.5)),
    )


def limits_from_preset(preset: dict) -> ChainLimits:
    raw = preset.get("limits", {})
    return ChainLimits(
        min_rib_m=float(raw.get("min_rib_m", 0.30e-3)),
        min_width_m=float(raw.get("min_width_m", 0.40e-3)),
        min_land_m=float(raw.get("min_land_m", 0.30e-3)),
        max_aspect=float(raw.get("max_aspect", 5.0)),
        velocity_cap_m_s=float(raw.get("velocity_cap_m_s", 0.80)),
    )


def bulk_of(design: ColumnDesign) -> dict[str, float]:
    return evaluate(
        design.fluid,
        n=design.n,
        width_m=design.width_m,
        rib_m=design.rib_m,
        height_m=design.channel_height_m,
        heated_length_m=design.heated_length_m,
        column_length_m=design.column_length_m,
        flow_lpm=design.flow_lpm,
        power_w=design.power_w,
        k_copper=design.k_copper,
    )


def format_bulk(name: str, design: ColumnDesign, bulk: dict[str, float]) -> str:
    total_mm = chain_sum(design.land_m, design.n, design.width_m, design.rib_m) * 1e3
    lines = [
        (
            f"{name}: n={design.n}  w={design.width_m*1e3:.3f} mm  "
            f"rib={design.rib_m*1e3:.3f} mm  land={design.land_m*1e3:.3f} mm  "
            f"H={design.channel_height_m*1e3:.2f} mm"
        ),
        f"  chain = {total_mm:.3f} mm",
        f"  V = {bulk['V']:.4f} m/s   V_leg = {bulk['V_leg']:.4f} m/s   Re = {bulk['Re']:.2f}",
        f"  Dh = {bulk['Dh_mm']:.3f} mm   Nu = {bulk['Nu']:.3f}   h = {bulk['h']:.1f}   eta = {bulk['eta']:.4f}",
        f"  dTf = {bulk['dTf']:.3f} K   dTf_leg = {bulk['dTf_leg']:.3f} K   dTconv = {bulk['dTconv']:.3f} K",
        f"  dP = {bulk['dP_Pa']:.2f} Pa   fRe = {bulk['fRe']:.3f}",
    ]
    return "\n".join(lines)


def run_bulk_check(preset: dict) -> tuple[bool, list[str]]:
    """Compare the named section with the three published bulk targets."""
    spec = preset["bulk_check"]
    design = design_from_section(preset, spec["section"])
    bulk = bulk_of(design)
    tol = float(spec.get("tolerance", 0.05))
    checks = (
        ("dTf", bulk["dTf"], float(spec["dTf"])),
        ("dTconv", bulk["dTconv"], float(spec["dTconv"])),
        ("dP_Pa", bulk["dP_Pa"], float(spec["dP_Pa"])),
    )
    lines = [f"bulk check on {spec['section']}, tolerance {tol}"]
    ok = True
    for label, got, target in checks:
        err = abs(got - target)
        status = "PASS" if err <= tol else "FAIL"
        if status == "FAIL":
            ok = False
        lines.append(f"  {label}: got {got:.4f}  target {target}  |err| {err:.4f}  {status}")
    return ok, lines


def result_payload(preset: dict, ny: int, iters: int, do_solve: bool, do_sweep: bool) -> dict:
    limits = limits_from_preset(preset)
    sections_out = {}
    for name, section in preset["sections"].items():
        design = design_from_section(preset, name)
        bulk = bulk_of(design)
        failed = limit_failures(
            land_m=design.land_m,
            n=design.n,
            width_m=design.width_m,
            rib_m=design.rib_m,
            height_m=design.channel_height_m,
            column_width_m=design.column_width_m,
            velocity_m_s=bulk["V"],
            limits=limits,
        )
        entry: dict = {
            "inputs": section,
            "chain_mm": chain_sum(design.land_m, design.n, design.width_m, design.rib_m) * 1e3,
            "limit_failures": failed,
            "bulk": bulk,
        }
        if do_solve:
            solved = {}
            for scheme in section.get("schemes", ["cross"]):
                field = solve(design, scheme, ny=ny, iters=iters)
                field.pop("bulk", None)
                solved[scheme] = _jsonable(field)
            entry["segmented"] = solved
        sections_out[name] = entry
    payload: dict = {"preset_sections": sections_out, "ny": ny, "iters": iters}
    if do_sweep:
        template = design_from_section(preset, "retained" if "retained" in preset["sections"] else next(iter(preset["sections"])))
        payload["sweep_center_top"] = sweep(template, scheme="center", ny=min(ny, 25), iters=min(iters, 80), limits=limits)[:15]
    return payload


def _jsonable(value):
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, float):
        return round(value, 6)
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="1D rectangular-channel column screen")
    parser.add_argument("--preset", required=True, help="Preset JSON path")
    parser.add_argument("--bulk-check", action="store_true", help="Print bulk dTf, dTconv, and dP and compare them with the preset targets")
    parser.add_argument("--solve", action="store_true", help="Run the segmented march for each scheme listed in the preset")
    parser.add_argument("--sweep", action="store_true", help="Sweep width and rib on the center-feed scheme")
    parser.add_argument("--ny", type=int, default=50)
    parser.add_argument("--iters", type=int, default=6400)
    parser.add_argument("--out", help="Write a result JSON for the next iteration")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    preset = load_preset(Path(args.preset))
    do_bulk = args.bulk_check or not (args.solve or args.sweep or args.out)
    ok = True
    if do_bulk or args.out:
        for name in preset["sections"]:
            design = design_from_section(preset, name)
            print(format_bulk(name, design, bulk_of(design)))
    if do_bulk and "bulk_check" in preset:
        passed, lines = run_bulk_check(preset)
        print("\n".join(lines))
        ok = passed
    if args.solve or args.sweep or args.out:
        payload = result_payload(preset, args.ny, args.iters, args.solve or bool(args.out), args.sweep)
        if args.solve:
            for name, entry in payload["preset_sections"].items():
                segmented = entry.get("segmented", {})
                for scheme, field in segmented.items():
                    print(
                        f"{name} {scheme}: Tmin {field['Tmin']:.3f}  Tmean {field['Tmean']:.3f}  "
                        f"Tmax {field['Tmax']:.3f}  dT {field['dT']:.3f}"
                    )
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print("wrote", args.out)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
