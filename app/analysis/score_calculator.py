class ScoreCalculator:

    def calculate(self, ast_result, pylint_result):

        score = 100

        # Deduct points for pylint issues
        issue_count = pylint_result["issue_count"]
        score -= issue_count * 2

        # Syntax error is severe
        if ast_result["syntax_error"]:
            score -= 30

        # Too many functions
        if ast_result["functions"] > 15:
            score -= 5

        # Too many loops
        if ast_result["loops"] > 10:
            score -= 5

        # Too many if statements
        if ast_result["if_statements"] > 15:
            score -= 5

        # Keep score between 0 and 100
        score = max(0, min(score, 100))

        return score