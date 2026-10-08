# SURF System Architecture & Data Engineering Pipeline

**SURF: Satellite Urban Resilience Framework**  
*NASA Space Apps Challenge*

---

## System Overview
SURF comprises three primary layers:
1. **NASA Earth Observation Ingestion Layer** (Landsat TIRS, MODIS, NASADEM, AppEEARS)
2. **Environmental Intelligence Engine** (FastAPI, NumPy, Rasterio, GeoPandas, Scikit-Learn)
3. **Interactive Decision-Support Web Dashboard** (HTML5, Leaflet.js, Chart.js, Glassmorphic CSS)

## API Endpoints
- `GET /api/health`: System health and NASA Earthdata readiness
- `GET /api/cities`: List of curated urban centers
- `GET /api/layers/heat`: GeoJSON grid of Land Surface Temperature (LST)
- `GET /api/layers/vegetation`: GeoJSON grid of NDVI vegetation health
- `GET /api/layers/urban-change`: GeoJSON grid of 2015-2025 urban dynamics
- `POST /api/analyze`: Full environmental intelligence assessment
- `GET /api/geojson/{file}`: Sample administrative boundaries (e.g. Dhaka wards)
