import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceFile:
    path: str
    text: str
    tree: ast.AST


@dataclass
class AnalysisContext:
    source: SourceFile

    def snippet(self, node: ast.AST) -> str:
        lines = self.source.text.splitlines()
        line = getattr(node, "lineno", 1)

        if 1 <= line <= len(lines):
            return lines[line - 1].strip()

        return ""