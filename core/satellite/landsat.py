"""
SURF Landsat 8/9 TIRS & OLI Satellite Processing Module
Supports River Masking and Multi-Temporal Satellite Scene Generation (2015 - 2026)
"""
from __future__ import annotations
import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np
from config import LANDSAT_TIRS, PHYSICAL_CONSTANTS

logger = logging.getLogger(__name__)

class LandsatProcessor:
    def __init__(self, band10_constants: Optional[Dict[str, float]] = None):
        self.tirs = band10_constants or LANDSAT_TIRS["BAND_10"]
        self.ml = self.tirs["M_L"]
        self.al = self.tirs["A_L"]
        self.k1 = self.tirs["K1"]
        self.k2 = self.tirs["K2"]
        self.wavelength = self.tirs["WAVELENGTH_UM"]
        self.rho = PHYSICAL_CONSTANTS["BOLTZMANN_C2"] * 1e6

    def compute_toa_radiance(self, band10_dn: np.ndarray) -> np.ndarray:
        radiance = self.ml * band10_dn + self.al
        return np.maximum(radiance, 0.0)

    def compute_brightness_temperature(self, radiance: np.ndarray) -> np.ndarray:
        safe_radiance = np.where(radiance <= 0, 1e-6, radiance)
        return self.k2 / np.log((self.k1 / safe_radiance) + 1.0)

    @staticmethod
    def compute_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        denom = nir_band + red_band
        safe_denom = np.where(denom == 0, 1e-6, denom)
        return np.clip((nir_band - red_band) / safe_denom, -1.0, 1.0)

    @staticmethod
    def compute_fractional_vegetation_cover(ndvi: np.ndarray, ndvi_soil: float = 0.05, ndvi_veg: float = 0.70) -> np.ndarray:
        denom = ndvi_veg - ndvi_soil
        return np.clip(((ndvi - ndvi_soil) / denom) ** 2, 0.0, 1.0)

    def compute_land_surface_emissivity(self, ndvi: np.ndarray, fvc: np.ndarray, eps_soil: float = 0.965, eps_veg: float = 0.985) -> np.ndarray:
        d_eps = (1.0 - eps_soil) * (1.0 - fvc) * 0.55 * eps_veg
        emissivity = np.where(
            ndvi < 0.0, PHYSICAL_CONSTANTS["EMISSIVITY_WATER"],
            np.where(ndvi < 0.15, eps_soil, np.where(ndvi > 0.70, eps_veg, eps_veg * fvc + eps_soil * (1.0 - fvc) + d_eps))
        )
        return np.clip(emissivity, 0.90, 0.995)

    def compute_lst(self, band10_dn: np.ndarray, red_band: np.ndarray, nir_band: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        radiance = self.compute_toa_radiance(band10_dn)
        bt = self.compute_brightness_temperature(radiance)
        ndvi = self.compute_ndvi(red_band, nir_band)
        fvc = self.compute_fractional_vegetation_cover(ndvi)
        emissivity = self.compute_land_surface_emissivity(ndvi, fvc)
        denom = 1.0 + ((self.wavelength * bt) / self.rho) * np.log(emissivity)
        lst_celsius = (bt / denom) - 273.15
        return lst_celsius, ndvi, emissivity

    @classmethod
    def generate_synthetic_scene(cls, shape: Tuple[int, int] = (64, 64), year: int = 2026, seed: int = 42) -> Dict[str, np.ndarray]:
        np.random.seed(seed)
        rows, cols = shape
        y, x = np.mgrid[0:rows, 0:cols]
        y_norm = y / rows
        x_norm = x / cols

        # Temporal trajectory: 2015 has less urban built-up and cooler temperature; 2026 has peak urban density
        time_fraction = max(0.0, min(1.0, (year - 2015) / 11.0))

        # Meandering river geometry (Bhairab / Rupsha River channel)
        river_center = 0.60 + 0.12 * np.sin(y_norm * 4.5)
        river_mask = np.abs(x_norm - river_center) < 0.06

        # Urban Core (Kotwali, Sadar, Khalishpur west of river)
        dist_urban = np.sqrt((x_norm - 0.42)**2 + (y_norm - 0.50)**2)
        urban_base = np.exp(-dist_urban * 3.8)
        urban_density = np.clip(urban_base * (0.60 + time_fraction * 0.45), 0.0, 1.0)
        urban_density = np.where(river_mask, 0.0, urban_density)

        # Vegetation / Green Corridors (Gollamari, Mayur river basin, peri-urban)
        park_gollamari = np.exp(-(((x_norm - 0.20)**2 + (y_norm - 0.75)**2) * 45))
        park_north = np.exp(-(((x_norm - 0.30)**2 + (y_norm - 0.20)**2) * 55))
        veg_baseline = (1.0 - urban_density) * (0.55 - time_fraction * 0.20) + (park_gollamari + park_north) * 0.35
        veg_coverage = np.clip(veg_baseline, 0.05, 0.85)
        veg_coverage = np.where(river_mask, 0.0, veg_coverage)

        # Multi-spectral bands
        red = 0.28 * urban_density + 0.05 * (1.0 - urban_density) - 0.06 * veg_coverage + np.random.normal(0, 0.012, shape)
        nir = 0.12 * urban_density + 0.50 * veg_coverage + np.random.normal(0, 0.012, shape)
        red = np.where(river_mask, 0.02, np.clip(red, 0.02, 0.55))
        nir = np.where(river_mask, 0.01, np.clip(nir, 0.01, 0.75))

        # Calibrated thermal Band 10 DN
        # Urban hotspots: 35C to 41C in 2026; cooler in 2015 (30C to 34C)
        # Rivers: 24C - 26C (cool)
        base_temp_dn = 28500 + (time_fraction * 1800) + (urban_density * 4200) - (veg_coverage * 2800)
        base_temp_dn = np.where(river_mask, 25500, base_temp_dn)
        band10_dn = base_temp_dn + np.random.normal(0, 80, shape)

        return {
            "band10_dn": np.clip(band10_dn, 22000, 36000),
            "red": red,
            "nir": nir,
            "river_mask": river_mask,
            "year": year
        }
