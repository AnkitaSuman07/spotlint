from dataclasses import dataclass


@dataclass(frozen=True)
class AnalyzerConfig:

    minimum_severity: str = "LOW"

    recursive: bool = True

    rule_ids: set[str] | None = None