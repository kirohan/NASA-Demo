# SURF — Satellite Urban Resilience Framework

> **A Satellite-Powered Environmental Intelligence & Urban Climate Resilience Platform**  
> *NASA Space Apps Challenge Submission*

---

## 🌍 1. Problem Statement

Cities across the globe are facing severe environmental challenges:
- **Urban Heat Islands (UHI):** Dense concrete structures, asphalt roads, and sparse tree canopies cause urban centers to absorb solar radiation and trap heat, elevating surface temperatures 4°C to 10°C above surrounding rural baselines.
- **Vegetation Canopy Loss:** Rapid expansion strips natural buffers, diminishing shade and natural evapotranspirative cooling.
- **Unplanned Urbanization:** Sprawl encroaches onto wetlands, low-lying floodplains, and peri-urban green corridors.
- **The Information Gap:** City planners, architects, and municipal authorities often lack intuitive, accessible environmental intelligence to make rapid, evidence-grounded adaptation decisions.

---

## 🛰️ 2. The Solution: SURF

**SURF** transforms NASA Earth Observation datasets into an interactive, scientifically defensible decision-support platform. 

Instead of generating speculative climate forecasts, SURF provides actionable intelligence:
> *"Use NASA Earth observation data to understand how a city is changing and identify where climate action is needed."*

---

## 🚀 3. Core Features

### Feature 1: Satellite-Based Urban Heat Map
- **Purpose:** Identify areas suffering acute surface temperature extremes.
- **Data Sources:** NASA Landsat 8/9 Thermal Infrared Sensor (TIRS Band 10) & Terra/Aqua MODIS Land Surface Temperature (MOD11A2).
- **Processing:** Raw Digital Numbers (DN) -> Top-of-Atmosphere (TOA) Radiance -> Brightness Temperature (Planck inversion) -> NDVI-based surface emissivity (Sobrino et al. 2004) -> Calibrated Land Surface Temperature (LST, °C).
- **Risk Categorization:** Low (<28°C), Moderate (28-34°C), High (34-40°C), Extreme (>40°C).
- **Output:** Interactive spatial heat risk grid with UHI anomaly calculations.

### Feature 2: Vegetation Health & Canopy Density Analysis
- **Purpose:** Measure green coverage, canopy distribution, and vegetative cooling capacity.
- **Formulation:** Standardized Normalized Difference Vegetation Index: `NDVI = (NIR - RED) / (NIR + RED)`.
- **Classification:**
  - 0.8 – 1.0: Dense Vegetation
  - 0.4 – 0.8: Moderate Vegetation
  - 0.0 – 0.4: Low Vegetation (built-up, bare soil)
  - < 0.0: Water Bodies
- **Output:** Vegetation canopy deficit percentage and Fractional Vegetation Cover (FVC).

### Feature 3: Multi-Temporal Urban Change Detection
- **Purpose:** Quantify decadal urban transitions between historical and recent observations (2015 vs. 2025).
- **Metrics:** Normalized Difference Built-up Index (NDBI) and delta-NDVI.
- **Detection:**
  - Urban built-up expansion (e.g., +35.2%)
  - Canopy deforestation / loss (e.g., -18.4%)
  - Surface water body alterations
- **Output:** Spatial change classification map (Urban Expansion, Vegetation Loss, Greening Gain, Stable Urban).

### Feature 4: Climate Resilience & Vulnerability Score (MCDA Model)
- **Scoring Model:** Multi-Criteria Decision Analysis (0–100 risk scale) combining:
  1. Surface Temperature Anomaly (Weight: 30%)
  2. Vegetation Canopy Deficit (Weight: 25%)
  3. Built-Up Density / NDBI (Weight: 20%)
  4. Population Exposure Density (Weight: 15%)
  5. Topographic / Elevation Profile via NASADEM (Weight: 10%)
- **Output:** Composite Climate Risk Score (e.g., 82/100, Extreme Risk) and attribution breakdown.

### Feature 5: AI-Driven Actionable Recommendations
- **Purpose:** Context-aware urban adaptation strategies based on localized environmental thresholds.
- **Key Interventions:**
  1. **Deploy Cool Roofs & High-Albedo Coatings:** Target high-heat commercial and residential roofs.
  2. **Expand Urban Green Canopies & Pocket Forests:** Plant shade trees and pocket forests (Miyawaki method) in low-NDVI wards.
  3. **Preserve Mature Canopy & Wetlands:** Enforce anti-encroachment perimeters around existing urban water bodies.
  4. **Incentivize Albedo-Optimized Rooftop Solar:** Pair rooftop photovoltaics with reflective coatings.
  5. **Construct Permeable Pavements & Bioswales:** Enhance stormwater percolation and evaporative cooling.
- **NASA Verification:** Each action includes a verified NASA satellite monitoring metric to measure long-term progress.

---

## 🛰️ 4. NASA Data Integration

| NASA Mission / Product | Sensor / Platform | Spatial / Temporal Resolution | Platform Role |
| :--- | :--- | :--- | :--- |
| **Landsat 8/9 Collection 2** | TIRS Band 10 | 30m / 16-day | Land Surface Temperature (LST) derivation |
| **Landsat 8/9 OLI** | OLI Bands 4, 5, 6 | 30m / 16-day | NDVI canopy health and NDBI built-up mapping |
| **MOD11A2 / MYD11A2** | MODIS (Terra/Aqua) | 1km / 8-day | Large-scale LST and Surface Urban Heat Island (SUHI) |
| **MOD13Q1** | MODIS (Terra) | 250m / 16-day | Time-series vegetation dynamics |
| **NASADEM_NC.001** | SRTM / NASADEM | 30m / Static | Elevation and topographic heat-trapping analysis |
| **NASA AppEEARS** | LP DAAC Cloud API | Point & Area Extraction | Automated data ingestion pipeline |
| **NASA Giovanni** | Web Service | Multi-Sensor | Ambient air temperature and precipitation validation |

---

## 🏛️ 5. System Architecture

```
                    NASA Earth Observations
         (Landsat 8/9 • MODIS • NASADEM • AppEEARS)
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │          SURF Backend (FastAPI)              │
     │                                              │
     │  • LandsatProcessor (Planck / Sobrino LST)   │
     │  • ModisProcessor (MOD11A2 / MOD13Q1)        │
     │  • NdviAnalyzer (Canopy Health & FVC)        │
     │  • UrbanChangeDetector (Decadal NDBI/NDVI)   │
     │  • ClimateRiskModel (MCDA 0-100 Scoring)     │
     │  • RecommendationEngine (Adaptive Actions)   │
     └──────────────────────┬───────────────────────┘
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │          SURF Frontend Web Dashboard         │
     │                                              │
     │  • Leaflet.js Interactive GIS Mapping        │
     │  • Dynamic Layers: Heat, NDVI, Change, Wards │
     │  • Telemetry Metrics & Risk Score Radial     │
     │  • Decadal Trajectory Trends (Chart.js)      │
     │  • Actionable Policy & Planning Interventions│
     └──────────────────────────────────────────────┘
```

---

## 🛠️ 6. Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic
- **Geospatial & Analysis:** NumPy, Pandas, GeoPandas, Rasterio, Shapely, Scikit-learn
- **Frontend Dashboard:** HTML5, CSS3 Glassmorphism, Vanilla JavaScript
- **Mapping & GIS:** Leaflet.js, CartoDB Dark Matter, GeoJSON vectors
- **Visualization:** Chart.js, FontAwesome Icons

---

## ⚡ 7. Quickstart & Installation

```bash
# 1. Clone repository
git clone https://github.com/nasa-space-apps/SURF.git
cd SURF

# 2. Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python app.py
```
Open **http://localhost:8000** in your web browser. (API Docs at `http://localhost:8000/docs`).

---

## 🔬 8. Scientific Limitations & Governance

SURF is strictly designed as a decision-support platform:
1. **No Deterministic Weather Forecasts:** SURF does not claim to predict exact daily temperatures or future rainfall events.
2. **Satellite-Derived Indicators:** All metrics represent satellite-derived environmental indicators based on NASA Earth observations.
3. **Estimated Environmental Impact:** Recommended cooling potentials represent estimated equilibrium ranges derived from peer-reviewed urban climate literature.

---

## 👥 9. NASA Space Apps Challenge Team

- **Lead Remote Sensing & EO Researcher**
- **GIS & Geospatial Systems Engineer**
- **Full-Stack & Cloud Architecture Developer**
- **AI & Urban Resilience Product Architect**

*Built for the NASA International Space Apps Challenge.*
