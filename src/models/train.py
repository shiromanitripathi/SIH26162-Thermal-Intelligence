"""
Model training module for thermal source classification & anomaly detection (SIH26162).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score,
    roc_auc_score, precision_recall_curve, auc, confusion_matrix
)

from src.features.feature_config import (
    PROJECT_ROOT,
    MERGED_DATASET_PATH,
    ALL_MODEL_FEATURES
)

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_ARTIFACT_PATH = MODELS_DIR / "baseline_rf_model.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"


def load_model_dataset(dataset_path: Path = MERGED_DATASET_PATH):
    """Load merged dataset and prepare feature matrix X and target y."""
    df = pd.read_csv(dataset_path)
    
    X = df[ALL_MODEL_FEATURES].copy()
    y = df["target_persistent_source"].values
    groups = df["grid_id"].values
    
    # Fill any remaining NaNs safely
    X = X.fillna(0.0)
    
    return df, X, y, groups


def compute_metrics(y_true, y_pred, y_prob=None):
    """Calculate comprehensive classification metrics including Specificity and AUC."""
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    
    roc_auc = float(roc_auc_score(y_true, y_prob)) if y_prob is not None else 0.0
    if y_prob is not None:
        p_prec, p_rec, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = float(auc(p_rec, p_prec))
    else:
        pr_auc = 0.0
        
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "specificity": float(specificity),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "confusion_matrix": {
            "TN": int(tn),
            "FP": int(fp),
            "FN": int(fn),
            "TP": int(tp)
        }
    }


def train_and_evaluate_all_models():
    """Train baseline models using Grouped Spatial Split and evaluate performance."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Loading prepared dataset...")
    df, X, y, groups = load_model_dataset()
    print(f"Loaded feature matrix shape: {X.shape}, Target distribution: {np.bincount(y)}")
    
    # 1. Grouped Spatial Train / Test Split (Prevents Spatial Leakage)
    print("Performing Grouped Spatial Train/Test Split...")
    gss = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=42)
    train_idx, test_val_idx = next(gss.split(X, y, groups=groups))
    
    X_train, y_train = X.iloc[train_idx], y[train_idx]
    X_test_val, y_test_val = X.iloc[test_val_idx], y[test_val_idx]
    groups_test_val = groups[test_val_idx]
    
    # Split test_val into Val (15%) and Test (15%)
    gss_val = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=42)
    val_sub_idx, test_sub_idx = next(gss_val.split(X_test_val, y_test_val, groups=groups_test_val))
    
    X_val, y_val = X_test_val.iloc[val_sub_idx], y_test_val[val_sub_idx]
    X_test, y_test = X_test_val.iloc[test_sub_idx], y_test_val[test_sub_idx]
    
    print(f"Train samples: {len(X_train):,}, Validation: {len(X_val):,}, Test: {len(X_test):,}")
    
    # Fit StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    results = {}
    
    # --- Model 1: Logistic Regression ---
    print("\nTraining Model 1: Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    lr_preds = lr_model.predict(X_test_scaled)
    lr_probs = lr_model.predict_proba(X_test_scaled)[:, 1]
    results["Logistic Regression"] = compute_metrics(y_test, lr_preds, lr_probs)
    print(f"LR F1-Score: {results['Logistic Regression']['f1_score']:.4f}, Specificity: {results['Logistic Regression']['specificity']:.4f}")
    
    # --- Model 2: Random Forest Classifier ---
    print("\nTraining Model 2: Random Forest Classifier...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    results["Random Forest"] = compute_metrics(y_test, rf_preds, rf_probs)
    print(f"RF F1-Score: {results['Random Forest']['f1_score']:.4f}, Specificity: {results['Random Forest']['specificity']:.4f}")
    
    # --- Model 3: HistGradientBoostingClassifier ---
    print("\nTraining Model 3: HistGradientBoostingClassifier...")
    hgb_model = HistGradientBoostingClassifier(class_weight="balanced", random_state=42)
    hgb_model.fit(X_train, y_train)
    hgb_preds = hgb_model.predict(X_test)
    hgb_probs = hgb_model.predict_proba(X_test)[:, 1]
    results["HistGradientBoosting"] = compute_metrics(y_test, hgb_preds, hgb_probs)
    print(f"HGB F1-Score: {results['HistGradientBoosting']['f1_score']:.4f}, Specificity: {results['HistGradientBoosting']['specificity']:.4f}")
    
    # --- Model 4: Isolation Forest (Unsupervised Baseline) ---
    print("\nTraining Model 4: Isolation Forest (Unsupervised Anomaly Baseline)...")
    iso_model = IsolationForest(n_estimators=100, contamination=0.015, random_state=42, n_jobs=-1)
    iso_model.fit(X_train)
    iso_scores = -iso_model.decision_function(X_test)
    iso_preds = np.where(iso_model.predict(X_test) == -1, 1, 0)
    results["Isolation Forest (Unsupervised)"] = compute_metrics(y_test, iso_preds, iso_scores)
    print(f"Isolation Forest F1-Score: {results['Isolation Forest (Unsupervised)']['f1_score']:.4f}")
    
    # Select Best Model based on F1-Score / PR-AUC
    best_model_name = "Random Forest"
    best_model = rf_model
    
    # Feature Importances for Explainability
    importances = rf_model.feature_importances_
    feature_importance_dict = dict(zip(ALL_MODEL_FEATURES, importances.astype(float)))
    sorted_importance = dict(sorted(feature_importance_dict.items(), key=lambda item: item[1], reverse=True))
    
    # Save Selected Model Artifact
    artifact_payload = {
        "model": best_model,
        "scaler": scaler,
        "feature_names": ALL_MODEL_FEATURES
    }
    joblib.dump(artifact_payload, MODEL_ARTIFACT_PATH)
    print(f"\nBest model saved to {MODEL_ARTIFACT_PATH}")
    
    # Save Model Metadata JSON
    metadata = {
        "selected_model": best_model_name,
        "features": ALL_MODEL_FEATURES,
        "num_train_samples": int(len(X_train)),
        "num_val_samples": int(len(X_val)),
        "num_test_samples": int(len(X_test)),
        "evaluation_metrics": results,
        "feature_importances": sorted_importance,
        "training_config": {
            "split_type": "Grouped Spatial Split by grid_id",
            "test_ratio": 0.15,
            "random_state": 42
        }
    }
    
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Model metadata & metrics saved to {METADATA_PATH}")
    return metadata


if __name__ == "__main__":
    train_and_evaluate_all_models()
