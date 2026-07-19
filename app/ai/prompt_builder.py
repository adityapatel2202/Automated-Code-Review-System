class PromptBuilder:

    def build(self, source_code, issues):

        prompt = (
            "Improve the following Python code.\n\n"
            "Detected Issues:\n"
        )

        for issue in issues:
            prompt += f"- {issue['message']}\n"

        prompt += "\nCode:\n"
        prompt += source_code

        return prompt