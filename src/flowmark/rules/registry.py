from .base import Rule

from .flow001 import Flow001
from .flow002 import Flow002
from .flow003 import Flow003
from .flow004 import Flow004
from .flow005 import Flow005


class RuleRegistry:

    def __init__(self, rules: list[Rule]):
        self.rules = {
            rule.metadata.rule_id: rule
            for rule in rules
        }

    def select(self, rule_ids=None):

        if not rule_ids:
            return list(self.rules.values())

        unknown = rule_ids - self.rules.keys()

        if unknown:
            raise ValueError(
                f"Unknown rule(s): {', '.join(sorted(unknown))}"
            )

        return [
            self.rules[rule_id]
            for rule_id in sorted(rule_ids)
        ]


def default_registry():

    return RuleRegistry(
        [
            Flow001(),
            Flow002(),
            Flow003(),
            Flow004(),
            Flow005(),
        ]
    )