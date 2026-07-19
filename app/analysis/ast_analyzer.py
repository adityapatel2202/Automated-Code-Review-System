import ast


class ASTAnalyzer:

    def analyze(self, file_path):

        with open(file_path, "r", encoding="utf-8") as file:
            source = file.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return {
                 "functions": 0,
                 "classes": 0,
                 "imports": 0,
                 "loops": 0,
                 "variables": 0,
                 "if_statements": 0,
                 "try_blocks": 0,
                 "returns": 0,
                 "function_calls": 0,
                 "comments": 0,
                 "syntax_error": True
            }

        result = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "loops": 0,
            "variables": 0,
            "if_statements": 0,
            "try_blocks": 0,
            "returns": 0,
            "function_calls": 0,
            "comments": 0,
            "syntax_error": False
        }

        # Count comments
        for line in source.splitlines():
            if line.strip().startswith("#"):
                result["comments"] += 1

        # Walk through AST
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

            elif isinstance(node, ast.If):
                result["if_statements"] += 1

            elif isinstance(node, ast.Try):
                result["try_blocks"] += 1

            elif isinstance(node, ast.Return):
                result["returns"] += 1

            elif isinstance(node, ast.Call):
                result["function_calls"] += 1

        return result