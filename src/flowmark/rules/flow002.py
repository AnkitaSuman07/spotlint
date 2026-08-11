import ast

from .base import Rule, RuleMetadata
from .helpers import is_tool_call, inside_try_except

from ..model.context import AnalysisContext
from ..model.finding import Finding, SourceLocation


class Flow002(Rule):

    metadata = RuleMetadata(
        rule_id="FLOW002",
        name="Uncontrolled Tool Invocation",
        severity="HIGH",
        description="Detects tool calls without a local failure boundary.",
    )

    def analyze(self, tree, context):

        findings = []

        for node in ast.walk(tree):

            if not isinstance(node, ast.Call):
                continue

            if not is_tool_call(node):
                continue

            if inside_try_except(tree, node):
                continue

            findings.append(
                Finding(
                    rule_id="FLOW002",
                    severity="HIGH",
                    message="Tool invocation has no visible error boundary",
                    location=SourceLocation(
                        context.source.path,
                        node.lineno,
                        node.col_offset + 1,
                    ),
                    evidence=context.snippet(node),
                    explanation=(
                        "A tool invocation can fail without a visible "
                        "exception handling boundary."
                    ),
                    remediation=(
                        "Handle tool failures explicitly or establish "
                        "a controlled higher-level failure boundary."
                    ),
                )
            )

        return findings