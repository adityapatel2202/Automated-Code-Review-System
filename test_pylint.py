from app.analysis.pylint_analyzer import PylintAnalyzer

analyzer = PylintAnalyzer()

result = analyzer.analyze("uploads/week3_1.py")

print(result)   