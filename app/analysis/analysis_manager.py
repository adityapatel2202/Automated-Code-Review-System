from .code_reader import CodeReader
from .suggestion_engine import SuggestionEngine
from .ast_analyzer import ASTAnalyzer
from .pylint_analyzer import PylintAnalyzer
from .score_calculator import ScoreCalculator
from app.ai.ai_service import AIService
from app.semantic.semantic_analyzer import SemanticAnalyzer
from app.ml.predictor import QualityPredictor


class AnalysisManager:

    def __init__(self):
        self.ast = ASTAnalyzer()
        self.pylint = PylintAnalyzer()
        self.suggestion = SuggestionEngine()
        self.score = ScoreCalculator()
        self.reader = CodeReader()
        self.ai = AIService()
        self.semantic = SemanticAnalyzer()
        self.predictor = QualityPredictor()

    def analyze(self, file_path):

        # Read uploaded source code
        source_code = self.reader.read(file_path)

        # AI Code Generation
        ai_result = self.ai.improve_code(source_code)

        # Semantic Analysis (CodeBERT)
        semantic_result = self.semantic.analyze(source_code)

        # AST Analysis
        ast_result = self.ast.analyze(file_path)

        # Pylint Analysis
        pylint_result = self.pylint.analyze(file_path)

        # Suggestions
        suggestions = self.suggestion.generate(
            pylint_result["issues"]
        )

        # Quality Score
        quality_score = self.score.calculate(
            ast_result,
            pylint_result
        )

        # ML Prediction
        try:
            ml_prediction = self.predictor.predict(file_path)
        except Exception as e:
            print(f"[AnalysisManager] ML Prediction failed: {e}")
            ml_prediction = {
                "quality_label": "Unknown",
                "prediction": "Unknown",
                "confidence": 0.0,
                "error": str(e)
            }

        print("\n===== Semantic Analysis =====")
        print(semantic_result)
        print("=============================\n")

        return {
            "ast_analysis": ast_result,
            "issues_found": pylint_result["issues"],
            "issue_count": pylint_result["issue_count"],
            "suggestions": suggestions,
            "quality_score": quality_score,
            "source_code": source_code,
            "ai_result": ai_result,
            "semantic_analysis": semantic_result,
            "ml_prediction": ml_prediction,
        }


