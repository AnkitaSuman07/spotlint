import argparse
from pathlib import Path
import sys

from .analysis.engine import AnalysisEngine
from .config import AnalyzerConfig
from .reporters.text import TextReporter
from .reporters.json import JsonReporter
from .reporters.sarif import SarifReporter
from .rules.registry import default_registry


SEVERITY = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def build_parser():

    parser = argparse.ArgumentParser(
        prog="spotlint"
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    check = sub.add_parser(
        "check"
    )

    check.add_argument(
        "path",
        type=Path
    )

    check.add_argument(
        "--format",
        choices=[
            "text",
            "json",
            "sarif",
        ],
        default="text",
    )

    check.add_argument(
        "--output",
        type=Path
    )

    check.add_argument(
        "--rule"
    )

    check.add_argument(
        "--severity",
        choices=[
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        ],
        default="LOW",
    )

    return parser


def main(argv=None):

    parser = build_parser()

    args = parser.parse_args(argv)

    try:

        rule_ids = None

        if args.rule:
            rule_ids = {
                rule.strip()
                for rule in args.rule.split(",")
            }

        config = AnalyzerConfig(
            minimum_severity=args.severity,
            rule_ids=rule_ids,
        )

        engine = AnalysisEngine(
            default_registry(),
            config,
        )

        findings = engine.analyze_path(
            args.path
        )

        if args.format == "json":

            output = JsonReporter().render(
                findings
            )

        elif args.format == "sarif":

            output = SarifReporter().render(
                findings
            )

        else:

            output = TextReporter().render(
                findings
            )

        if args.output:

            args.output.write_text(
                output,
                encoding="utf-8"
            )

        else:

            print(output)

        threshold = SEVERITY[
            args.severity
        ]

        return int(
            any(
                SEVERITY[f.severity] >= threshold
                for f in findings
            )
        )

    except (OSError, ValueError) as exc:

        print(
            f"spotlint: error: {exc}",
            file=sys.stderr
        )

        return 2