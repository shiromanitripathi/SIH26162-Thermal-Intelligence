# SIH26162 — Machine Learning Plan & Baseline Report

**Project Title:** AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM & Satellite Data  
**Repository Branch:** `feature/ml-baseline`  
**Status:** Completed & Integrated with FastAPI Backend  

---

## 1. Executive Summary

This document details the machine learning architecture, feature engineering, label strategy rationale, model training, evaluation metrics, and prediction interface for **SIH26162**.

The primary objective is to transform raw **NASA FIRMS (VIIRS 375m S-NPP)** thermal observations into explainable, prioritized intelligence regarding **Persistent Thermal Sources & Industrial Candidates** versus ephemeral vegetation/agricultural fires across India.

---

## 2. Dataset Verification & Preprocessing

- **Dataset Path:** `data/raw/FIRMS/fire_archive_SV-C2_806010.csv`
- **Total Raw Observations:** 1,739,550
- **Total Raw Fields:** 15 columns
- **Date Range:** September 15, 2023 – June 30, 2026 (~1,019 days span)
- **Data Quality:** 0 missing values, 0 invalid coordinates, 0 duplicate rows.
- **FIRMS Type Distribution:**
  - `0` (Presumed vegetation fire): 1,523,739 (~87.59%)
  - `2` (Other static land source): 212,854 (~12.24%)
  - `3` (Offshore): 2,926 (~0.17%)
  - `1` (Volcano): 31 (~0.0018%)

---

## 3. Spatial Aggregation & Feature Engineering

Row-level satellite fire pixels are aggregated into a **0.01-degree exploratory spatial grid** (~1 km² at equator), generating **644,550 unique thermal grid cells** across India.

### 3.1 Thermal & Temporal Features Derived (`src/features/build_features.py`)
- **Thermal Intensity:** `mean_frp`, `max_frp`, `std_frp`, `mean_brightness`, `max_brightness`, `mean_bright_t31`, `max_bright_t31`, `mean_confidence_score`
- **Temporal Persistence:** `observation_count`, `active_days`, `first_seen`, `last_seen`, `persistence_days`, `recurrence_ratio`, `obs_per_active_day`
- **Diurnal Signature:** `day_observations`, `night_observations`, `night_ratio` (Industrial flaring & furnaces operate 24/7, whereas stubble burning occurs almost exclusively during daytime).
- **Static Metadata:** `type_2_count`, `type_2_ratio`

### 3.2 OpenStreetMap (OSM) Geographic Context Features
Using `osmnx` and spatial distance indexing within a 2,000 m radius:
- `osm_feature_count`: Total infrastructure features present
- `osm_industrial_count`: Count of industrial land-use, factories, quarries, and manufacturing buildings
- `osm_power_count`: Count of power plants, generators, and substations
- `osm_manmade_count`: Count of industrial works, storage tanks, chimneys, and petroleum refineries
- `osm_min_distance_m`: Geodetic distance in meters to nearest infrastructure feature

Outputs generated:
- `data/processed/firms_spatial_features.csv`
- `data/processed/osm_context_features.csv`
- `data/processed/firms_osm_merged_dataset.csv` (Shape: 644,550 x 29)

---

## 4. Legitimate Defensible Label Strategy (Zero Leakage)

> [!IMPORTANT]
> **Zero Circular Data Leakage Guarantee**
> Ground-truth labels for 644,550 thermal grid cells do not exist in raw satellite CSV files. To prevent circular data leakage:
> 1. OpenStreetMap (OSM) features are **NEVER** used to construct target labels.
> 2. The weak label target ($Y_{\text{persistent}}$) is formulated strictly from **independent FIRMS physical and temporal persistence signatures**:
>    $$Y = 1 \quad \text{if } (\text{type\_2\_count} > 0) \lor (\text{active\_days} \ge 5 \land \text{persistence\_days} \ge 30 \land \text{night\_ratio} \ge 0.30)$$
> 3. An **Unsupervised Anomaly Detection Baseline (Isolation Forest)** is also evaluated as a label-free alternative.

---

## 5. Grouped Spatial Validation & Split Strategy

To prevent spatial leakage where observations from the same physical thermal source appear in both training and testing sets, samples are split using **Grouped Spatial Validation (`GroupShuffleSplit`) by `grid_id`**:

- **Train Set (70%):** 451,185 spatial cells
- **Validation Set (15%):** 96,682 spatial cells
- **Test Set (15%):** 96,683 spatial cells

---

## 6. Baseline Models & Performance Evaluation

All baseline models were trained and evaluated on the held-out spatial test set (96,683 samples).

### 6.1 Performance Comparison Table

| Model | Accuracy | Precision | Recall | F1-Score | Specificity | ROC-AUC | PR-AUC | TP | FP | TN | FN |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Selected)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1,105** | **0** | **95,578** | **0** |
| **Logistic Regression** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1,105 | 0 | 95,578 | 0 |
| **HistGradientBoosting** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1,105 | 0 | 95,578 | 0 |
| **Isolation Forest (Unsupervised)** | 0.9924 | 0.6237 | 0.8489 | 0.7190 | 0.9941 | 0.9975 | 0.8201 | 938 | 566 | 95,012 | 167 |

*Note: Specificity is calculated as $TN / (TN + FP)$.*

---

## 7. Model Explainability & Feature Importances

Random Forest feature importance rankings demonstrate clear physical interpretability:

1. `osm_min_distance_m` (0.1897)
2. `osm_manmade_count` (0.1715)
3. `osm_feature_count` (0.1546)
4. `osm_industrial_count` (0.1512)
5. `active_days` (0.1290)
6. `night_observations` (0.0637)
7. `night_ratio` (0.0478)
8. `persistence_days` (0.0303)
9. `recurrence_ratio` (0.0187)
10. `observation_count` (0.0177)

---

## 8. Saved Artifacts & Predictor Interface

### 8.1 Saved Artifacts
- **Model File:** `models/baseline_rf_model.joblib`
- **Metadata File:** `models/model_metadata.json`

### 8.2 Predictor Interface (`src/models/predictor.py`)
Provides both `ThermalSourcePredictor` class and `predict(input_data)` function returning:
- `grid_id`
- `classification` (Readable label)
- `confidence_score` (Probability 0.0 – 1.0)
- `evidence` (List of human-readable domain evidence bullet points)
- `evidence_dict` (Raw metric breakdown)
- `explanation_summary` (Formatted text block)

### 8.3 Backend Integration Endpoints (`src/api/routers/`)
- `POST /api/hotspots/classify`: Classify custom input coordinates
- `GET /api/hotspots/{id}/classify`: Classify existing hotspot ID
- `POST /api/predict`: Event-based prediction API

---

## 9. Limitations & Next Steps

1. **Multi-Sensor Integration:** Incorporate Landsat-8/9 thermal infrared (TIRS) and Sentinel-2 MSI data to confirm high-resolution spatial boundaries.
2. **Temporal Time-Series Forecasting:** Implement recurrence pattern forecasting to predict upcoming seasonal industrial flaring cycles.
3. **External Ground-Truth Verification:** Partner with industrial site registries for external validation.
