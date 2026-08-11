from abc import ABC, abstractmethod
from dataclasses import dataclass
import ast

from ..model.context import AnalysisContext
from ..model.finding import Finding


@dataclass(frozen=True)
class RuleMetadata:
    rule_id: str
    name: str
    severity: str
    description: str


class Rule(ABC):

    metadata: RuleMetadata

    @abstractmethod
    def analyze(
        self,
        tree: ast.AST,
        context: AnalysisContext
    ) -> list[Finding]:
        pass