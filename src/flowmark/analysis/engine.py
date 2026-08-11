import ast
from pathlib import Path

from ..config import AnalyzerConfig
from ..model.context import AnalysisContext, SourceFile
from ..model.finding import Finding
from ..rules.registry import RuleRegistry


SEVERITY = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


class AnalysisEngine:

    def __init__(
        self,
        registry: RuleRegistry,
        config: AnalyzerConfig,
    ):
        self.registry = registry
        self.config = config

    def analyze_path(
        self,
        path: Path,
    ) -> list[Finding]:

        files = self._discover(path)

        findings: list[Finding] = []

        for file in files:
            findings.extend(
                self._analyze_file(file)
            )

        return sorted(
            findings,
            key=lambda finding: (
                finding.location.file,
                finding.location.line,
                finding.rule_id,
            ),
        )

    def _discover(self, path: Path) -> list[Path]:

        if not path.exists():
            raise OSError(
                f"Path does not exist: {path}"
            )

        if path.is_file():

            if path.suffix != ".py":
                return []

            return [path]

        pattern = (
            "**/*.py"
            if self.config.recursive
            else "*.py"
        )

        return sorted(
            path.glob(pattern)
        )

    def _analyze_file(
        self,
        path: Path,
    ) -> list[Finding]:

        source = path.read_text(
            encoding="utf-8"
        )

        try:

            tree = ast.parse(
                source,
                filename=str(path),
            )

        except SyntaxError as exc:

            raise ValueError(
                f"Syntax error in "
                f"{path}:{exc.lineno}: "
                f"{exc.msg}"
            ) from exc

        source_file = SourceFile(
            path=str(path),
            text=source,
            tree=tree,
        )

        context = AnalysisContext(
            source=source_file
        )

        findings: list[Finding] = []

        rules = self.registry.select(
            self.config.rule_ids
        )

        for rule in rules:

            rule_findings = rule.analyze(
                tree,
                context,
            )

            findings.extend(
                rule_findings
            )

        minimum = SEVERITY[
            self.config.minimum_severity
        ]

        return [
            finding
            for finding in findings
            if SEVERITY[finding.severity]
            >= minimum
        ]
