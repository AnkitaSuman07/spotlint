import ast

from .base import Rule, RuleMetadata
from .helpers import is_agent_or_tool_call

from ..model.context import AnalysisContext
from ..model.finding import Finding, SourceLocation


class Flow001(Rule):

    metadata = RuleMetadata(
        rule_id="FLOW001",
        name="Unbounded Agent Execution",
        severity="HIGH",
        description=(
            "Detects unconditional loops containing "
            "agent or tool execution."
        ),
    )

    def analyze(self, tree, context):

        findings = []

        for node in ast.walk(tree):

            if not isinstance(node, ast.While):
                continue

            if not (
                isinstance(node.test, ast.Constant)
                and node.test.value is True
            ):
                continue

            contains_agent = any(
                isinstance(child, ast.Call)
                and is_agent_or_tool_call(child)
                for child in ast.walk(node)
            )

            if not contains_agent:
                continue

            findings.append(
                Finding(
                    rule_id="FLOW001",
                    severity="HIGH",
                    message=(
                        "Unbounded agent/tool execution loop detected"
                    ),
                    location=SourceLocation(
                        context.source.path,
                        node.lineno,
                        node.col_offset + 1,
                    ),
                    evidence=context.snippet(node),
                    explanation=(
                        "An unconditional loop contains agent or "
                        "tool execution and has no statically "
                        "visible iteration bound."
                    ),
                    remediation=(
                        "Add an iteration limit, depth limit, "
                        "timeout, cancellation condition, "
                        "or explicit termination policy."
                    ),
                )
            )

        return findings