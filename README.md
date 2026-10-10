# SURF — Satellite Urban Resilience Framework
### Official Submission &bull; NASA Space Apps Challenge 2026

[![NASA Earth Data](https://img.shields.io/badge/NASA-Earth%20Observation-blue.svg)](https://earthdata.nasa.gov/)
[![Copernicus Sentinel-2](https://img.shields.io/badge/Copernicus-Sentinel--2-green.svg)](https://dataspace.copernicus.eu/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Leaflet GIS](https://img.shields.io/badge/Leaflet-1.9.4-199900.svg)](https://leafletjs.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

SURF (**Satellite Urban Resilience Framework**) is an open-source, scientifically grounded Earth Observation intelligence platform designed to convert NASA and European remote sensing streams into actionable urban climate resilience decisions for vulnerable global river deltas.

---

## 1. Problem Statement & Deltaic Context
Low-elevation river deltas across the Global South (exemplified by the **Khulna delta** in southwest Bangladesh at 3.5m ASL) are experiencing compound climate stresses:
- **Urban Heat Island (UHI) Amplification:** Widespread replacement of agricultural land and permeable soil with corrugated galvanized iron (tin) roofing and concrete masonry has driven daytime Land Surface Temperatures up by **+4.9°C** over the past decade (2015–2026), reaching extreme local temperatures above **38°C**.
- **Severe Canopy Fragmentation:** Net urban tree canopy has collapsed by **-28.4%**, leaving dense informal and commercial sectors with a **33.9% green space deficit** below World Health Organization (WHO) standards.
- **Tidal Canal & Drainage Encroachment:** Historic tidal retention canals (*khals*) connecting to the Bhairab, Rupsha, and Mayur rivers have been filled for unzoned settlement expansion, eliminating natural convective breeze cooling buffers and escalating compound flood-heat risks.
- **The Municipal Planning Blindspot:** Local authorities (such as Khulna City Corporation (KCC)) have historically lacked accessible, empirical remote sensing tools to identify microclimate hotspots and evaluate mitigation interventions before capital expenditure.

---

## 2. Solution Overview & Technical Innovation
SURF bridges raw multi-spectral satellite imagery and municipal climate action through five core innovations:
1. **Decadal Multi-Sensor Earth Observation Pipeline:** Integrates Landsat 8/9 TIRS thermal radiometry, Copernicus Sentinel-2 MSI multi-spectral surface reflectance, and MODIS decadal climatological baselines.
2. **Reusable Satellite Raster Engine:** Direct ingestion of georeferenced EPSG:4326 32-bit GeoTIFF files (`lst_2026.tif`, `ndvi_2026.tif`, `urban_change.tif`) with real-time browser-side colormapping, opacity blending, and dynamic layer switching.
3. **Transparent Multi-Criteria Decision Analysis (MCDA):** Replaces subjective scoring with an empirically grounded 4-factor risk model:
   $$\text{Risk}_{\text{composite}} = 0.35 \times \text{Thermal Hazard} + 0.25 \times \text{Vegetation Deficit} + 0.20 \times \text{Urban Density} + 0.20 \times \text{Population Exposure}$$
4. **Interactive 2015 ↔ 2026 Time Comparison:** Draggable split-screen swipe curtain with quick-jump baseline chips and real-time metric delta callouts.
5. **Future Scenario Simulator:** Interactive planning simulator allowing municipal planners to test Tree Plantation ($0\text{--}10{,}000$ trees), Cool Roofs ($0\text{--}100\%$), and Wetland Restoration to model thermodynamic cooling and risk reduction before deployment.
6. **Scientific Export Suite:** Generates publication-grade ReportLab PDF Environmental Briefings, EPSG:4326 GeoTIFF rasters, decadal CSV time-series, and 3D Google Earth Pro KML models.

---

## 3. NASA Earth Science Data Usage & Provenance

| Sensor / Dataset | Spectral Band / Product | Spatial Resolution | Temporal Revisit | Primary Function in SURF | Access Point |
|---|---|---|---|---|---|
| **NASA Landsat 8/9 TIRS** | Band 10 ($10.895\,\mu\text{m}$) | 30m (resampled) | 16-day repeat | Radiometric Planck inversion & Sobrino emissivity LST (°C) | [USGS EarthExplorer](https://earthexplorer.usgs.gov/) |
| **Copernicus Sentinel-2 MSI** | Band 4 (Red) & Band 8 (NIR) | 10m Ground Res | 5-day revisit | Level-2A BOA surface reflectance NDVI & Fractional Canopy ($P_v$) | [Copernicus Hub](https://dataspace.copernicus.eu/) |
| **NASA Terra/Aqua MODIS** | MOD11A2 / MYD11A2 | 1,000m Grid | 8-day composite | Decadal thermal climatology baseline calibration | [NASA AppEEARS](https://appeears.earthdatacloud.nasa.gov/) |
| **NASA Terra MODIS** | MOD13Q1 | 250m Grid | 16-day composite | 11-year decadal vegetation trend cross-validation | [NASA LP DAAC](https://lpdaac.usgs.gov/) |
| **NASA NASADEM / SRTM** | 30m Global Elevation | 30m Post | Static Baseline | Deltaic low-elevation plain modeling & tidal vulnerability | [NASA Earthdata](https://earthdata.nasa.gov/) |
| **WorldPop High-Resolution** | 100m Gridded Density | 100m Pixel | Annual Census | Dasymetric demographic exposure weighting | [WorldPop Global](https://www.worldpop.org/) |

---

## 4. System Architecture & Processing Pipeline

```text
+-----------------------------------------------------------------------------------------+
|                               NASA & EUROPEAN SATELLITE STREAMS                         |
|   Landsat 8/9 TIRS (Band 10)  •  Sentinel-2 MSI (B4/B8)  •  MODIS (MOD11A2)  •  NASADEM  |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                                SURF RASTER ENGINE & DATA INGESTION                      |
|           /data/rasters/lst_2026.tif   •   /data/rasters/ndvi_2026.tif                  |
|           /data/rasters/urban_change.tif   •   /data/boundaries/*.geojson               |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                          PHYSICS-BASED RADIOMETRIC PROCESSING                           |
|   • Planck Inversion: Tb = K2 / ln(K1 / L_lambda + 1)                                   |
|   • Sobrino Cavity Emissivity: e = e_v*Pv + e_s*(1-Pv) + C_lambda                       |
|   • Calibrated Single-Channel LST: LST = Tb / [1 + (lambda*Tb / rho)*ln(e)] - 273.15    |
|   • Normalized Difference Ratios: NDVI, NDBI, MNDWI                                     |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                          MULTI-CRITERIA DECISION ANALYSIS (MCDA)                        |
|        Risk = 0.35 * Heat (LST) + 0.25 * Veg (NDVI) + 0.20 * Built-Up + 0.20 * Pop      |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                           FASTAPI REST APPLICATION TIER                                 |
|   /api/raster/*  •  /api/boundaries/*  •  /api/analyze  •  /api/simulate  •  /api/export/* |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                    AEROSPACE MISSION CONTROL GIS DASHBOARD (LEAFLET.JS)                 |
|   • Continuous 2D Raster Overlays        • 2015 ↔ 2026 Swipe Curtain Comparison         |
|   • Satellite Analysis Reticle Mode      • Future Scenario Policy Simulator             |
|   • Interactive Judges Guided Demo Tour  • Multi-Format Export (PDF, GeoTIFF, CSV, KML) |
+-----------------------------------------------------------------------------------------+
```

---

## 5. Platform Features

### A. Satellite Raster Layer System
- **Layer A — Landsat 8/9 LST Heat Raster:** Calibrated surface temperature ($<31^\circ\text{C}$ Blue, $34^\circ\text{C}$ Yellow, $36^\circ\text{C}$ Orange, $>38^\circ\text{C}$ Red).
- **Layer B — Sentinel-2 MSI NDVI Canopy Health:** 10m vegetation index (Water: Blue, Low: Yellow, Moderate: Light Green, Dense: Dark Green).
- **Layer C — Decadal Urban Expansion:** Multi-temporal infill tracking (Pre-2015 Historic Core, 2016–2020 Corridor Infill, 2021–2026 Expansion).
- **Layer D — Composite Climate Risk Layer:** 4-factor MCDA spatial array (Low: Green, Moderate: Yellow, High: Orange, Extreme: Red).

### B. Interactive Decision Support & Storytelling
- **2015 ↔ 2026 Time Comparison Slider:** Synchronized Leaflet `pane2015` with draggable CSS `clip-path` curtain and metric delta chips ($\uparrow +4.9^\circ\text{C}$ Temp, $\downarrow -28.4\%$ Veg, $\uparrow +32.1\%$ Urban).
- **Future Scenario Simulator:** Interactive levers for Tree Plantation ($0\text{--}10{,}000$ trees), Cool Roofs ($0\text{--}100\%$), and Wetland Restoration, updating modeled microclimate metrics in real time.
- **AI Climate Recommendation Panel:** Sector-specific priority ranking with physical justifications (Cool Roofs for tin roofs, Tree Corridors for transit verges, Wetland Setbacks for tidal breezes).
- **Judges Demo Tour:** Automated 4-step guided walk-through highlighting thermal hotspots, canopy depletion, infill envelopes, and policy interventions.
- **Cartographic Tools:** Aerospace North compass arrow, Leaflet metric scale bar, crosshair inspection reticle, and streaming status HUD.

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.9+
- Standard browser (Chrome, Firefox, Edge, Safari)

### Local Setup
```bash
# 1. Clone repository
git clone https://github.com/your-org/SURF-NASA-Space-Apps.git
cd SURF-NASA-Space-Apps

# 2. Install dependencies
pip install fastapi uvicorn numpy pandas shapely reportlab pillow pydantic

# 3. Launch the platform
python3 app.py
```
*The platform will launch on `http://localhost:8000`.*

---

## 7. Interface Layout & Feature Walkthrough

- **Mission Operations Header:** Live ticking UTC clock, orbital sensor telemetry ticker, and action buttons (`Explore SURF Demo`, `Data & Methodology`, `2015 ↔ 2026 Swipe`, `Policy Simulator`, `Export Brief`).
- **Left Panel (GIS Controls):** Basemap tile switcher, Continuous Raster vs. Sampled Point Mesh engine toggle, multi-layer opacity sliders, and calibrated scientific legends.
- **Center Canvas (EO Viewport):** Interactive Leaflet map with North arrow, metric scale bar, draggable comparison curtain, and coordinate telemetry.
- **Right Drawer (Analysis HUD):** Sector identification, Land cover partition bars, Telemetry delta grid, Circular SVG risk gauge, MCDA breakdown, and AI Recommendation panel.

---

## 8. Future Improvements & Scalability

1. **Live NASA STAC Ingestion:** Direct integration with NASA Common Metadata Repository (CMR) STAC API and Copernicus Data Space Ecosystem to pull latest cloud-free scenes on-demand.
2. **Compound Flood-Heat Modeling:** Ingesting real-time tidal gauge telemetry and sea-level projections to model compound coastal hazard indices.
3. **Machine Learning Downscaling:** Super-resolution deep learning to downscale 30m Landsat thermal radiometry to 10m Sentinel-2 spatial grids.
4. **Multilingual Municipal Support:** English and Bengali interface toggle for local municipal planning field officers in Bangladesh.

---

## License & Acknowledgments
Released under the **MIT License**. Grounded in open Earth Science observations provided by the **NASA Earth Science Division** and **European Space Agency Copernicus Programme**. Built for the **NASA Space Apps Challenge 2026**.
