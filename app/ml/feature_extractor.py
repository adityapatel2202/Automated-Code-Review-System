"""
ML Feature Extractor for the Automated Code Review System.

Orchestrates the AST, Pylint, and Semantic analyzers to produce a
feature dictionary that matches the exact schema used during model training.
"""

import os
import sys

# Add the project root to sys.path so we can import app modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.analysis.ast_analyzer import ASTAnalyzer
from app.analysis.pylint_analyzer import PylintAnalyzer
from app.semantic.semantic_analyzer import SemanticAnalyzer


class MLFeatureExtractor:
    """
    Extracts ML-ready features from a Python source file.

    Combines outputs from the AST, Pylint, and Semantic analyzers into
    a single feature dictionary whose keys match the training dataset
    columns (excluding metadata and target columns).
    """

    def __init__(self):
        """Initialise all three sub-analyzers."""
        self.ast_analyzer = ASTAnalyzer()
        self.pylint_analyzer = PylintAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()

    def extract(self, file_path):
        """
        Run all analyzers on *file_path* and return a unified feature dict.

        The returned dict contains exactly the features used during training:
            functions, classes, imports, loops, variables, if_statements,
            returns, function_calls, comments, syntax_error,
            issue_count, error_count, warning_count, convention_count,
            refactor_count, fatal_count,
            embedding_dimension, token_count, semantic_score, confidence,
            readability

        Args:
            file_path (str): Absolute path to the Python file to analyse.

        Returns:
            dict: Feature dictionary matching the training schema.
        """
        # ------------------------------------------------------------------
        # 1. AST features
        # ------------------------------------------------------------------
        ast_result = self.ast_analyzer.analyze(file_path)

        # ------------------------------------------------------------------
        # 2. Pylint features
        # ------------------------------------------------------------------
        pylint_result = self.pylint_analyzer.analyze(file_path)

        # ------------------------------------------------------------------
        # 3. Semantic features (requires the raw source code)
        # ------------------------------------------------------------------
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        semantic_result = self.semantic_analyzer.analyze(code)

        # ------------------------------------------------------------------
        # 4. Build the unified feature dictionary
        # ------------------------------------------------------------------
        features = {
            # AST features (excluding try_blocks which is not in training CSV)
            "functions": ast_result.get("functions", 0),
            "classes": ast_result.get("classes", 0),
            "imports": ast_result.get("imports", 0),
            "loops": ast_result.get("loops", 0),
            "variables": ast_result.get("variables", 0),
            "if_statements": ast_result.get("if_statements", 0),
            "returns": ast_result.get("returns", 0),
            "function_calls": ast_result.get("function_calls", 0),
            "comments": ast_result.get("comments", 0),
            "syntax_error": ast_result.get("syntax_error", False),

            # Pylint features (excluding the raw issues list)
            "issue_count": pylint_result.get("issue_count", 0),
            "error_count": pylint_result.get("error_count", 0),
            "warning_count": pylint_result.get("warning_count", 0),
            "convention_count": pylint_result.get("convention_count", 0),
            "refactor_count": pylint_result.get("refactor_count", 0),
            "fatal_count": pylint_result.get("fatal_count", 0),

            # Semantic features
            "embedding_dimension": semantic_result.get("embedding_dimension", 768),
            "token_count": semantic_result.get("token_count", 0),
            "semantic_score": semantic_result.get("semantic_score", 0.0),
            "confidence": semantic_result.get("confidence", 0.0),
            "readability": semantic_result.get("readability", "Average"),
        }

        return features


if __name__ == "__main__":
    # Quick smoke test with a sample file
    if len(sys.argv) < 2:
        print("Usage: python -m app.ml.feature_extractor <path_to_python_file>")
        sys.exit(1)

    extractor = MLFeatureExtractor()
    result = extractor.extract(sys.argv[1])
    print("\nExtracted Features:")
    for key, value in result.items():
        print(f"  {key:25s}: {value}")
