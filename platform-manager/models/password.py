from dataclasses import dataclass
from typing import Optional, Set

@dataclass(frozen=True)
class PasswordPolicy:
    min_length: int
    max_length: Optional[int] = None
    require_upper: bool = False
    require_lower: bool = False
    require_number: bool = False
    allowed_symbols: Optional[Set[str]] = None
    only_latin: bool = False
    check_leak: bool = False

    def get_requirements_data(self) -> list[dict]:
        """Returns a list of requirement definitions based on the policy."""
        reqs = []
        if self.min_length:
            reqs.append({"id": "min_length", "text": f" At least {self.min_length} characters long"})
        if self.max_length:
            reqs.append({"id": "max_length", "text": f" Maximum of {self.max_length} characters"})
        if self.require_upper:
            reqs.append({"id": "upper", "text": " At least one uppercase letter"})
        if self.require_lower:
            reqs.append({"id": "lower", "text": " At least one lowercase letter"})
        if self.require_number:
            reqs.append({"id": "number", "text": " At least one number"})
        if self.only_latin:
            reqs.append({"id": "latin_only", "text": " Only Latin characters allowed"})
        if self.allowed_symbols:
            symbols_str = " ".join(sorted(self.allowed_symbols))
            reqs.append({"id": "symbols", "text": f" Allowed symbols: {symbols_str}"})
        
        return reqs

PANEL_PASSWORD_POLICY = PasswordPolicy(
    min_length=12,
    require_upper=True,
    require_lower=True,
    require_number=True,
    check_leak=True,
)

VPS_PASSWORD_POLICY = PasswordPolicy(
    min_length=12,
    max_length=50,
    require_upper=True,
    require_lower=True,
    require_number=True,
    allowed_symbols=set("-().&@?'#,/;+"),
    only_latin=True,
    check_leak=False,
)