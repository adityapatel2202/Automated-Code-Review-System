"""
Feature Engineering Module for the Automated Code Review System.

Loads the features dataset, performs encoding and scaling transformations,
and provides train/test splits for model training.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder


# Path to the features CSV dataset
FEATURES_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "dataset", "features", "features.csv"
)

# Columns to drop before training (non-feature metadata and derived target)
DROP_COLUMNS = ["repository", "function_name"]

# The target variable column
TARGET_COLUMN = "quality_label"

# Columns that should NOT be scaled (they are encoded separately or are the target)
# quality_score is a derived numeric — we keep it as a feature but scale it normally
CATEGORICAL_COLUMNS = ["readability"]
BOOLEAN_COLUMNS = ["syntax_error"]


def load_and_prepare_data():
    """
    Load features.csv and prepare data for ML training.

    Returns:
        tuple: (X_train, X_test, y_train, y_test, scaler, label_encoders)
            - X_train (np.ndarray): Scaled training features
            - X_test (np.ndarray): Scaled testing features
            - y_train (np.ndarray): Encoded training labels
            - y_test (np.ndarray): Encoded testing labels
            - scaler (StandardScaler): Fitted scaler for numerical features
            - label_encoders (dict): Mapping of column name -> fitted LabelEncoder
    """
    # ------------------------------------------------------------------
    # 1. Load the dataset
    # ------------------------------------------------------------------
    df = pd.read_csv(FEATURES_CSV_PATH)
    print(f"[INFO] Loaded dataset with shape: {df.shape}")

    # ------------------------------------------------------------------
    # 2. Drop non-feature columns
    # ------------------------------------------------------------------
    df = df.drop(columns=DROP_COLUMNS, errors="ignore")

    # ------------------------------------------------------------------
    # 3. Separate the target variable
    # ------------------------------------------------------------------
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(df[TARGET_COLUMN])
    df = df.drop(columns=[TARGET_COLUMN])

    # Also drop quality_score — it is a derived score, not a raw feature
    # and would leak the target variable
    df = df.drop(columns=["quality_score"], errors="ignore")

    # ------------------------------------------------------------------
    # 4. Encode categorical features
    # ------------------------------------------------------------------
    label_encoders = {"quality_label": target_encoder}

    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le

    # ------------------------------------------------------------------
    # 5. Convert boolean columns to int
    # ------------------------------------------------------------------
    for col in BOOLEAN_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).map(
                {"True": 1, "False": 0, "1": 1, "0": 0}
            ).fillna(0).astype(int)

    # ------------------------------------------------------------------
    # 6. Ensure all remaining columns are numeric
    # ------------------------------------------------------------------
    feature_columns = df.columns.tolist()
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    # ------------------------------------------------------------------
    # 7. Normalize numerical features with StandardScaler
    # ------------------------------------------------------------------
    scaler = StandardScaler()
    X = scaler.fit_transform(df)

    # Store feature column names on the scaler for later reference
    scaler.feature_names_ = feature_columns

    # ------------------------------------------------------------------
    # 8. Train/test split (80/20)
    # ------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"[INFO] Feature columns ({len(feature_columns)}): {feature_columns}")
    print(f"[INFO] Target classes: {list(target_encoder.classes_)}")
    print(f"[INFO] X_train shape: {X_train.shape}")
    print(f"[INFO] X_test shape:  {X_test.shape}")
    print(f"[INFO] y_train shape: {y_train.shape}")
    print(f"[INFO] y_test shape:  {y_test.shape}")

    return X_train, X_test, y_train, y_test, scaler, label_encoders


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, scaler, label_encoders = load_and_prepare_data()
    print("\n--- Summary ---")
    print(f"Training samples:   {X_train.shape[0]}")
    print(f"Testing samples:    {X_test.shape[0]}")
    print(f"Number of features: {X_train.shape[1]}")
    print(f"Label encoders:     {list(label_encoders.keys())}")
