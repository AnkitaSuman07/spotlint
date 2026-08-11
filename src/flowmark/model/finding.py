from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class SourceLocation:
    file: str
    line: int
    column: int


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    location: SourceLocation
    evidence: str
    explanation: str
    remediation: str

    def to_dict(self) -> dict:
        return asdict(self)