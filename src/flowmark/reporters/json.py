import json


class JsonReporter:

    def render(self, findings):

        return json.dumps(
            {
                "version": "0.1",
                "findings": [
                    finding.to_dict()
                    for finding in findings
                ],
            },
            indent=2,
        )