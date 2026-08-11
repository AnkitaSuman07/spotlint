import json


class SarifReporter:

    def render(self, findings):

        results = []

        for finding in findings:

            results.append(
                {
                    "ruleId": finding.rule_id,
                    "level": (
                        "error"
                        if finding.severity
                        in {"HIGH", "CRITICAL"}
                        else "warning"
                    ),
                    "message": {
                        "text": finding.message
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri":
                                        finding.location.file
                                },
                                "region": {
                                    "startLine":
                                        finding.location.line,
                                    "startColumn":
                                        finding.location.column,
                                },
                            }
                        }
                    ],
                }
            )

        return json.dumps(
            {
                "$schema":
                    "https://json.schemastore.org/sarif-2.1.0.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {
                                "name": "spotlint",
                                "version": "0.1.0",
                            }
                        },
                        "results": results,
                    }
                ],
            },
            indent=2,
        )