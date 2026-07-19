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
            return self.empty_result()

        try:
            issues = json.loads(output)
        except json.JSONDecodeError:
            return self.empty_result()

        error_count = 0
        warning_count = 0
        convention_count = 0
        refactor_count = 0
        fatal_count = 0

        for issue in issues:

            issue_type = issue.get("type", "").lower()

            if issue_type == "error":
                error_count += 1

            elif issue_type == "warning":
                warning_count += 1

            elif issue_type == "convention":
                convention_count += 1

            elif issue_type == "refactor":
                refactor_count += 1

            elif issue_type == "fatal":
                fatal_count += 1

        return {
            "issues": issues,
            "issue_count": len(issues),
            "error_count": error_count,
            "warning_count": warning_count,
            "convention_count": convention_count,
            "refactor_count": refactor_count,
            "fatal_count": fatal_count
        }

    @staticmethod
    def empty_result():
        return {
            "issues": [],
            "issue_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "convention_count": 0,
            "refactor_count": 0,
            "fatal_count": 0
        }