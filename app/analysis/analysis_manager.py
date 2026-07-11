from app.analysis.code_reader import CodeReader

from .suggestion_engine import SuggestionEngine
from .ast_analyzer import ASTAnalyzer
from .pylint_analyzer import PylintAnalyzer
from .score_calculator import ScoreCalculator


class AnalysisManager:

    def __init__(self):

        self.ast = ASTAnalyzer()
        self.pylint = PylintAnalyzer()
        self.suggestion = SuggestionEngine()
        self.score = ScoreCalculator()
        self.reader = CodeReader()

    def analyze(self, file_path):

        ast_result = self.ast.analyze(file_path)

        pylint_result = self.pylint.analyze(file_path)
        suggestions = self.suggestion.generate(
            pylint_result["issues"]
        )
        quality_score = self.score.calculate(
            ast_result,
            pylint_result
        )
        result = {
            "ast_analysis": ast_result,
            "issues_found": pylint_result["issues"],
            "issue_count": pylint_result["issue_count"],
            "suggestions": suggestions,
            "quality_score": quality_score,
           
        }

        return result