"""
NASA Landsat 8/9 TIRS Processing Pipeline
Calculates Top-of-Atmosphere (TOA) Spectral Radiance, At-Sensor Brightness Temperature,
Land Surface Emissivity (LSE) via Sobrino NDVI Threshold Method, Calibrated LST,
and Continuous 2D Geospatial Thermal Raster Generation with GeoTIFF file ingestion.
"""
import io
import os
from pathlib import Path
import numpy as np
from PIL import Image

try:
    from ..config import (
        LANDSAT_K1, LANDSAT_K2, LANDSAT_ML, LANDSAT_AL,
        TIRS_WAVELENGTH, PLANCK_RHO,
        NDVI_SOIL, NDVI_VEG, EMISSIVITY_SOIL, EMISSIVITY_VEG, CAVITY_FACTOR,
        RASTERS_DIR
    )
except (ImportError, ValueError):
    try:
        from backend.config import (
            LANDSAT_K1, LANDSAT_K2, LANDSAT_ML, LANDSAT_AL,
            TIRS_WAVELENGTH, PLANCK_RHO,
            NDVI_SOIL, NDVI_VEG, EMISSIVITY_SOIL, EMISSIVITY_VEG, CAVITY_FACTOR,
            RASTERS_DIR
        )
    except (ImportError, ValueError):
        from config import (
            LANDSAT_K1, LANDSAT_K2, LANDSAT_ML, LANDSAT_AL,
            TIRS_WAVELENGTH, PLANCK_RHO,
            NDVI_SOIL, NDVI_VEG, EMISSIVITY_SOIL, EMISSIVITY_VEG, CAVITY_FACTOR,
            RASTERS_DIR
        )

def compute_toa_radiance(dn_val, ml=LANDSAT_ML, al=LANDSAT_AL):
    """Convert raw Digital Number (DN) to TOA spectral radiance L_lambda (W/(m²·sr·µm))."""
    return (ml * dn_val) + al

def compute_brightness_temperature(radiance, k1=LANDSAT_K1, k2=LANDSAT_K2):
    """Invert Planck's radiation equation to obtain at-sensor brightness temperature (K)."""
    radiance = max(radiance, 0.001)
    return k2 / np.log((k1 / radiance) + 1.0)

def compute_emissivity_from_ndvi(ndvi):
    """
    Calculate Land Surface Emissivity (LSE) using the Sobrino et al. (2004) NDVI threshold method.
    - Water (NDVI < 0): e = 0.991
    - Bare Soil (NDVI < NDVI_SOIL): e = EMISSIVITY_SOIL
    - Fully Vegetated (NDVI > NDVI_VEG): e = EMISSIVITY_VEG + CAVITY_FACTOR
    - Mixed Urban/Vegetation: e = e_veg * Pv + e_soil * (1 - Pv) + C
    """
    if ndvi < 0:
        return 0.991
    elif ndvi < NDVI_SOIL:
        return EMISSIVITY_SOIL
    elif ndvi > NDVI_VEG:
        return EMISSIVITY_VEG + CAVITY_FACTOR
    else:
        pv = ((ndvi - NDVI_SOIL) / (NDVI_VEG - NDVI_SOIL)) ** 2
        c_lambda = (1.0 - EMISSIVITY_SOIL) * EMISSIVITY_VEG * 0.55 * (1.0 - pv)
        return (EMISSIVITY_VEG * pv) + (EMISSIVITY_SOIL * (1.0 - pv)) + c_lambda

def compute_lst_celsius(tb_kelvin, emissivity, wavelength=TIRS_WAVELENGTH):
    """
    Calculate split-window / single-channel Land Surface Temperature in Celsius.
    Formula: LST = Tb / [1 + (lambda * Tb / rho) * ln(emissivity)] - 273.15
    """
    emissivity = max(emissivity, 0.90)
    lst_kelvin = tb_kelvin / (1.0 + ((wavelength * tb_kelvin / PLANCK_RHO) * np.log(emissivity)))
    return round(lst_kelvin - 273.15, 2)

def generate_lst_point_dataset(center_lat, center_lon, base_temp=35.0, year=2026, count=40):
    """
    Generates realistic, physically-grounded LST observation points for raster/heatmap rendering.
    Takes into account urban warming trend (+0.42°C/year since 2015 baseline) and river cooling.
    """
    year_delta = (year - 2015) * 0.41
    points = []
    np.random.seed(int(year * 100 + 42))
    
    for _ in range(count):
        dlat = np.random.uniform(-0.05, 0.05)
        dlon = np.random.uniform(-0.04, 0.05)
        lat = center_lat + dlat
        lon = center_lon + dlon
        
        dist_river = abs(lon - 89.570)
        cooling = max(0, (0.015 - dist_river) * 120.0)
        
        dist_center = np.sqrt(dlat**2 + dlon**2)
        urban_warming = max(0, (0.035 - dist_center) * 80.0)
        
        t = base_temp + year_delta + urban_warming - cooling + np.random.uniform(-0.5, 0.5)
        t = round(float(t), 1)
        
        intensity = min(1.0, max(0.1, (t - 28.0) / 14.0))
        points.append([round(lat, 5), round(lon, 5), round(intensity, 3), t])
        
    return points

def colormap_lst_to_rgba(lst_arr):
    """
    Applies strict Phase 2 scientific color ramp:
    - < 31°C  -> Blue (#0077be)
    - 34°C    -> Yellow (#fee08b)
    - 36°C    -> Orange (#fc8d59)
    - > 38°C  -> Red (#d73027)
    """
    rows, cols = lst_arr.shape
    r = np.zeros((rows, cols), dtype=np.uint8)
    g = np.zeros((rows, cols), dtype=np.uint8)
    b = np.zeros((rows, cols), dtype=np.uint8)
    a = np.full((rows, cols), 220, dtype=np.uint8)

    # 1. Below 31°C: Solid Blue
    m_cold = lst_arr < 31.0
    r[m_cold], g[m_cold], b[m_cold] = 0, 119, 190

    # 2. 31°C to 34°C: Blue -> Yellow
    m_by = (lst_arr >= 31.0) & (lst_arr < 34.0)
    t_by = (lst_arr[m_by] - 31.0) / 3.0
    r[m_by] = (0 + t_by * 254).astype(np.uint8)
    g[m_by] = (119 + t_by * (224 - 119)).astype(np.uint8)
    b[m_by] = (190 - t_by * (190 - 139)).astype(np.uint8)

    # 3. 34°C to 36°C: Yellow -> Orange
    m_yo = (lst_arr >= 34.0) & (lst_arr < 36.0)
    t_yo = (lst_arr[m_yo] - 34.0) / 2.0
    r[m_yo] = (254 - t_yo * (254 - 252)).astype(np.uint8)
    g[m_yo] = (224 - t_yo * (224 - 141)).astype(np.uint8)
    b[m_yo] = (139 - t_yo * (139 - 89)).astype(np.uint8)

    # 4. 36°C to 38°C: Orange -> Red
    m_or = (lst_arr >= 36.0) & (lst_arr < 38.0)
    t_or = (lst_arr[m_or] - 36.0) / 2.0
    r[m_or] = (252 - t_or * (252 - 215)).astype(np.uint8)
    g[m_or] = (141 - t_or * (141 - 48)).astype(np.uint8)
    b[m_or] = (89 - t_or * (89 - 39)).astype(np.uint8)

    # 5. Above 38°C: Solid Extreme Red
    m_hot = lst_arr >= 38.0
    r[m_hot], g[m_hot], b[m_hot] = 215, 48, 39

    return np.stack([r, g, b, a], axis=-1)

def generate_lst_raster_image(bounds, city_id="khulna", year=2026, rows=200, cols=200):
    """
    Renders continuous 2D Landsat 8/9 TIRS LST raster overlay (PNG).
    Reads authentic GeoTIFF file from data/rasters/ if present; otherwise synthesizes via physical equations.
    """
    # 1. Check for authentic GeoTIFF file in data/rasters/
    geotiff_path = Path(RASTERS_DIR) / f"lst_{year}.tif"
    if not geotiff_path.exists() and year == 2026:
        geotiff_path = Path(RASTERS_DIR) / "lst_2026.tif"

    if geotiff_path.exists() and city_id == "khulna":
        try:
            im_tif = Image.open(geotiff_path)
            lst = np.array(im_tif, dtype=np.float32)
            if lst.shape != (rows, cols):
                im_resized = Image.fromarray(lst).resize((cols, rows), Image.BILINEAR)
                lst = np.array(im_resized, dtype=np.float32)
        except Exception:
            lst = None
    else:
        lst = None

    # 2. Dynamic Physical Synthesis fallback
    if lst is None:
        min_lat, min_lon, max_lat, max_lon = bounds
        lats = np.linspace(max_lat, min_lat, rows)
        lons = np.linspace(min_lon, max_lon, cols)
        lon_grid, lat_grid = np.meshgrid(lons, lats)
        
        if city_id == "khulna":
            center_lat, center_lon = 22.8456, 89.5403
            river_lon_base = 89.565
            river_curve = 0.015 * np.sin((lat_grid - 22.84) * 35.0)
            dist_river = np.abs(lon_grid - (river_lon_base + river_curve))
            river_cooling = np.exp(- (dist_river / 0.007)**2) * 3.8
        else:
            center_lat, center_lon = 23.8103, 90.4125
            river_lat_base = 23.715
            dist_river = np.abs(lat_grid - river_lat_base)
            river_cooling = np.exp(- (dist_river / 0.010)**2) * 3.2
            
        dist_center = np.sqrt((lat_grid - center_lat)**2 + (lon_grid - center_lon)**2)
        urban_heat = np.maximum(0, (0.045 - dist_center) / 0.045) * 4.6
        year_delta = (year - 2015) * 0.42
        spatial_var = (np.sin(lat_grid * 300.0) * np.cos(lon_grid * 300.0)) * 0.4
        base_t = 32.2 if city_id == "khulna" else 32.8
        lst = base_t + year_delta + urban_heat - river_cooling + spatial_var
        lst = np.clip(lst, 27.5, 41.5)

    min_lst = round(float(lst.min()), 1)
    max_lst = round(float(lst.max()), 1)

    # 3. Apply exact color ramp
    rgba = colormap_lst_to_rgba(lst)
    img = Image.fromarray(rgba, "RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue(), min_lst, max_lst
