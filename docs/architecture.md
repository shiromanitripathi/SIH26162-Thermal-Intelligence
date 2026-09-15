# Technical Architecture & Methodology Overview

**Project:** SIH26162 - AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources  
**Organization:** National Technical Research Organisation (NTRO)  

---

## 1. System Vision

The primary objective of this system is to enhance satellite-detected thermal anomaly data (from NASA FIRMS) with spatial, temporal, and contextual intelligence to differentiate industrial fires and static/persistent thermal emitters from non-industrial thermal anomalies (e.g. agricultural burning, forest fires, vegetation fires).

---

## 2. Core Subsystems

### 2.1 Data Ingestion Subsystem (`src/data/`)
- **NASA FIRMS API Connector:** Fetches near-real-time active fire / thermal anomaly data (VIIRS / MODIS).
- **OpenStreetMap Data Pipeline:** Queries OSM infrastructure, POIs, industrial land-use zones, and facility footprints via Overpass API / Geofabrik extracts.
- **Auxiliary Satellite Data Interface:** Ingests elevation, land-cover/land-use (LULC), and satellite spectral imagery features.

### 2.2 Geospatial Engine (`src/geospatial/`)
- Coordinate reference system (CRS) projection management (e.g., EPSG:4326 to localized UTM zones).
- Spatial indexing (R-tree / Quadtree via GeoPandas / Shapely) for spatial joins.
- Proximity calculations and distance buffering around industrial assets and OSM infrastructure.

### 2.3 Feature Engineering Pipeline (`src/features/`)
- **Thermal Signal Features:** Fire Radiative Power (FRP), Brightness Temperature, day/night flags, detection confidence.
- **Temporal Persistence Features:** Multi-day observation frequency, recurrence rate over sliding temporal windows.
- **Spatial Clustering Features:** Spatial point density (DBSCAN / HDBSCAN) and cluster radius.
- **Contextual Infrastructure Features:** Distance to nearest industrial plant, refinery, power plant, cement kiln, or flared gas stack.

### 2.4 ML Classification Module (`src/models/`)
- Model training routines supporting tabular and spatial-temporal classifier architectures.
- Experiment tracking and metric logging.
- Model evaluation with spatial cross-validation strategies to prevent spatial autocorrelation leakage.
- Inference pipeline exporting classified hotspots with confidence scores and feature attribution.

---

## 3. Technology Stack

| Layer | Component |
|---|---|
| **Language** | Python 3.10+ |
| **Data Processing** | NumPy, Pandas |
| **Geospatial Processing** | GeoPandas, Shapely, PyProj, Rasterio |
| **Machine Learning** | Scikit-Learn (Future experimentation with XGBoost, LightGBM, Random Forest, etc.) |
| **Visualization & EDA** | Matplotlib, Seaborn, Jupyter |
| **Environment Management** | `python-dotenv`, Python `.venv` |
