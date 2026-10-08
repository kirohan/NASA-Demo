"""
SURF — Satellite Urban Resilience Framework
Configuration & Parameter Registry
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
GEOJSON_DIR = DATA_DIR / "sample_geojson"
DOCS_DIR = BASE_DIR / "docs"

APP_NAME = "SURF — Satellite Urban Resilience Framework"
APP_VERSION = "2.5.0 (Historical Timeline & Smooth GIS Edition)"
APP_DESCRIPTION = "A satellite-powered environmental intelligence platform transforming NASA Earth Observations into actionable urban climate resilience insights."

HOST = os.getenv("SURF_HOST", "0.0.0.0")
PORT = int(os.getenv("SURF_PORT", 8000))
DEBUG = os.getenv("SURF_DEBUG", "True").lower() in ("true", "1", "yes")

EARTHDATA_USERNAME = os.getenv("EARTHDATA_USERNAME", "")
EARTHDATA_PASSWORD = os.getenv("EARTHDATA_PASSWORD", "")
EARTHDATA_TOKEN = os.getenv("EARTHDATA_TOKEN", "")
APPEEARS_API_URL = "https://appeears.earthdatacloud.nasa.gov/api"

DEMO_MODE = os.getenv("SURF_DEMO_MODE", "True").lower() in ("true", "1", "yes")

LANDSAT_TIRS = {"BAND_10": {"M_L": 0.0003342, "A_L": 0.1, "K1": 774.8853, "K2": 1321.0789, "WAVELENGTH_UM": 10.895}}
PHYSICAL_CONSTANTS = {"BOLTZMANN_C2": 0.014388, "EMISSIVITY_SOIL": 0.965, "EMISSIVITY_VEG": 0.985, "EMISSIVITY_WATER": 0.991, "EMISSIVITY_BUILDING": 0.950}
NDVI_CLASSES = {"WATER": (-1.0, 0.0), "BUILT_UP_BARE": (0.0, 0.2), "LOW_VEGETATION": (0.2, 0.4), "MODERATE_VEGETATION": (0.4, 0.7), "DENSE_VEGETATION": (0.7, 1.0)}
HEAT_RISK_THRESHOLDS = {"LOW": (0.0, 28.0), "MODERATE": (28.0, 34.0), "HIGH": (34.0, 40.0), "EXTREME": (40.0, 65.0)}
RISK_WEIGHTS: Dict[str, float] = {"surface_temperature": 0.30, "vegetation_deficit": 0.25, "built_up_density": 0.20, "population_density": 0.15, "elevation_vulnerability": 0.10}

SUPPORTED_CITIES = [
    {"id": "khulna", "name": "Khulna", "country": "Bangladesh", "lat": 22.8456, "lng": 89.5403, "zoom": 13, "baseline_lst": 36.4, "baseline_ndvi": 0.24, "baseline_risk": 78},
    {"id": "dhaka", "name": "Dhaka", "country": "Bangladesh", "lat": 23.8103, "lng": 90.4125, "zoom": 12, "baseline_lst": 38.5, "baseline_ndvi": 0.18, "baseline_risk": 82},
    {"id": "phoenix", "name": "Phoenix", "country": "United States", "lat": 33.4484, "lng": -112.0740, "zoom": 11, "baseline_lst": 44.8, "baseline_ndvi": 0.12, "baseline_risk": 89},
    {"id": "nairobi", "name": "Nairobi", "country": "Kenya", "lat": -1.2921, "lng": 36.8219, "zoom": 12, "baseline_lst": 31.4, "baseline_ndvi": 0.35, "baseline_risk": 58},
    {"id": "cairo", "name": "Cairo", "country": "Egypt", "lat": 30.0444, "lng": 31.2357, "zoom": 11, "baseline_lst": 41.2, "baseline_ndvi": 0.09, "baseline_risk": 86}
]
