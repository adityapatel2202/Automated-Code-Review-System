import json
import subprocess


class PylintAnalyzer:

    def analyze(self, file_path):

        command = [
            "pylint",
            file_path,
            "--output-format=json",
            "--score=y"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        output = result.stdout.strip()

        if not output:
            return {
                "issues": [],
                "issue_count": 0
            }

        try:
            issues = json.loads(output)
        except json.JSONDecodeError:
            return {
                "issues": [],
                "issue_count": 0
            }

        return {
            "issues": issues,
            "issue_count": len(issues)
        }