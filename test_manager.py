from app.analysis.analysis_manager import AnalysisManager

manager = AnalysisManager()

result = manager.analyze("uploads/week3_1.py")

print("\nAST Analysis")
print(result["ast_analysis"])

print("\nIssues Found")
for issue in result["issues_found"]:
    print("-", issue["message"])

print("\nSuggestions")
for suggestion in result["suggestions"]:
    print("-", suggestion)