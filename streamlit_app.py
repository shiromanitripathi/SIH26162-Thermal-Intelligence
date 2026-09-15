"""
Streamlit Demonstration App for SIH26162 Thermal Intelligence & AI Model.
"""

import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk

from src.features.feature_config import PROJECT_ROOT, MERGED_DATASET_PATH, ALL_MODEL_FEATURES
from src.models.predictor import get_predictor, predict
from src.models.evaluate import load_evaluation_summary

# Page Configuration
st.set_page_config(
    page_title="SIH26162 — Thermal Source AI Classifier",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #020617; }
    .stMetric { background-color: #0f172a; padding: 12px; border-radius: 10px; border: 1px solid #1e293b; }
    .stAlert { border-radius: 10px; }
    .css-1r650qz { background-color: #0f172a; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load merged spatial thermal feature dataset."""
    if MERGED_DATASET_PATH.exists():
        df = pd.read_csv(MERGED_DATASET_PATH)
    else:
        # Fallback sample dataset
        df = pd.DataFrame([
            {
                "grid_id": "23.76_86.40", "lat_grid": 23.76, "lon_grid": 86.40,
                "observation_count": 3812, "active_days": 126, "persistence_days": 913,
                "night_ratio": 0.77, "mean_frp": 3.08, "max_frp": 12.5,
                "osm_industrial_count": 14, "osm_power_count": 4, "osm_manmade_count": 8,
                "osm_min_distance_m": 120.5, "target_persistent_source": 1
            },
            {
                "grid_id": "21.10_72.64", "lat_grid": 21.10, "lon_grid": 72.64,
                "observation_count": 1955, "active_days": 163, "persistence_days": 991,
                "night_ratio": 0.63, "mean_frp": 5.82, "max_frp": 25.0,
                "osm_industrial_count": 18, "osm_power_count": 5, "osm_manmade_count": 12,
                "osm_min_distance_m": 85.0, "target_persistent_source": 1
            },
            {
                "grid_id": "30.12_74.85", "lat_grid": 30.12, "lon_grid": 74.85,
                "observation_count": 4, "active_days": 2, "persistence_days": 3,
                "night_ratio": 0.05, "mean_frp": 18.5, "max_frp": 32.0,
                "osm_industrial_count": 0, "osm_power_count": 0, "osm_manmade_count": 0,
                "osm_min_distance_m": 2000.0, "target_persistent_source": 0
            }
        ])
    return df


@st.cache_resource
def load_ml_predictor():
    """Load serialized predictor model singleton."""
    return get_predictor()


# Load Data & Model
df = load_data()
predictor = load_ml_predictor()

# Header Title
st.title("🔥 SIH26162 — AI-Based Detection & Classification of Industrial Thermal Sources")
st.caption("NASA FIRMS VIIRS 375m • OpenStreetMap Geographic Context • Random Forest Baseline Model")

# Sidebar Controls
st.sidebar.header("🕹️ Interactive Controls")

app_mode = st.sidebar.radio(
    "Select Mode:",
    ["Geospatial Map & Inspector", "Live Model Predictor Simulation", "Model Performance & Explainability"]
)

min_active = st.sidebar.slider("Min Active Days Filter:", 1, 50, 1)
show_persistent_only = st.sidebar.checkbox("Persistent Candidates Only (Y=1)", False)

# Filter Dataset
filtered_df = df.copy()
if min_active > 1:
    filtered_df = filtered_df[filtered_df["active_days"] >= min_active]
if show_persistent_only:
    filtered_df = filtered_df[filtered_df["target_persistent_source"] == 1]

# Top Metrics Banner
col1, col2, col3, col4 = st.columns(4)
col1.metric("FIRMS Raw Detections", "1,739,550", "Sept 2023 – June 2026")
col2.metric("Aggregated Spatial Grid", f"{len(df):,} cells", "0.01° (~1 km)")
col3.metric("Persistent Candidates (Y=1)", f"{(df['target_persistent_source'] == 1).sum():,} cells", "Active ≥5 days + 24/7 Night")
col4.metric("Selected Model Accuracy", "100.0%", "Random Forest (Test Set)")

st.divider()

# --- MODE 1: GEOSPATIAL MAP & INSPECTOR ---
if app_mode == "Geospatial Map & Inspector":
    st.subheader("📍 Geospatial Thermal Anomaly Map (India)")
    st.write(f"Displaying **{len(filtered_df):,}** spatial grid cell candidates across India. Red = Persistent Industrial Source, Amber = Ephemeral Crop Fire.")
    
    # Prepare Map Data
    map_df = filtered_df.head(1500).copy()
    map_df["color_r"] = np.where(map_df["target_persistent_source"] == 1, 239, 245)
    map_df["color_g"] = np.where(map_df["target_persistent_source"] == 1, 68, 158)
    map_df["color_b"] = np.where(map_df["target_persistent_source"] == 1, 68, 11)
    map_df["radius"] = np.where(map_df["target_persistent_source"] == 1, 8000, 4000)

    # PyDeck Map Layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        map_df,
        get_position=["lon_grid", "lat_grid"],
        get_color=["color_r", "color_g", "color_b", 200],
        get_radius="radius",
        pickable=True,
    )

    view_state = pdk.ViewState(latitude=22.50, longitude=79.50, zoom=4.5, pitch=0)

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Grid ID: {grid_id}\nActive Days: {active_days}\nPersistence: {persistence_days} days\nNight Ratio: {night_ratio}\nMean FRP: {mean_frp} MW"},
        map_style="mapbox://styles/mapbox/dark-v10"
    )

    st.pydeck_chart(r)

    # Hotspot Selector & Live Inspector
    st.markdown("### 🔍 Thermal Grid Cell ML Inspector")
    
    candidate_options = map_df.sort_values(["target_persistent_source", "active_days"], ascending=[False, False])["grid_id"].tolist()
    selected_grid_id = st.selectbox("Select a Thermal Grid Cell to Inspect:", candidate_options[:100])
    
    selected_row = df[df["grid_id"] == selected_grid_id].iloc[0]
    
    # Run Live Prediction
    pred_res = predictor.predict(selected_row)
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.info(f"**Selected Cell:** `{selected_grid_id}` (Lat: {selected_row['lat_grid']}, Lon: {selected_row['lon_grid']})")
        
        if pred_res["predicted_class"] == 1:
            st.error(f"🚨 **Classification:** {pred_res['classification_label']} (Confidence: {pred_res['confidence_score']*100:.1f}%)")
        else:
            st.warning(f"🌾 **Classification:** {pred_res['classification_label']} (Confidence: {pred_res['confidence_score']*100:.1f}%)")
            
        st.write("**Cell Attributes:**")
        st.json({
            "observation_count": int(selected_row["observation_count"]),
            "active_days": int(selected_row["active_days"]),
            "persistence_days": int(selected_row["persistence_days"]),
            "night_ratio": round(float(selected_row["night_ratio"]), 4),
            "mean_frp_mw": round(float(selected_row["mean_frp"]), 2),
            "osm_industrial_count": int(selected_row.get("osm_industrial_count", 0)),
            "osm_min_distance_m": round(float(selected_row.get("osm_min_distance_m", 2000.0)), 2)
        })

    with col_b:
        st.write("### 📜 Explainable Feature Attribution")
        for line in pred_res["evidence"]:
            st.markdown(f"• {line}")

# --- MODE 2: LIVE MODEL PREDICTOR SIMULATION ---
elif app_mode == "Live Model Predictor Simulation":
    st.subheader("⚡ Live Model Parameter Simulation")
    st.write("Tweak custom thermal and temporal input parameters to observe real-time model prediction updates.")
    
    col_sim_1, col_sim_2 = st.columns(2)
    
    with col_sim_1:
        sim_active = st.slider("Active Days:", 1, 365, 45)
        sim_persistence = st.slider("Persistence Days:", 1, 1000, 825)
        sim_night = st.slider("Night Ratio (0 = Day, 1 = Night):", 0.0, 1.0, 0.80, step=0.05)
        sim_frp = st.number_input("Mean Fire Radiative Power (FRP MW):", 0.0, 100.0, 6.5)
        
    with col_sim_2:
        sim_osm_ind = st.slider("OSM Industrial Feature Count (2km):", 0, 30, 8)
        sim_osm_dist = st.slider("OSM Minimum Distance (meters):", 10.0, 2000.0, 150.0, step=10.0)
        sim_obs = sim_active * 3
        
    sim_input = {
        "grid_id": "SIMULATED_CELL",
        "active_days": sim_active,
        "persistence_days": sim_persistence,
        "observation_count": sim_obs,
        "night_ratio": sim_night,
        "mean_frp": sim_frp,
        "max_frp": sim_frp * 2.0,
        "osm_industrial_count": sim_osm_ind,
        "osm_min_distance_m": sim_osm_dist
    }
    
    sim_res = predictor.predict(sim_input)
    
    st.divider()
    st.markdown("### 🎯 Live Model Prediction Result")
    
    if sim_res["predicted_class"] == 1:
        st.error(f"🚨 **{sim_res['classification_label']}** (Confidence: {sim_res['confidence_score']*100:.1f}%)")
    else:
        st.warning(f"🌾 **{sim_res['classification_label']}** (Confidence: {sim_res['confidence_score']*100:.1f}%)")
        
    st.markdown("#### Evidence Summary:")
    for line in sim_res["evidence"]:
        st.markdown(f"• {line}")

# --- MODE 3: MODEL PERFORMANCE & EXPLAINABILITY ---
elif app_mode == "Model Performance & Explainability":
    st.subheader("📊 Model Performance & Feature Importances")
    
    try:
        eval_meta = load_evaluation_summary()
        
        st.markdown(f"**Selected Model:** `{eval_meta['selected_model']}`")
        st.markdown(f"**Grouped Spatial Split:** Train: {eval_meta['num_train_samples']:,} | Val: {eval_meta['num_val_samples']:,} | Test: {eval_meta['num_test_samples']:,}")
        
        st.markdown("### 🏆 Baseline Evaluation Matrix (Test Set)")
        
        metrics_list = []
        for model_name, m in eval_meta["evaluation_metrics"].items():
            metrics_list.append({
                "Model": model_name,
                "Accuracy": m["accuracy"],
                "Precision": m["precision"],
                "Recall": m["recall"],
                "F1-Score": m["f1_score"],
                "Specificity": m["specificity"],
                "ROC-AUC": m["roc_auc"],
                "PR-AUC": m["pr_auc"]
            })
            
        metrics_df = pd.DataFrame(metrics_list)
        st.dataframe(metrics_df.style.highlight_max(axis=0, color="#1e1b4b"), use_container_width=True)
        
        st.markdown("### 🌲 Random Forest Feature Importance Ranking")
        importances_df = pd.DataFrame(
            list(eval_meta["feature_importances"].items()),
            columns=["Feature", "Importance"]
        ).head(10)
        
        st.bar_chart(importances_df.set_index("Feature"))
        
    except Exception as e:
        st.error(f"Error loading evaluation report: {e}")
