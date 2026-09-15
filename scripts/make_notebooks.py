import json
from pathlib import Path

def make_nb(cells):
    return {
        'cells': cells,
        'metadata': {
            'language_info': {'name': 'python'}
        },
        'nbformat': 4,
        'nbformat_minor': 2
    }

def code_cell(src):
    return {'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': src.splitlines(keepends=True)}

def md_cell(src):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': src.splitlines(keepends=True)}

# 01 Data Understanding
cells_01 = [
    md_cell('# 01 — FIRMS Data Understanding and Verification\n\nThis notebook inspects NASA FIRMS VIIRS S-NPP thermal hotspot observations for SIH26162.'),
    code_cell('''import pandas as pd
import numpy as np
from pathlib import Path

RAW_FIRMS_PATH = Path("../data/raw/FIRMS/fire_archive_SV-C2_806010.csv")
df = pd.read_csv(RAW_FIRMS_PATH)
print("Raw FIRMS Shape:", df.shape)
display(df.head())'''),
    code_cell('''print("=== DATA TYPES AND MISSING VALUES ===")
print("Missing values per column:")
print(df.isna().sum())
print("\\nData types:")
print(df.dtypes)'''),
    code_cell('''print("=== TEMPORAL RANGE AND TYPE DISTRIBUTION ===")
df["acq_date"] = pd.to_datetime(df["acq_date"])
print("Start Date:", df["acq_date"].min())
print("End Date:", df["acq_date"].max())
print("Total Days Span:", (df["acq_date"].max() - df["acq_date"].min()).days)
print("\\nFIRMS Type Distribution:")
print(df["type"].value_counts(dropna=False))'''),
    code_cell('''print("=== DIURNAL AND NUMERIC SUMMARY ===")
print("Day/Night Distribution:")
print(df["daynight"].value_counts())
print("\\nFRP Brightness Summary:")
display(df[["brightness", "bright_t31", "frp"]].describe())''')
]

# 02 Feature Engineering
cells_02 = [
    md_cell('# 02 — Spatial Aggregation, Feature Engineering, and OSM Context\n\nAggregates 1.74M observations into 644k spatial cells and merges OpenStreetMap context.'),
    code_cell('''import pandas as pd
import numpy as np
from src.features.build_features import build_full_feature_dataset

merged_df = build_full_feature_dataset()
print("Merged Dataset Shape:", merged_df.shape)
display(merged_df.head())'''),
    code_cell('''print("=== SPATIAL AND PERSISTENCE SUMMARY ===")
print("Observation Count Distribution:")
print(merged_df["observation_count"].describe())
print("\\nActive Days Distribution:")
print(merged_df["active_days"].describe())
print("\\nTarget Label Distribution (Zero OSM Leakage):")
print(merged_df["target_persistent_source"].value_counts())'''),
    code_cell('''print("=== OSM CONTEXT FEATURES SUMMARY ===")
osm_cols = ["osm_feature_count", "osm_industrial_count", "osm_power_count", "osm_manmade_count", "osm_min_distance_m"]
display(merged_df[osm_cols].describe())''')
]

# 03 Baseline Models
cells_03 = [
    md_cell('# 03 — Baseline Model Training and Grouped Validation\n\nTrains Logistic Regression, Random Forest, HistGradientBoosting, and Isolation Forest models.'),
    code_cell('''from src.models.train import train_and_evaluate_all_models

metadata = train_and_evaluate_all_models()
print("Selected Best Model:", metadata["selected_model"])
print("Train / Val / Test Split:", metadata["num_train_samples"], metadata["num_val_samples"], metadata["num_test_samples"])''')
]

# 04 Model Evaluation
cells_04 = [
    md_cell('# 04 — Model Evaluation and Predictor Demonstration\n\nEvaluates baseline models and demonstrates explainable predictor output on real thermal candidates.'),
    code_cell('''from src.models.evaluate import print_evaluation_report
from src.models.predictor import get_predictor
import pandas as pd

print_evaluation_report()'''),
    code_cell('''print("=== DEMO: EXPLAINABLE PREDICTION ON REAL THERMAL CELL ===")
df = pd.read_csv("../data/processed/firms_osm_merged_dataset.csv")
candidate_cell = df[df["target_persistent_source"] == 1].iloc[0]

predictor = get_predictor()
res = predictor.predict(candidate_cell)
print("Classification:", res["classification"])
print("Confidence:", res["confidence_score"])
print("Explanation Summary:\\n" + res["explanation_summary"])''')
]

for name, cells in [
    ('01_data_understanding.ipynb', cells_01),
    ('02_feature_engineering.ipynb', cells_02),
    ('03_baseline_models.ipynb', cells_03),
    ('04_model_evaluation.ipynb', cells_04)
]:
    p = Path('notebooks') / name
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(make_nb(cells), f, indent=2)
    print("Wrote notebook:", p)
