"""
SURF — Satellite Urban Resilience Framework
FastAPI Web Application & Environmental Intelligence API Gateway
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, SUPPORTED_CITIES,
    GEOJSON_DIR, BASE_DIR, DEMO_MODE, PORT, DEBUG
)
from core.satellite.landsat import LandsatProcessor
from core.satellite.modis import ModisProcessor
from core.satellite.appeears import AppEEARSClient
from core.analysis.heat_analysis import HeatAnalyzer
from core.analysis.ndvi_analysis import NdviAnalyzer
from core.analysis.urban_change import UrbanChangeDetector
from core.analysis.risk_model import ClimateRiskModel
from core.recommendation.engine import RecommendationEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SURF")

app = FastAPI(title=APP_NAME, version=APP_VERSION, description=APP_DESCRIPTION, docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

landsat_proc = LandsatProcessor()
modis_proc = ModisProcessor()
appeears_client = AppEEARSClient()
heat_analyzer = HeatAnalyzer()
ndvi_analyzer = NdviAnalyzer()
change_detector = UrbanChangeDetector()
risk_model = ClimateRiskModel()
rec_engine = RecommendationEngine()

class AnalysisRequest(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")
    city_id: Optional[str] = Field(None, description="City identifier")
    year_start: int = Field(2015, description="Baseline comparison year")
    year_end: int = Field(2026, description="Recent observation year")

def get_or_create_satellite_data(lat: float, lng: float, year: int = 2026, seed_offset: int = 0) -> Dict[str, Any]:
    seed = int(abs(lat * 1000 + lng * 1000)) % 10000 + seed_offset
    scene_curr = LandsatProcessor.generate_synthetic_scene(shape=(64, 64), year=year, seed=seed)
    lst_array, ndvi_array, emissivity = landsat_proc.compute_lst(
        scene_curr["band10_dn"], scene_curr["red"], scene_curr["nir"]
    )

    scene_base = LandsatProcessor.generate_synthetic_scene(shape=(64, 64), year=2015, seed=seed + 101)
    lst_base, ndvi_base, _ = landsat_proc.compute_lst(
        scene_base["band10_dn"], scene_base["red"], scene_base["nir"]
    )

    ndbi_curr = UrbanChangeDetector.compute_ndbi(scene_curr["red"] * 1.35, scene_curr["nir"])
    ndbi_base = UrbanChangeDetector.compute_ndbi(scene_base["red"] * 1.10, scene_base["nir"])

    return {
        "lst_array": lst_array,
        "ndvi_array": ndvi_array,
        "emissivity": emissivity,
        "river_mask": scene_curr["river_mask"],
        "ndvi_base": ndvi_base,
        "ndbi_base": ndbi_base,
        "ndbi_curr": ndbi_curr,
        "year": year
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "demo_mode": DEMO_MODE,
        "nasa_appeears_ready": appeears_client.authenticate()
    }

@app.get("/api/cities")
def list_supported_cities():
    return {"cities": SUPPORTED_CITIES}

@app.get("/api/layers/temporal")
def get_temporal_layer(
    year: int = Query(2026, ge=2015, le=2026, description="Observation year"),
    lat: float = Query(22.8456, description="Center latitude"),
    lng: float = Query(89.5403, description="Center longitude"),
    city_id: Optional[str] = Query("khulna", description="City ID")
):
    """
    Returns year-specific satellite heat, vegetation, and risk telemetry for the time-slider.
    """
    sat = get_or_create_satellite_data(lat, lng, year=year)
    heat_stats = heat_analyzer.analyze_raster(sat["lst_array"], river_mask=sat["river_mask"])
    ndvi_stats = ndvi_analyzer.analyze_raster(sat["ndvi_array"], river_mask=sat["river_mask"])

    # High-density heat points for smooth Leaflet.heat rendering
    smooth_heat = heat_analyzer.generate_smooth_heat_data(
        lat, lng, sat["lst_array"], river_mask=sat["river_mask"], grid_size_km=10.0
    )
    veg_geojson = ndvi_analyzer.generate_grid_geojson(
        lat, lng, sat["ndvi_array"], river_mask=sat["river_mask"], grid_size_km=10.0, subdivisions=16
    )

    mean_lst = heat_stats["mean_temperature_c"]
    mean_ndvi = ndvi_stats["mean_ndvi"]
    mean_ndbi = float(np.mean(sat["ndbi_curr"]))

    # Temporal land cover fractions
    time_frac = (year - 2015) / 11.0
    built_up_pct = round(42.0 + time_frac * 34.0 + mean_ndbi * 20.0, 1)
    green_pct = round(max(10.0, ndvi_stats["green_coverage_pct"]), 1)
    water_pct = round(max(3.0, 100.0 - built_up_pct - green_pct), 1)

    risk_output = risk_model.compute_composite_risk(
        surface_temp_c=mean_lst,
        ndvi=mean_ndvi,
        ndbi=mean_ndbi,
        pop_density=22000.0 if city_id == "khulna" else 30000.0,
        elevation_m=3.8 if city_id == "khulna" else 8.5,
        ward_id=f"{city_id.capitalize()} ({year})"
    )

    return {
        "year": year,
        "thermal_intelligence": heat_stats,
        "vegetation_intelligence": ndvi_stats,
        "resilience_and_risk": risk_output,
        "heat_points": smooth_heat["heat_points"],
        "heat_geojson": smooth_heat["geojson"],
        "veg_geojson": veg_geojson,
        "map_area_intelligence": {
            "total_area_sqkm": 100.0,
            "total_area_hectares": 10000.0,
            "built_up_area_sqkm": round(100.0 * (built_up_pct / 100.0), 2),
            "built_up_pct": built_up_pct,
            "green_canopy_sqkm": round(100.0 * (green_pct / 100.0), 2),
            "green_canopy_pct": green_pct,
            "water_body_sqkm": round(100.0 * (water_pct / 100.0), 2),
            "water_body_pct": water_pct
        }
    }

@app.post("/api/analyze")
def run_full_environmental_analysis(payload: AnalysisRequest):
    sat = get_or_create_satellite_data(payload.lat, payload.lng, year=payload.year_end)
    heat_stats = heat_analyzer.analyze_raster(sat["lst_array"], river_mask=sat["river_mask"])
    ndvi_stats = ndvi_analyzer.analyze_raster(sat["ndvi_array"], river_mask=sat["river_mask"])
    change_stats = change_detector.detect_changes(
        sat["ndvi_base"], sat["ndvi_array"], sat["ndbi_base"], sat["ndbi_curr"],
        year_t1=payload.year_start, year_t2=payload.year_end
    )

    city_match = next((c for c in SUPPORTED_CITIES if c["id"] == payload.city_id), None)
    pop_density = 24000.0 if not city_match else (22000.0 if city_match["id"] == "khulna" else 32000.0)
    elevation = 3.8 if (city_match and city_match["id"] == "khulna") else (8.5 if (city_match and city_match["id"] == "dhaka") else 10.0)

    mean_lst = heat_stats["mean_temperature_c"]
    mean_ndvi = ndvi_stats["mean_ndvi"]
    mean_ndbi = float(np.mean(sat["ndbi_curr"]))

    risk_output = risk_model.compute_composite_risk(
        surface_temp_c=mean_lst,
        ndvi=mean_ndvi,
        ndbi=mean_ndbi,
        pop_density=pop_density,
        elevation_m=elevation,
        ward_id=city_match["name"] if city_match else f"Area ({payload.lat:.3f}, {payload.lng:.3f})"
    )

    recommendations = rec_engine.generate_recommendations(
        surface_temp_c=mean_lst,
        ndvi=mean_ndvi,
        ndbi=mean_ndbi,
        risk_level=risk_output["risk_level"],
        built_up_change_pct=change_stats["metrics"]["built_up_change_pct"],
        veg_change_pct=change_stats["metrics"]["vegetation_change_pct"]
    )

    temporal_trends = ModisProcessor.simulate_temporal_trend(
        base_lst=mean_lst - 3.4,
        base_ndvi=mean_ndvi + 0.16,
        years=list(range(2015, 2027))
    )

    total_area_sqkm = 100.0
    total_area_ha = 10000.0
    built_up_pct = max(10.0, min(85.0, 52.0 + mean_ndbi * 65.0))
    green_pct = ndvi_stats.get("green_coverage_pct", 26.0)
    water_pct = max(3.0, round(100.0 - built_up_pct - green_pct, 1))

    map_area_stats = {
        "total_area_sqkm": round(total_area_sqkm, 2),
        "total_area_hectares": round(total_area_ha, 1),
        "built_up_area_sqkm": round(total_area_sqkm * (built_up_pct / 100.0), 2),
        "built_up_pct": round(built_up_pct, 1),
        "green_canopy_sqkm": round(total_area_sqkm * (green_pct / 100.0), 2),
        "green_canopy_pct": round(green_pct, 1),
        "water_body_sqkm": round(total_area_sqkm * (water_pct / 100.0), 2),
        "water_body_pct": round(water_pct, 1)
    }

    return {
        "map_area_intelligence": map_area_stats,
        "location": {
            "latitude": payload.lat,
            "longitude": payload.lng,
            "city_id": payload.city_id,
            "city_name": city_match["name"] if city_match else "Custom Location",
            "country": city_match["country"] if city_match else "Bangladesh"
        },
        "thermal_intelligence": heat_stats,
        "vegetation_intelligence": ndvi_stats,
        "change_detection": change_stats,
        "resilience_and_risk": risk_output,
        "recommendations": recommendations,
        "temporal_trends": temporal_trends
    }

@app.get("/api/layers/urban-change")
def get_urban_change_layer(
    lat: float = Query(22.8456, description="Center latitude"),
    lng: float = Query(89.5403, description="Center longitude"),
    grid_km: float = Query(10.0, description="Bounding extent in kilometers")
):
    sat = get_or_create_satellite_data(lat, lng, year=2026)
    grid_geojson = change_detector.generate_change_geojson(
        lat, lng, sat["ndvi_base"], sat["ndvi_array"], sat["ndbi_base"], sat["ndbi_curr"],
        river_mask=sat["river_mask"], grid_size_km=grid_km, subdivisions=16
    )
    summary = change_detector.detect_changes(
        sat["ndvi_base"], sat["ndvi_array"], sat["ndbi_base"], sat["ndbi_curr"],
        year_t1=2015, year_t2=2026
    )
    return {"summary": summary, "geojson": grid_geojson}

@app.get("/api/export/kml")
def export_google_earth_kml(
    lat: float = Query(22.8456, description="Center latitude"),
    lng: float = Query(89.5403, description="Center longitude"),
    city_id: Optional[str] = Query("khulna", description="City ID")
):
    sat = get_or_create_satellite_data(lat, lng, year=2026)
    heat_stats = heat_analyzer.analyze_raster(sat["lst_array"], river_mask=sat["river_mask"])
    ndvi_stats = ndvi_analyzer.analyze_raster(sat["ndvi_array"], river_mask=sat["river_mask"])
    city_name = "Khulna" if city_id == "khulna" else ("Dhaka" if city_id == "dhaka" else f"Area_{lat:.3f}_{lng:.3f}")

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>SURF — {city_name} 3D Environmental Intelligence</name>
    <description>Satellite Urban Resilience Framework (NASA Space Apps Challenge)</description>
    
    <Style id="extremeHeat"><PolyStyle><color>990000ff</color><outline>1</outline></PolyStyle><LineStyle><color>ff0000ff</color><width>1.5</width></LineStyle></Style>
    <Style id="highHeat"><PolyStyle><color>990066ff</color><outline>1</outline></PolyStyle><LineStyle><color>ff0066ff</color><width>1.5</width></LineStyle></Style>
    <Style id="moderateHeat"><PolyStyle><color>9900ccff</color><outline>1</outline></PolyStyle><LineStyle><color>ff00ccff</color><width>1.5</width></LineStyle></Style>
    
    <Folder>
      <name>Summary: {city_name}</name>
      <Placemark>
        <name>{city_name} Core</name>
        <description><![CDATA[
          <h2>SURF Environmental Intelligence</h2>
          <p><b>Mean Surface Temperature:</b> {heat_stats['mean_temperature_c']} °C<br/>
          <b>UHI Anomaly:</b> +{heat_stats['uhi_intensity_c']} °C<br/>
          <b>Vegetation Health (NDVI):</b> {ndvi_stats['mean_ndvi']}<br/>
          <b>Canopy Deficit:</b> {ndvi_stats['vegetation_deficit_pct']}%<br/>
          <b>Total Area:</b> 100.0 km² (10,000 hectares)</p>
        ]]></description>
        <Point><coordinates>{lng},{lat},0</coordinates></Point>
      </Placemark>
    </Folder>

    <Folder>
      <name>Thermal Stress Grid (Clipped for Rivers)</name>
"""
    rows, cols = sat["lst_array"].shape
    d_lat = (10.0 / 111.0) / 8
    d_lng = (10.0 / (111.0 * np.cos(np.radians(lat)))) / 8
    start_lat = lat - 4 * d_lat
    start_lng = lng - 4 * d_lng

    for i in range(8):
        for j in range(8):
            r_idx = min(rows - 1, i * (rows // 8))
            c_idx = min(cols - 1, j * (cols // 8))
            if sat["river_mask"][r_idx, c_idx]:
                continue
            val = float(sat["lst_array"][r_idx, c_idx])
            style_id = "extremeHeat" if val >= 38.0 else ("highHeat" if val >= 34.0 else "moderateHeat")
            min_lat, max_lat = start_lat + i * d_lat, start_lat + (i + 1) * d_lat
            min_lng, max_lng = start_lng + j * d_lng, start_lng + (j + 1) * d_lng

            kml += f"""      <Placemark>
        <name>LST [{i},{j}] ({val:.1f} °C)</name>
        <styleUrl>#{style_id}</styleUrl>
        <description><![CDATA[<b>Surface Temp:</b> {val:.1f} °C<br/><b>Cell Size:</b> ~1.56 km² (156 ha)]]></description>
        <Polygon><outerBoundaryIs><LinearRing><coordinates>{min_lng},{min_lat},0 {max_lng},{min_lat},0 {max_lng},{max_lat},0 {min_lng},{max_lat},0 {min_lng},{min_lat},0</coordinates></LinearRing></outerBoundaryIs></Polygon>
      </Placemark>
"""
    kml += """    </Folder>
  </Document>
</kml>"""

    return Response(
        content=kml,
        media_type="application/vnd.google-earth.kml+xml",
        headers={"Content-Disposition": f"attachment; filename=SURF_{city_name}_GoogleEarth.kml"}
    )

@app.get("/api/geojson/{filename}")
def serve_sample_geojson(filename: str):
    file_path = GEOJSON_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"GeoJSON file {filename} not found.")
    return FileResponse(file_path, media_type="application/geo+json")

frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def serve_frontend_dashboard():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"), status_code=200)
        return HTMLResponse(content="<h1>SURF Frontend Not Found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    print(f"Starting {APP_NAME} on http://localhost:{PORT}...")
    uvicorn.run("app:app", host="127.0.0.1", port=PORT, reload=DEBUG)
