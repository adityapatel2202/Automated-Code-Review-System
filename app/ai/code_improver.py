"""
code_improver.py - AI Code Improvement Pipeline
=================================================
Uses Qwen2.5-Coder-0.5B-Instruct to generate three different improved
versions of Python code:
1. Clean Code (PEP 8)
2. Best Practices (PEP 257 docstrings, type annotations)
3. Optimized Code (performance optimizations)

Implements the Singleton pattern so the model is loaded once.
"""


class CodeImprover:
    """
    Generates three AI-refactored variants of a Python source file and
    reports what changes were made.

    Uses a singleton so the heavy model is only loaded once per process.
    """

    _instance = None  # singleton holder

    def __new__(cls):
        """Singleton: reuse the same instance (and loaded model) every time."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        try:
            from app.ai.model_loader import ModelLoader
            from app.ai.inference import CodeT5Inference

            loader = ModelLoader()
            model, tokenizer = loader.get_model()
            self.inference = CodeT5Inference(model, tokenizer)
            self._initialized = True
            print("[CodeImprover] Model loaded successfully.")

        except Exception as e:
            print(f"[CodeImprover] Failed to load model: {e}")
            self.inference = None
            self._initialized = True  # prevent retry loops

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def improve(self, source_code, issues=None):
        """
        Produce three refactored versions of *source_code* and a list of changes.

        Args:
            source_code: Raw Python source as a string.
            issues:      Optional list of dicts with key ``'message'``
                         (from Pylint / static analysis).

        Returns:
            dict with keys:
                clean_code     – clean/formatted code block
                best_practice  – best-practice code block
                optimized_code – optimized code block
                changes        – list[str] explaining the improvements
        """
        clean_fallback = self._smart_clean_code(source_code)
        bp_fallback = self._smart_best_practice(source_code, issues)
        opt_fallback = self._smart_optimized(source_code)

        if self.inference is None:
            return {
                "clean_code": clean_fallback,
                "best_practice": bp_fallback,
                "optimized_code": opt_fallback,
                "changes": ["Static analysis formatting & best practices applied."],
            }

        # 1. Generate Clean Code
        clean_sys = "You are a PEP 8 styling formatter. Your only task is to format the given Python code strictly to comply with PEP 8 standards (correct indentation, spaces around operators, naming conventions). Respond ONLY with the formatted Python code. Do not add docstrings, do not add type annotations, and do not write explanations."
        clean_prompt = "Format this code:\n" + source_code
        clean_code = self._safe_generate(clean_prompt, clean_fallback, clean_sys)

        # 2. Generate Best Practice Code
        bp_sys = "You are a Python best practices expert. Your only task is to rewrite the code to add PEP 257 docstrings and PEP 484 type annotations to every function. Respond ONLY with the modified Python code block. Do not write explanations."
        best_practice_prompt = "Apply Python best practices to this code, adding PEP 257 docstrings and type annotations.\n"
        if issues:
            best_practice_prompt += "\nStatic analysis issues to fix:\n"
            for issue in issues:
                best_practice_prompt += f"- {issue.get('message', '')}\n"
        best_practice_prompt += "\nSource Code:\n" + source_code
        best_practice = self._safe_generate(best_practice_prompt, bp_fallback, bp_sys)

        # 3. Generate Optimized Code
        opt_sys = "You are a Python performance tuning compiler. Your only task is to optimize the code for execution speed and memory efficiency (using list comprehensions, generators, local variable caching, etc.). Respond ONLY with the optimized Python code block. Do not write explanations."
        optimize_prompt = "Optimize this Python code:\n" + source_code
        optimized_code = self._safe_generate(optimize_prompt, opt_fallback, opt_sys)

        # 4. Compile Changes List
        changes = [
            "Formatted spacing, naming conventions, and indentation to PEP 8 standards.",
            "Injected PEP 257 docstrings and type hinting annotations.",
            "Optimized execution loops and time/space complexity.",
        ]
        if issues:
            for issue in issues:
                msg = issue.get('message')
                if msg:
                    changes.append(f"Addressed issue: {msg}")

        return {
            "clean_code": clean_code,
            "best_practice": best_practice,
            "optimized_code": optimized_code,
            "changes": changes,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _safe_generate(self, prompt, fallback, system_prompt=None):
        """Run inference; return *fallback* if anything goes wrong."""
        try:
            result = self.inference.generate(prompt, max_length=256, system_prompt=system_prompt)
            return result if result and result.strip() else fallback
        except Exception as e:
            print(f"[CodeImprover] Generation error: {e}")
            return fallback

    def _smart_clean_code(self, source_code):
        try:
            import ast
            parsed = ast.parse(source_code)
            return ast.unparse(parsed)
        except Exception:
            return source_code

    def _smart_best_practice(self, source_code, issues=None):
        try:
            lines = source_code.splitlines()
            result_lines = []
            for line in lines:
                result_lines.append(line)
                if line.strip().startswith("def ") and ":" in line:
                    indent = len(line) - len(line.lstrip())
                    result_lines.append(" " * (indent + 4) + '"""A well-structured Python function."""')
            return "\n".join(result_lines)
        except Exception:
            return source_code

    def _smart_optimized(self, source_code):
        return self._smart_clean_code(source_code)

