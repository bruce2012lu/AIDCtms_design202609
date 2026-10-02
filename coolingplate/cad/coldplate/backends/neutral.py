"""中性格式后端：STEP / STL。

STEP 是给下游 CFD 和供应商报价用的唯一交换格式；STL 只用于快速目视和
3D 打印验证件，不作为出货依据（报告明确不把整板金属 3D 打印作出货基线）。
"""

from __future__ import annotations

from pathlib import Path

from build123d import Compound, export_step, export_stl

from ..geometry import ColdPlateBuild
from ..model import Spec


def export(spec: Spec, build_result: ColdPlateBuild, assembly: Compound,
           out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    model = spec.model

    asm_step = out_dir / f"{model}_assembly.step"
    export_step(assembly, str(asm_step))
    written.append(asm_step)

    asm_stl = out_dir / f"{model}_assembly.stl"
    export_stl(assembly, str(asm_stl))
    written.append(asm_stl)

    for name, part in build_result.parts.items():
        p = out_dir / f"{model}_{name}.step"
        export_step(part, str(p))
        written.append(p)

    return written
