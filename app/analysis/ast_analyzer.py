import ast


class ASTAnalyzer:

    def analyze(self, file_path):

        with open(file_path, "r", encoding="utf-8") as file:
            source_code = file.read()

        tree = ast.parse(source_code)

        result = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "loops": 0,
            "variables": 0,
            "syntax_error": False
        }

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):
                result["functions"] += 1

            elif isinstance(node, ast.ClassDef):
                result["classes"] += 1

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                result["imports"] += 1

            elif isinstance(node, (ast.For, ast.While)):
                result["loops"] += 1

            elif isinstance(node, ast.Assign):
                result["variables"] += len(node.targets)

        return result