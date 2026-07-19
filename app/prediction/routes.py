from flask import render_template, request, jsonify
from flask_login import login_required

from . import prediction_bp
from app.ml.predictor import QualityPredictor


@prediction_bp.route("/")
@login_required
def prediction_page():
    return render_template("prediction/prediction.html")


@prediction_bp.route("/predict", methods=["POST"])
@login_required
def predict():
    filename = request.form.get("filename") or request.json.get("filename", "")

    if not filename:
        return jsonify({"error": "No filename provided"}), 400

    file_path = f"uploads/{filename}"

    try:
        predictor = QualityPredictor()
        result = predictor.predict(file_path)

        return jsonify({
            "success": True,
            "prediction": result.get("prediction", "Unknown"),
            "confidence": result.get("confidence", 0.0),
            "filename": filename,
        })

    except FileNotFoundError:
        return jsonify({"error": "Model not trained yet. Please train the model first."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
