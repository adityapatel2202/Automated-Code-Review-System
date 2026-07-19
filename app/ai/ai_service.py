"""
ai_service.py - AI Service Facade
====================================
Entry-point used by AnalysisManager to obtain AI-improved code.

The heavy CodeImprover (and its underlying CodeT5 model) is lazy-loaded
on first call so that application startup remains fast.  If the model
or its dependencies are unavailable the service falls back to returning
the original code with an explanatory note.
"""


class AIService:
    """
    Public interface consumed by the rest of the application.

    Usage (unchanged from Phase 1):
        ai = AIService()
        result = ai.improve_code(source_code)
        # result -> {clean_code, best_practice, optimized_code, changes}
    """

    def __init__(self):
        # Lazy-loaded on first improve_code() call
        self._improver = None
        self._load_attempted = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def improve_code(self, source_code, issues=None):
        """
        Generate AI-improved versions of the supplied source code.

        Args:
            source_code: Raw Python source string.
            issues:      Optional list of detected issues (dicts with
                         ``'message'`` key) from static analysis.

        Returns:
            dict with keys:
                clean_code     – cleaned / formatted variant
                best_practice  – best-practice variant
                optimized_code – performance-optimized variant
                changes        – list[str] describing what changed
        """
        # Lazy-load the CodeImprover (and its model) on first use
        self._ensure_improver_loaded()

        if self._improver is not None:
            try:
                return self._improver.improve(source_code, issues=issues)
            except Exception as e:
                print(f"[AIService] CodeImprover failed: {e}")
                return self._fallback_result(source_code)
        else:
            return self._fallback_result(source_code)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_improver_loaded(self):
        """Attempt to import and instantiate CodeImprover exactly once."""
        if self._load_attempted:
            return

        self._load_attempted = True
        try:
            from app.ai.code_improver import CodeImprover

            self._improver = CodeImprover()
            print("[AIService] CodeImprover loaded successfully.")
        except Exception as e:
            print(f"[AIService] Could not load CodeImprover: {e}")
            self._improver = None

    @staticmethod
    def _fallback_result(source_code):
        """
        Return a graceful fallback when the AI model is unavailable.
        """
        return {
            "clean_code": source_code,
            "best_practice": source_code,
            "optimized_code": source_code,
            "changes": [
                "AI model not available – original code returned",
                "Install transformers and torch to enable AI improvements",
                "Run: pip install transformers torch",
            ],
        }