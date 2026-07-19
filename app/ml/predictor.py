"""
Quality Predictor for the Automated Code Review System.

Loads the trained Random Forest model and associated artifacts, extracts
features from a given Python file, and predicts the code quality label.
"""

import os
import sys
import numpy as np
import joblib
import pandas as pd

# Add the project root to sys.path so we can import app modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.ml.feature_extractor import MLFeatureExtractor


# Paths to saved model artifacts
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "random_forest_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
LABEL_ENCODERS_PATH = os.path.join(MODEL_DIR, "label_encoders.pkl")


class QualityPredictor:
    """
    Predicts the quality label of a Python source file using the
    trained Random Forest model.
    """

    def __init__(self):
        """
        Load model, scaler, and label encoders from disk.

        If the model files do not exist yet (i.e. the model has not been
        trained), the predictor will still be instantiated but will return
        a fallback result on every prediction.
        """
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.extractor = MLFeatureExtractor()

        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH) and os.path.exists(LABEL_ENCODERS_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.label_encoders = joblib.load(LABEL_ENCODERS_PATH)
                print("[INFO] Model artifacts loaded successfully.")
            except Exception as e:
                print(f"[WARNING] Failed to load model artifacts: {e}")
                self.model = None
        else:
            print("[WARNING] Model artifacts not found. Train the model first "
                  "by running app.ml.train_random_forest.")

    def predict(self, file_path):
        """
        Predict the quality label for a Python source file.

        Args:
            file_path (str): Absolute path to the Python file.

        Returns:
            dict: {
                "quality_label": str,  — Predicted label (Excellent/Good/Average/Poor)
                "confidence": float,   — Prediction confidence (max probability)
                "features": dict       — Raw extracted features for transparency
            }
        """
        # ------------------------------------------------------------------
        # Fallback when model is not available
        # ------------------------------------------------------------------
        if self.model is None:
            return {
                "quality_label": "Unknown",
                "prediction": "Unknown",
                "confidence": 0.0,
                "features": {},
                "error": "Model not trained yet. Run train_random_forest.py first."
            }

        # ------------------------------------------------------------------
        # 1. Extract raw features from the file
        # ------------------------------------------------------------------
        raw_features = self.extractor.extract(file_path)

        # ------------------------------------------------------------------
        # 2. Apply the same transformations used during training
        # ------------------------------------------------------------------
        # Build a DataFrame with columns in the same order as training
        feature_columns = self.scaler.feature_names_
        feature_dict = {}

        for col in feature_columns:
            if col in raw_features:
                feature_dict[col] = raw_features[col]
            else:
                feature_dict[col] = 0

        df = pd.DataFrame([feature_dict])

        # Encode categorical columns using the saved label encoders
        if "readability" in df.columns and "readability" in self.label_encoders:
            readability_encoder = self.label_encoders["readability"]
            readability_value = df["readability"].iloc[0]
            # Handle unseen categories gracefully
            if readability_value in readability_encoder.classes_:
                df["readability"] = readability_encoder.transform(
                    df["readability"].astype(str)
                )
            else:
                # Fall back to the most common class index
                df["readability"] = 0

        # Convert syntax_error boolean to int
        if "syntax_error" in df.columns:
            df["syntax_error"] = df["syntax_error"].astype(str).map(
                {"True": 1, "False": 0, "1": 1, "0": 0}
            ).fillna(0).astype(int)

        # Ensure all values are numeric
        df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

        # ------------------------------------------------------------------
        # 3. Scale features with the training scaler
        # ------------------------------------------------------------------
        X = self.scaler.transform(df)

        # ------------------------------------------------------------------
        # 4. Predict
        # ------------------------------------------------------------------
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = float(np.max(probabilities))

        # Decode the numeric label back to a string
        target_encoder = self.label_encoders["quality_label"]
        quality_label = target_encoder.inverse_transform([prediction])[0]

        return {
            "quality_label": quality_label,
            "prediction": quality_label,
            "confidence": round(confidence, 4),
            "features": raw_features
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.ml.predictor <path_to_python_file>")
        sys.exit(1)

    predictor = QualityPredictor()
    result = predictor.predict(sys.argv[1])

    print("\n========== Prediction Result ==========")
    print(f"Quality Label : {result['quality_label']}")
    print(f"Confidence    : {result['confidence']}")
    if "error" in result:
        print(f"Error         : {result['error']}")
    print("\nFeatures:")
    for key, value in result.get("features", {}).items():
        print(f"  {key:25s}: {value}")
    print("========================================")
