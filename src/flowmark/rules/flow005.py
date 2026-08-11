import ast

from .base import Rule, RuleMetadata
from .helpers import is_agent_call, has_keyword

from ..model.context import AnalysisContext
from ..model.finding import Finding, SourceLocation


BOUNDARY_ARGUMENTS = {
    "timeout",
    "max_iterations",
    "max_steps",
    "max_depth",
    "deadline",
}


class Flow005(Rule):

    metadata = RuleMetadata(
        rule_id="FLOW005",
        name="Missing Execution Boundary",
        severity="MEDIUM",
        description="Detects agent execution without explicit boundary controls.",
    )

    def analyze(self, tree, context):

        findings = []

        for node in ast.walk(tree):

            if not isinstance(node, ast.Call):
                continue

            if not is_agent_call(node):
                continue

            bounded = any(
                has_keyword(node, argument)
                for argument in BOUNDARY_ARGUMENTS
            )

            if bounded:
                continue

            findings.append(
                Finding(
                    rule_id="FLOW005",
                    severity="MEDIUM",
                    message="Agent execution has no explicit execution boundary",
                    location=SourceLocation(
                        context.source.path,
                        node.lineno,
                        node.col_offset + 1,
                    ),
                    evidence=context.snippet(node),
                    explanation=(
                        "The agent invocation does not expose a visible "
                        "timeout, iteration, step, or depth boundary."
                    ),
                    remediation=(
                        "Configure an explicit timeout, max iterations, "
                        "max steps, max depth, or equivalent execution budget."
                    ),
                )
            )

        return findings