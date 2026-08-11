import ast

from .base import Rule, RuleMetadata
from .helpers import is_tool_call, call_name

from ..model.context import AnalysisContext
from ..model.finding import Finding, SourceLocation


DANGEROUS_TOOLS = {
    "execute_sql",
    "run_sql",
    "execute_command",
    "run_command",
    "shell",
    "write_file",
    "delete_file",
}


class Flow003(Rule):

    metadata = RuleMetadata(
        rule_id="FLOW003",
        name="Dangerous Tool Reachability",
        severity="HIGH",
        description="Detects agent/tool code reaching high-impact capabilities.",
    )

    def analyze(self, tree, context):

        findings = []

        for node in ast.walk(tree):

            if not isinstance(node, ast.Call):
                continue

            name = call_name(node).lower()

            if name not in DANGEROUS_TOOLS:
                continue

            findings.append(
                Finding(
                    rule_id="FLOW003",
                    severity="HIGH",
                    message=(
                        f"High-impact tool reachable: {call_name(node)}"
                    ),
                    location=SourceLocation(
                        context.source.path,
                        node.lineno,
                        node.col_offset + 1,
                    ),
                    evidence=context.snippet(node),
                    explanation=(
                        "The source contains a tool capable of "
                        "performing a high-impact operation such as "
                        "database mutation, command execution, or "
                        "filesystem modification."
                    ),
                    remediation=(
                        "Place the capability behind explicit authorization, "
                        "input validation, policy enforcement, and least-"
                        "privilege boundaries."
                    ),
                )
            )

        return findings