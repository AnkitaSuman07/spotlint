class TextReporter:

    def render(self, findings):

        if not findings:
            return "Flowmark: no findings."

        output = []

        for finding in findings:

            output.append(
                f"{finding.rule_id} "
                f"{finding.severity}"
            )

            output.append(
                f"  {finding.location.file}:"
                f"{finding.location.line}:"
                f"{finding.location.column}"
            )

            output.append(
                f"  {finding.message}"
            )

            output.append(
                f"  Evidence: {finding.evidence}"
            )

            output.append(
                f"  Why: {finding.explanation}"
            )

            output.append(
                f"  Fix: {finding.remediation}"
            )

            output.append("")

        return "\n".join(output)