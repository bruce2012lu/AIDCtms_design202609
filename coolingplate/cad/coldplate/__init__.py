"""CP-B300 冷板 AI CAD 能力。

分层：params(数据) -> model(派生) -> rules(判断) -> geometry(实体) -> backends(落地)
判断必须在建模之前，落地后端可插拔。
"""

from .model import Derived, Spec, SpecError, load_spec
from .rules import Finding, RuleViolation, require_clean, validate

__all__ = [
    "Derived",
    "Finding",
    "RuleViolation",
    "Spec",
    "SpecError",
    "load_spec",
    "require_clean",
    "validate",
]
