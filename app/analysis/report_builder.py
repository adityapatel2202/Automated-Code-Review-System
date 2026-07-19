"""
ReportBuilder: Generates standalone HTML reports from analysis results.
"""

from datetime import datetime


class ReportBuilder:
    """Builds standalone HTML report documents from analysis results."""

    def build_html_report(self, result, filename):
        """
        Generate a standalone HTML string report from the analysis result.

        Args:
            result: dict containing analysis results
            filename: name of the analyzed file

        Returns:
            str: Complete HTML document string
        """
        quality_score = result.get("quality_score", 0)
        issue_count = result.get("issue_count", 0)
        issues = result.get("issues_found", [])
        suggestions = result.get("suggestions", [])
        ast = result.get("ast_analysis", {})
        semantic = result.get("semantic_analysis", {})
        source_code = result.get("source_code", "")
        ml_prediction = result.get("ml_prediction")
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Determine quality label
        if quality_score >= 85:
            quality_label = "EXCELLENT"
            label_color = "#198754"
        elif quality_score >= 70:
            quality_label = "GOOD"
            label_color = "#0d6efd"
        elif quality_score >= 50:
            quality_label = "AVERAGE"
            label_color = "#ffc107"
        else:
            quality_label = "POOR"
            label_color = "#dc3545"

        # Build issues HTML
        issues_html = ""
        if issues:
            issues_rows = ""
            for i, issue in enumerate(issues, 1):
                issue_type = issue.get("type", "info")
                badge_color = {
                    "error": "#dc3545",
                    "warning": "#ffc107",
                }.get(issue_type, "#0dcaf0")
                text_color = "#000" if issue_type == "warning" else "#fff"
                issues_rows += f"""
                <tr>
                    <td>{i}</td>
                    <td><span style="background:{badge_color};color:{text_color};
                        padding:2px 8px;border-radius:4px;font-size:12px;">
                        {issue_type.title()}</span></td>
                    <td>{issue.get('message', '')}</td>
                    <td>{issue.get('line', '')}</td>
                </tr>"""
            issues_html = f"""
            <table style="width:100%;border-collapse:collapse;margin-top:10px;">
                <thead>
                    <tr style="background:#f8f9fa;border-bottom:2px solid #dee2e6;">
                        <th style="padding:10px;text-align:left;">#</th>
                        <th style="padding:10px;text-align:left;">Type</th>
                        <th style="padding:10px;text-align:left;">Message</th>
                        <th style="padding:10px;text-align:left;">Line</th>
                    </tr>
                </thead>
                <tbody>{issues_rows}</tbody>
            </table>"""
        else:
            issues_html = '<p style="color:#198754;font-weight:bold;">🎉 No issues found. Excellent code quality!</p>'

        # Build suggestions HTML
        suggestions_html = ""
        for suggestion in suggestions:
            suggestions_html += f"""
            <div style="padding:10px;border-left:4px solid #198754;
                background:#f8fff8;margin-bottom:8px;border-radius:4px;">
                ✅ {suggestion}
            </div>"""

        # Build AST HTML
        ast_rows = ""
        ast_metrics = [
            ("Functions", ast.get("functions", 0)),
            ("Classes", ast.get("classes", 0)),
            ("Variables", ast.get("variables", 0)),
            ("Imports", ast.get("imports", 0)),
            ("Loops", ast.get("loops", 0)),
            ("If Statements", ast.get("if_statements", 0)),
            ("Try Blocks", ast.get("try_blocks", 0)),
            ("Returns", ast.get("returns", 0)),
            ("Function Calls", ast.get("function_calls", 0)),
            ("Comments", ast.get("comments", 0)),
        ]
        for metric_name, metric_value in ast_metrics:
            ast_rows += f"""
            <tr style="border-bottom:1px solid #dee2e6;">
                <td style="padding:8px;">{metric_name}</td>
                <td style="padding:8px;">{metric_value}</td>
            </tr>"""

        # Build ML prediction HTML
        ml_html = ""
        if ml_prediction:
            ml_conf = ml_prediction.get("confidence", 0)
            ml_label = ml_prediction.get("prediction", "Unknown")
            ml_html = f"""
            <div style="background:#fff;border-radius:10px;padding:20px;
                margin-top:20px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                <h3 style="color:#6f42c1;">🤖 ML Predicted Quality</h3>
                <p style="font-size:24px;font-weight:bold;">{ml_label}</p>
                <p>Confidence: {ml_conf:.1f}%</p>
            </div>"""

        # Build semantic HTML
        semantic_html = ""
        if semantic:
            semantic_html = f"""
            <div style="display:flex;gap:20px;text-align:center;flex-wrap:wrap;">
                <div style="flex:1;min-width:120px;">
                    <h6>Embedding Dimension</h6>
                    <h3 style="color:#0d6efd;">{semantic.get('embedding_dimension', 'N/A')}</h3>
                </div>
                <div style="flex:1;min-width:120px;">
                    <h6>Token Count</h6>
                    <h3 style="color:#198754;">{semantic.get('token_count', 'N/A')}</h3>
                </div>
                <div style="flex:1;min-width:120px;">
                    <h6>Semantic Score</h6>
                    <h3 style="color:#ffc107;">{semantic.get('semantic_score', 'N/A')}</h3>
                </div>
                <div style="flex:1;min-width:120px;">
                    <h6>Confidence</h6>
                    <h3 style="color:#dc3545;">{semantic.get('confidence', 'N/A')}</h3>
                </div>
            </div>"""

        import html as html_module
        escaped_source = html_module.escape(source_code)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review Report - {filename}</title>
    <style>
        @media print {{
            body {{ font-size: 12px; }}
            .no-print {{ display: none; }}
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f9;
            color: #333;
            padding: 30px;
        }}
        .report-container {{
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        .report-header {{
            text-align: center;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .report-header h1 {{
            color: #2c3e50;
            font-size: 28px;
        }}
        .report-header p {{
            color: #6c757d;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}
        .score-display {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .score-number {{
            font-size: 64px;
            font-weight: bold;
            color: {label_color};
        }}
        .quality-label {{
            font-size: 20px;
            font-weight: bold;
            color: {label_color};
            margin-top: 5px;
        }}
        .progress-bar-container {{
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            margin-top: 15px;
            overflow: hidden;
        }}
        .progress-bar-fill {{
            height: 100%;
            background: {label_color};
            border-radius: 10px;
            width: {quality_score}%;
            transition: width 0.5s;
        }}
        .code-block {{
            background: #0d1117;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 10px;
            overflow: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        th {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="report-container">

        <div class="report-header">
            <h1>🤖 Automated Code Review Report</h1>
            <p><strong>File:</strong> {filename} | <strong>Generated:</strong> {now}</p>
        </div>

        <div class="section">
            <div class="score-display">
                <div class="score-number">{quality_score} / 100</div>
                <div class="quality-label">{quality_label}</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill"></div>
                </div>
            </div>
        </div>

        {ml_html}

        <div class="section">
            <h3>📊 AST Analysis</h3>
            <table>{ast_rows}</table>
        </div>

        <div class="section">
            <h3>⚠️ Issues Found ({issue_count})</h3>
            {issues_html}
        </div>

        <div class="section">
            <h3>💡 Suggestions</h3>
            {suggestions_html if suggestions_html else '<p>No suggestions.</p>'}
        </div>

        <div class="section">
            <h3>🧠 Semantic Analysis</h3>
            {semantic_html if semantic_html else '<p>No semantic analysis available.</p>'}
        </div>

        <div class="section">
            <h3>📄 Source Code</h3>
            <div class="code-block">{escaped_source}</div>
        </div>

    </div>
</body>
</html>"""

        return html
