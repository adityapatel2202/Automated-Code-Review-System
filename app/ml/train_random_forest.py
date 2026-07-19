"""
Random Forest Training Module for the Automated Code Review System.

Trains a Random Forest classifier on the prepared feature dataset,
evaluates performance, and persists the model artifacts to disk.
"""

import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

from app.ml.feature_engineering import load_and_prepare_data


# Directory where trained model artifacts are saved
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")

# File paths for persisted artifacts
MODEL_PATH = os.path.join(MODEL_DIR, "random_forest_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
LABEL_ENCODERS_PATH = os.path.join(MODEL_DIR, "label_encoders.pkl")


def train_model():
    """
    Train a Random Forest classifier and save all artifacts.

    Steps:
        1. Load and prepare the feature-engineered data.
        2. Train a RandomForestClassifier with 100 estimators.
        3. Evaluate on the test set and print metrics.
        4. Save the model, scaler, and label encoders to disk.

    Returns:
        tuple: (model, accuracy) — the trained model and its test accuracy.
    """
    # ------------------------------------------------------------------
    # 1. Prepare the data
    # ------------------------------------------------------------------
    X_train, X_test, y_train, y_test, scaler, label_encoders = load_and_prepare_data()

    # ------------------------------------------------------------------
    # 2. Train the Random Forest classifier
    # ------------------------------------------------------------------
    print("\n[INFO] Training Random Forest classifier ...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("[INFO] Training complete.")

    # ------------------------------------------------------------------
    # 3. Evaluate the model
    # ------------------------------------------------------------------
    y_pred = model.predict(X_test)

    # Decode labels back to class names for a readable report
    target_encoder = label_encoders["quality_label"]
    target_names = list(target_encoder.classes_)

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test, y_pred, target_names=target_names, zero_division=0
    )
    cm = confusion_matrix(y_test, y_pred)

    print("\n========== Evaluation Results ==========")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"\nClassification Report:\n{report}")
    print(f"Confusion Matrix:\n{cm}")
    print("========================================\n")

    # ------------------------------------------------------------------
    # 4. Save model artifacts
    # ------------------------------------------------------------------
    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    print(f"[INFO] Model saved to:          {MODEL_PATH}")

    joblib.dump(scaler, SCALER_PATH)
    print(f"[INFO] Scaler saved to:         {SCALER_PATH}")

    joblib.dump(label_encoders, LABEL_ENCODERS_PATH)
    print(f"[INFO] Label encoders saved to: {LABEL_ENCODERS_PATH}")

    return model, accuracy


if __name__ == "__main__":
    trained_model, test_accuracy = train_model()
    print(f"\nFinal test accuracy: {test_accuracy:.4f}")
