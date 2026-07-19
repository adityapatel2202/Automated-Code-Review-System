from semantic_analyzer import SemanticAnalyzer

analyzer = SemanticAnalyzer()

code = """
def add(a, b):
    return a + b
"""

result = analyzer.analyze(code)

print(result)