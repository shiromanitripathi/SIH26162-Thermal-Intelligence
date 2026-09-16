"""
Model evaluation module for thermal source classification (SIH26162).
"""

import json
import joblib
import pandas as pd
from pathlib import Path

from src.features.feature_config import PROJECT_ROOT

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_ARTIFACT_PATH = MODELS_DIR / "baseline_rf_model.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"


def load_evaluation_summary():
    """Load model evaluation metrics and metadata."""
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found at {METADATA_PATH}. Run training first.")
        
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    return metadata


def print_evaluation_report():
    """Print comprehensive clean markdown evaluation report."""
    metadata = load_evaluation_summary()
    
    print("=" * 70)
    print(f"SIH26162 THERMAL SOURCE ML BASELINE EVALUATION REPORT")
    print("=" * 70)
    print(f"Selected Model: {metadata['selected_model']}")
    print(f"Dataset Split: Grouped Spatial Split by grid_id (Zero Leakage)")
    print(f"Training Samples: {metadata['num_train_samples']:,}")
    print(f"Validation Samples: {metadata['num_val_samples']:,}")
    print(f"Test Samples: {metadata['num_test_samples']:,}\n")
    
    metrics_df = []
    for model_name, m in metadata["evaluation_metrics"].items():
        metrics_df.append({
            "Model": model_name,
            "Accuracy": f"{m['accuracy']:.4f}",
            "Precision": f"{m['precision']:.4f}",
            "Recall": f"{m['recall']:.4f}",
            "F1-Score": f"{m['f1_score']:.4f}",
            "Specificity": f"{m['specificity']:.4f}",
            "ROC-AUC": f"{m['roc_auc']:.4f}",
            "PR-AUC": f"{m['pr_auc']:.4f}",
            "TP": m["confusion_matrix"]["TP"],
            "FP": m["confusion_matrix"]["FP"],
            "TN": m["confusion_matrix"]["TN"],
            "FN": m["confusion_matrix"]["FN"]
        })
        
    report_table = pd.DataFrame(metrics_df)
    print(report_table.to_string(index=False))
    
    print("\nTOP FEATURE IMPORTANCES (EXPLAINABILITY):")
    print("-" * 50)
    for feat, imp in list(metadata["feature_importances"].items())[:10]:
        print(f"  {feat:<25}: {imp:.4f}")
    print("=" * 70)


if __name__ == "__main__":
    print_evaluation_report()
