import ast

from .base import Rule, RuleMetadata
from .helpers import call_name

from ..model.context import AnalysisContext
from ..model.finding import Finding, SourceLocation


AGENT_METHODS = {
    "agent.run",
    "agent.invoke",
    "agent.arun",
    "agent.ainvoke",
}


class sp004(Rule):

    metadata = RuleMetadata(
        rule_id="sp004",
        name="Agent Recursion",
        severity="HIGH",
        description="Detects agent execution from within agent execution functions.",
    )

    def analyze(self, tree, context):

        findings = []

        for function in ast.walk(tree):

            if not isinstance(
                function,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue

            calls = [
                node
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
            ]

            agent_calls = [
                node
                for node in calls
                if call_name(node).lower()
                in {x.lower() for x in AGENT_METHODS}
            ]

            if len(agent_calls) < 2:
                continue

            for node in agent_calls[1:]:

                findings.append(
                    Finding(
                        rule_id="sp004",
                        severity="HIGH",
                        message="Multiple agent invocations detected in one execution path",
                        location=SourceLocation(
                            context.source.path,
                            node.lineno,
                            node.col_offset + 1,
                        ),
                        evidence=context.snippet(node),
                        explanation=(
                            "Multiple agent invocations in the same "
                            "function can create recursive or cascading "
                            "execution paths."
                        ),
                        remediation=(
                            "Add explicit depth/iteration limits and "
                            "document the permitted agent-to-agent "
                            "execution boundary."
                        ),
                    )
                )

        return findings