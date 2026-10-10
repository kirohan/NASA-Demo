import os
from pathlib import Path

_here = Path(__file__).resolve().parent
if _here.name == 'backend':
    BASE_DIR = _here.parent
else:
    BASE_DIR = _here

DATA_DIR = BASE_DIR / 'data'
BOUNDARIES_DIR = DATA_DIR / 'boundaries'
PROCESSED_DIR = DATA_DIR / 'processed'
RASTERS_DIR = DATA_DIR / 'rasters'
DOCS_DIR = BASE_DIR / 'docs'

# NASA Landsat 8/9 TIRS Band 10 Calibration Constants (USGS OLI/TIRS Calibration)
LANDSAT_K1 = 774.8853    # W / (m² · sr · µm)
LANDSAT_K2 = 1321.0789   # Kelvin
LANDSAT_ML = 0.0003342   # Radiance multiplicative rescaling factor
LANDSAT_AL = 0.1         # Radiance additive rescaling factor
TIRS_WAVELENGTH = 10.895 # Central wavelength in micrometers
PLANCK_RHO = 14388       # h * c / sigma (µm · K)

# Emissivity Parameters (Sobrino et al., 2004 NDVI Threshold Method)
NDVI_SOIL = 0.05
NDVI_VEG = 0.70
EMISSIVITY_SOIL = 0.960
EMISSIVITY_VEG = 0.985
CAVITY_FACTOR = 0.004

# Multi-Criteria Decision Analysis (MCDA) Climate Risk Weights
WEIGHT_HEAT_EXPOSURE = 0.35      # 35% weight: Land Surface Temperature anomaly
WEIGHT_VEGETATION_DEFICIT = 0.25 # 25% weight: Canopy loss / Green deficit
WEIGHT_URBAN_DENSITY = 0.20      # 20% weight: Impervious built-up fraction
WEIGHT_POPULATION_EXPOSURE = 0.20 # 20% weight: WorldPop density exposure

# Cities Center Coordinates & Bounds
# Validated NASA Testbed (Khulna Delta Focus)
CITIES = {
    "khulna": {
        "name": "Khulna Delta, Bangladesh",
        "lat": 22.8456,
        "lon": 89.5403,
        "zoom": 13,
        "bounds": [22.78, 89.48, 22.92, 89.60],
        "deltaic_elevation_m": 3.5,
        "primary_river": "Bhairab / Rupsha River Estuary"
    }
}
