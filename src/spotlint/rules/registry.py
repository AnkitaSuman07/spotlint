from .base import Rule

from .sp001 import sp001
from .sp002 import sp002
from .sp003 import sp003
from .sp005 import sp004
from .sp004 import sp005


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
            sp001(),
            sp002(),
            sp003(),
            sp004(),
            sp005(),
        ]
    )