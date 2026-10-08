# SURF System Architecture v2.5
Decoupled geospatial framework:
1. **NASA Earth Observation Engine** (Landsat TIRS, MODIS, NASADEM, AppEEARS)
2. **FastAPI Spatial Backend** (`/api/layers/temporal`, `/api/export/kml`, `/api/analyze`)
3. **Interactive Decision-Support GIS Frontend** (Leaflet.js, Leaflet.heat, Google Hybrid Satellite, OSM)
4. **Google Earth Pro 3D Companion Integration** (.kml exporter)
