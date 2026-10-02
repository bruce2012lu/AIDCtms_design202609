"""cp-design 本地工具服务。

两条入口：
  python server.py              MCP stdio（给 Cursor / Claude 调 CAD 门）
  python server.py --http 8765  同时提供冷板设计台 HTML

几何导出一律走子进程，并且必须 confirm=true。
参数化内核只能表达 CP-B300-JM-01 v1.0 这一类几何；
v2 的各向异性节距、asm_0921 三层板、Grace 冷板会在这里被明确拒绝，而不是画错。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import traceback
from dataclasses import asdict
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

AGENT = Path(__file__).resolve().parents[1]
ROOT = AGENT.parents[1]
CAD = ROOT / "cad"
UI = AGENT / "ui"
RUNS = AGENT / "runs"
PARAMS = CAD / "params" / "cp_b300_jm01.yaml"
VENV_PY = CAD / ".venv" / "Scripts" / "python.exe"

sys.path.insert(0, str(CAD))
sys.path.insert(0, str(AGENT))
from oned import design as oned_design
from zones import grace_design, hbm_design

KERNEL = {
    "id": "coldplate-parametric-v1",
    "entry": "cad/build.py",
    "params": "cad/params/cp_b300_jm01.yaml",
    "parts": [
        "JM01-100_base_plate",
        "JM01-200_nozzle_plate",
        "JM01-400_seal_frame",
    ],
    "stack": "余铜 + 短槽 + 喷距 + 喷嘴板 + 周边钎缝",
    "pitch": "单一 jets.pitch，X/Y 不能分开",
    "holes": "n_dies * count_x * count_y，方阵",
    "suction": "geometry.py 会按 jets.suction_diameter 打抽吸孔，yaml 仍标 suction_candidate",
    "cannot_build": [
        "各向异性节距（v2 的 Sx=3.0、Sy=2.4）",
        "asm_0921 的 12.5 mm 三层静压箱（PLATE/COVER1/COVER2）",
        "Grace CP-GRACE-MC-01 平行微通道",
        "水嘴、UQD、托盘歧管",
        "UC-01b 单元胞网格（那是 CFD 网格脚本，不是本 CAD 内核）",
    ],
}


def _json(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _set_path(obj: dict, path: str, value) -> None:
    keys = path.split(".")
    cur = obj
    for key in keys[:-1]:
        nxt = cur.get(key)
        if not isinstance(nxt, dict):
            raise KeyError(path)
        cur = nxt
    leaf = keys[-1]
    if leaf not in cur:
        raise KeyError(path)
    cur[leaf] = value


def _load_raw(params: str | None) -> tuple[dict, str]:
    path = Path(params) if params else PARAMS
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("参数文件必须在冷板目录内") from exc
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise ValueError("只接受 yaml 参数集")
    import yaml

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("参数集不是 mapping")
    return raw, str(path.relative_to(ROOT)).replace("\\", "/")


def inspect_spec(params: str | None = None, overlay: dict | None = None) -> dict:
    raw, source = _load_raw(params)
    applied: dict = {}
    rejected: list[dict] = []
    for key, value in (overlay or {}).items():
        try:
            _set_path(raw, str(key), value)
            applied[str(key)] = value
        except KeyError:
            rejected.append({
                "path": str(key),
                "reason": "参数化内核没有这个字段。各向异性节距请看知识库 cad-kernel-gap。",
            })

    from coldplate.model import Spec
    from coldplate.rules import validate

    spec = Spec(raw)
    derived = spec.derive()
    findings = [
        {"level": f.level, "code": f.code, "message": f.message}
        for f in validate(spec, derived)
    ]
    counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
    for f in findings:
        counts[f["level"]] += 1
    if counts["ERROR"]:
        gate = "block"
    elif counts["WARN"]:
        gate = "warn"
    else:
        gate = "pass"
    plate = raw["plate"]
    grooves = raw["gpu_grooves"]
    return {
        "model": spec.model,
        "status": raw["meta"].get("status"),
        "source": source,
        "overlay_applied": applied,
        "overlay_rejected": rejected,
        "derived": {k: _round(v) for k, v in asdict(derived).items()},
        "findings": findings,
        "counts": counts,
        "gate": gate,
        "stack_mm": {
            "base_remaining": plate["base_remaining"],
            "groove_depth": grooves["depth"],
            "jet_standoff": plate["jet_standoff"],
            "nozzle_plate_t": plate["nozzle_plate_t"],
            "braze_seam": plate["braze_seam"],
            "outline": plate["thickness"],
            "cavity": derived.cavity_thickness,
        },
        "kernel": KERNEL,
    }


def _round(value):
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, tuple):
        return [_round(v) for v in value]
    return value


def cad_tracks() -> dict:
    return _read_json(AGENT / "knowledge" / "cad-tracks.json")


def kb_catalog() -> dict:
    return _read_json(AGENT / "knowledge" / "catalog.json")


def memory_list() -> dict:
    items = []
    sem = AGENT / "memory" / "semantic"
    for path in sorted(sem.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta = {}
        if text.startswith("---"):
            _, front, body = text.split("---", 2)
            for line in front.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            preview = body.strip().splitlines()
        else:
            preview = text.strip().splitlines()
        title = next((ln[2:] for ln in preview if ln.startswith("# ")), path.stem)
        items.append({
            "file": f"agent/practice01_0926/memory/semantic/{path.name}",
            "title": title,
            "meta": meta,
        })
    return {"profile": "agent/practice01_0926/memory/profile.md", "semantic": items}


def build_spec(overlay: dict | None, backend: str, allow_warn: bool, confirm: bool) -> dict:
    if confirm is not True:
        return {
            "ok": False,
            "gate": "block",
            "message": "几何导出需要 confirm=true。先 cad_inspect，确认门通过后再导出。",
        }
    report = inspect_spec(overlay=overlay)
    if report["overlay_rejected"]:
        return {"ok": False, "gate": "block", "inspect": report,
                "message": "有字段被内核拒绝，没有写文件。"}
    if report["counts"]["ERROR"]:
        return {"ok": False, "gate": "block", "inspect": report,
                "message": "ERROR 级规则未通过，拒绝建模。"}
    if report["counts"]["WARN"] and not allow_warn:
        return {"ok": False, "gate": "warn", "inspect": report,
                "message": "存在 WARN。确认偏离 v1.0 报告后，把 allow_warn 设为 true。"}

    import yaml

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run = RUNS / stamp
    run.mkdir(parents=True, exist_ok=True)
    raw, _source = _load_raw(None)
    for key, value in (overlay or {}).items():
        _set_path(raw, str(key), value)
    raw["meta"]["status"] = "agent-candidate"
    params_path = run / "params.yaml"
    params_path.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding="utf-8")

    py = str(VENV_PY if VENV_PY.exists() else Path(sys.executable))
    cmd = [py, str(CAD / "build.py"), "build",
           "--params", str(params_path),
           "--out", str(run),
           "--backend", backend]
    if allow_warn:
        cmd.append("--allow-warn")
    proc = subprocess.run(
        cmd, cwd=str(CAD), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
    )
    files = [str(p.relative_to(ROOT)).replace("\\", "/")
             for p in run.rglob("*") if p.is_file() and p.name != "params.yaml"]
    access_violation = proc.returncode in {3221225477, -1073741819}
    return {
        "ok": proc.returncode == 0,
        "gate": "built" if proc.returncode == 0 else "block",
        "returncode": proc.returncode,
        "access_violation": access_violation,
        "message": ("OCC 偶发段错误。参数未改冻结 yaml，可直接重试。"
                    if access_violation else "建模子进程已结束。"),
        "run": str(run.relative_to(ROOT)).replace("\\", "/"),
        "files": files,
        "log_tail": (proc.stdout + "\n" + proc.stderr)[-4000:],
        "inspect": report,
    }


TOOLS = [
    {
        "name": "kb_catalog",
        "description": "列出冷板设计知识库条目（报告、专利、文献、CFD、CAD）。",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "memory_list",
        "description": "列出本智能体语义记忆及置信度。",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "cad_tracks",
        "description": "返回四条 CAD 轨道：参数化 v1、实测 asm_0921、Grace 概念、托盘示意。改几何前必须先看轨道。",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "cad_inspect",
        "description": "对冻结参数集做可选覆盖，然后派生热工水力并跑 rules.py。不写文件、不建模。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "params": {"type": "string", "description": "相对冷板根目录的 yaml，默认 v1 冻结集"},
                "overlay": {
                    "type": "object",
                    "description": "点路径覆盖，例如 {\"jets.diameter\": 0.4}",
                },
            },
        },
    },
    {
        "name": "cad_build",
        "description": "规则门通过后，在 agent/practice01_0926/runs/ 导出几何。不覆盖冻结 yaml。必须 confirm=true。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "overlay": {"type": "object"},
                "backend": {"type": "string", "enum": ["preview", "drawing", "neutral", "all"]},
                "allow_warn": {"type": "boolean"},
                "confirm": {"type": "boolean"},
            },
            "required": ["confirm"],
        },
    },
    {
        "name": "oned_design",
        "description": "一维设计。Re、开孔率、H/D 都在 Martin 1977 域内才采用阵列式；否则按低雷诺数短槽层流加驻点核给出保证值。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "point": {"type": "string", "enum": ["DP-A", "DP-B"]},
                "D_mm": {"type": "number"},
                "Q_lpm": {"type": "number"},
                "N": {"type": "integer"},
                "H_mm": {"type": "number"},
                "Sx_mm": {"type": "number"},
                "Sy_mm": {"type": "number"},
            },
        },
    },
    {
        "name": "hbm_design",
        "description": "B300 的 HBM 区一维设计。无喷嘴，低雷诺数平槽，近壁流速不超过 0.80 m/s。",
        "inputSchema": {"type": "object", "properties": {
            "point": {"type": "string"},
            "Q_hbm_lpm": {"type": "number"},
            "n_per_side": {"type": "integer"},
            "w_mm": {"type": "number"},
            "d_mm": {"type": "number"},
            "pitch_mm": {"type": "number"},
            "L_mm": {"type": "number"},
        }},
    },
    {
        "name": "grace_design",
        "description": "Grace CP-GRACE-MC-01 一维设计。平行微通道，无微射流，CPU 260 W，内存合计 40 W。",
        "inputSchema": {"type": "object", "properties": {
            "Q_lpm": {"type": "number"},
            "n_cpu": {"type": "integer"},
            "w_cpu_mm": {"type": "number"},
            "d_cpu_mm": {"type": "number"},
            "L_cpu_mm": {"type": "number"},
            "pitch_cpu_mm": {"type": "number"},
        }},
    },
]


def call_tool(name: str, arguments: dict | None) -> dict:
    args = arguments or {}
    if name == "kb_catalog":
        return kb_catalog()
    if name == "memory_list":
        return memory_list()
    if name == "cad_tracks":
        return cad_tracks()
    if name == "cad_inspect":
        return inspect_spec(args.get("params"), args.get("overlay") or {})
    if name == "cad_build":
        return build_spec(
            args.get("overlay") or {},
            args.get("backend") or "preview",
            bool(args.get("allow_warn")),
            args.get("confirm") is True,
        )
    if name == "oned_design":
        return oned_design(args)
    if name == "hbm_design":
        return hbm_design(args)
    if name == "grace_design":
        return grace_design(args)
    raise KeyError(name)


def _mcp_result(payload: dict) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}]}


def serve_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("method") == "notifications/initialized":
            continue
        mid = msg.get("id")
        method = msg.get("method")
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "cp-design", "version": "1.0.0"},
                }
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = msg.get("params") or {}
                result = _mcp_result(call_tool(params.get("name"), params.get("arguments")))
            elif method == "ping":
                result = {}
            else:
                if mid is None:
                    continue
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32601, "message": f"unknown method {method}"},
                }, ensure_ascii=False) + "\n")
                sys.stdout.flush()
                continue
            if mid is not None:
                sys.stdout.write(json.dumps(
                    {"jsonrpc": "2.0", "id": mid, "result": result},
                    ensure_ascii=False,
                ) + "\n")
                sys.stdout.flush()
        except Exception as exc:  # noqa: BLE001 — MCP 需要把工具错误返回给调用方
            if mid is None:
                continue
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0", "id": mid,
                "error": {"code": -32000, "message": f"{type(exc).__name__}: {exc}"},
            }, ensure_ascii=False) + "\n")
            sys.stdout.flush()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        static = {
            "/": UI / "index.html",
            "/index.html": UI / "index.html",
            "/styles.css": UI / "styles.css",
            "/app.js": UI / "app.js",
        }
        if path in static:
            file = static[path]
            kind = "text/html; charset=utf-8" if file.suffix == ".html" else (
                "text/css; charset=utf-8" if file.suffix == ".css" else "text/javascript; charset=utf-8"
            )
            self._send(200, file.read_bytes(), kind)
            return
        routes = {
            "/api/health": lambda: {
                "ok": True,
                "agent": "cp-design",
                "venv": VENV_PY.exists(),
                "params": PARAMS.exists(),
            },
            "/api/catalog": kb_catalog,
            "/api/memory": memory_list,
            "/api/cad/tracks": cad_tracks,
            "/api/cad/kernel": lambda: KERNEL,
        }
        if path in routes:
            try:
                self._send(200, _json(routes[path]()), "application/json; charset=utf-8")
            except Exception:
                self._send(500, _json({"ok": False, "trace": traceback.format_exc()}),
                           "application/json; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(400, _json({"ok": False, "message": "请求体不是 JSON"}),
                       "application/json; charset=utf-8")
            return
        try:
            if path == "/api/cad/inspect":
                body = inspect_spec(payload.get("params"), payload.get("overlay") or {})
            elif path == "/api/cad/build":
                body = build_spec(
                    payload.get("overlay") or {},
                    payload.get("backend") or "preview",
                    bool(payload.get("allow_warn")),
                    payload.get("confirm") is True,
                )
            elif path == "/api/oned/design":
                body = oned_design(payload)
            elif path == "/api/hbm/design":
                body = hbm_design(payload)
            elif path == "/api/grace/design":
                body = grace_design(payload)
            else:
                self._send(404, _json({"ok": False, "message": "未知接口"}),
                           "application/json; charset=utf-8")
                return
            self._send(200, _json(body), "application/json; charset=utf-8")
        except Exception as exc:  # noqa: BLE001
            self._send(400, _json({
                "ok": False, "message": f"{type(exc).__name__}: {exc}",
            }), "application/json; charset=utf-8")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="cp-design MCP / 设计台")
    ap.add_argument("--http", type=int, default=0, help="同时提供 HTML，端口例如 8765")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        report = inspect_spec()
        bad = inspect_spec(overlay={"jets.pitch_x": 3.0, "jets.diameter": 0.25})
        print(json.dumps({
            "frozen_gate": report["gate"],
            "frozen_counts": report["counts"],
            "illegal_gate": bad["gate"],
            "illegal_codes": [f["code"] for f in bad["findings"] if f["level"] == "ERROR"],
            "rejected": bad["overlay_rejected"],
            "jet_count": report["derived"]["jet_count"],
            "re": report["derived"]["jet_reynolds"],
        }, ensure_ascii=False))
        if report["counts"]["ERROR"]:
            raise SystemExit(2)
        return
    if args.http:
        httpd = ThreadingHTTPServer(("127.0.0.1", args.http), Handler)
        sys.stderr.write(f"cp-design 设计台 http://127.0.0.1:{args.http}/\n")
        httpd.serve_forever()
        return
    serve_stdio()


if __name__ == "__main__":
    main()
