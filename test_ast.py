from app.analysis.ast_analyzer import ASTAnalyzer

analyzer = ASTAnalyzer()

result = analyzer.analyze("uploads/week3_1.py")

print(result)
