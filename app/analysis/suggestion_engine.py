class SuggestionEngine:

    def generate(self, issues):

        suggestions = []

        rules = {
            "missing-module-docstring":
                "Add a module docstring describing the purpose of the file.",

            "missing-class-docstring":
                "Add a class docstring explaining the class.",

            "missing-function-docstring":
                "Add a docstring to explain what the function does.",

            "trailing-whitespace":
                "Remove trailing whitespace for cleaner formatting.",

            "redefined-outer-name":
                "Rename the variable to avoid redefining an existing name."
        }

        for issue in issues:

            symbol = issue.get("symbol")

            if symbol in rules:
                suggestions.append(rules[symbol])

        # Remove duplicate suggestions
        suggestions = list(dict.fromkeys(suggestions))

        return suggestions