import os
import csv

from app.ml.dataset_loader import DatasetLoader
from app.analysis.ast_analyzer import ASTAnalyzer
from app.analysis.pylint_analyzer import PylintAnalyzer
from app.semantic.semantic_analyzer import SemanticAnalyzer


class DatasetBuilder:

    def __init__(self):

        self.loader = DatasetLoader()

        self.ast = ASTAnalyzer()

        self.pylint = PylintAnalyzer()

        self.semantic = SemanticAnalyzer()

        self.temp_folder = "app/ml/temp"

        os.makedirs(self.temp_folder, exist_ok=True)

    def calculate_quality_score(self, ast_result, pylint_result, semantic_result):

        score = 100

        # Pylint penalties
        score -= pylint_result["error_count"] * 10
        score -= pylint_result["warning_count"] * 4
        score -= pylint_result["convention_count"] * 1
        score -= pylint_result["refactor_count"] * 2
        score -= pylint_result["fatal_count"] * 15

        # AST penalty
        if ast_result["syntax_error"]:
            score -= 30

        # Semantic contribution
        score += (semantic_result["semantic_score"] - 50) * 0.2

        score = max(0, min(100, score))

        return round(score, 1)

    def get_quality_label(self, score):

        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Average"
        else:
            return "Poor"

    def build(self, sample_size=100):

        dataset = self.loader.load_train_dataset()

        feature_rows = []

        processed = 0
        skipped = 0

        for index, item in enumerate(dataset.select(range(sample_size))):

            try:

                print(f"Processing {index + 1}/{sample_size}")

                code = item["func_code_string"]

                temp_file = os.path.join(
                    self.temp_folder,
                    "temp_code.py"
                )

                with open(temp_file, "w", encoding="utf-8") as file:
                    file.write(code)

                # AST Analysis
                ast_result = self.ast.analyze(temp_file)

                # Skip invalid Python code
                if ast_result["syntax_error"]:
                    print(f"Skipped sample {index + 1} (Syntax Error)")
                    skipped += 1
                    continue

                # Pylint Analysis
                pylint_result = self.pylint.analyze(temp_file)

                # Semantic Analysis
                semantic_result = self.semantic.analyze(code)

                # Quality Score
                quality_score = self.calculate_quality_score(
                    ast_result,
                    pylint_result,
                    semantic_result
                )

                quality_label = self.get_quality_label(
                    quality_score
                )

                row = {

                    "repository": item["repository_name"],

                    "function_name": item["func_name"],

                    # AST Features
                    "functions": ast_result["functions"],
                    "classes": ast_result["classes"],
                    "imports": ast_result["imports"],
                    "loops": ast_result["loops"],
                    "variables": ast_result["variables"],
                    "if_statements": ast_result["if_statements"],
                    "returns": ast_result["returns"],
                    "function_calls": ast_result["function_calls"],
                    "comments": ast_result["comments"],
                    "syntax_error": ast_result["syntax_error"],

                    # Pylint Features
                    "issue_count": pylint_result["issue_count"],
                    "error_count": pylint_result["error_count"],
                    "warning_count": pylint_result["warning_count"],
                    "convention_count": pylint_result["convention_count"],
                    "refactor_count": pylint_result["refactor_count"],
                    "fatal_count": pylint_result["fatal_count"],

                    # CodeBERT Features
                    "embedding_dimension": semantic_result["embedding_dimension"],
                    "token_count": semantic_result["token_count"],
                    "semantic_score": semantic_result["semantic_score"],
                    "confidence": semantic_result["confidence"],
                    "readability": semantic_result["readability"],

                    # Target
                    "quality_score": quality_score,
                    "quality_label": quality_label
                }

                feature_rows.append(row)
                processed += 1

            except Exception as e:

                print(f"Skipped sample {index + 1}: {e}")
                skipped += 1
                continue

        if not feature_rows:
            print("No valid samples were processed.")
            return

        output_file = "app/ml/dataset/features/features.csv"

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=feature_rows[0].keys()
            )

            writer.writeheader()

            writer.writerows(feature_rows)

        print()
        print("===================================")
        print("Dataset created successfully!")
        print(f"Processed Samples : {processed}")
        print(f"Skipped Samples   : {skipped}")
        print(f"Total Saved       : {len(feature_rows)}")
        print(f"Saved to          : {output_file}")
        print("===================================")