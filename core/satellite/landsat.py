"""
SURF — Satellite Urban Resilience Framework
Landsat 8/9 TIRS & OLI Satellite Processing Module
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
        bt_kelvin = self.k2 / np.log((self.k1 / safe_radiance) + 1.0)
        return bt_kelvin

    @staticmethod
    def compute_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        denom = nir_band + red_band
        safe_denom = np.where(denom == 0, 1e-6, denom)
        ndvi = (nir_band - red_band) / safe_denom
        return np.clip(ndvi, -1.0, 1.0)

    @staticmethod
    def compute_fractional_vegetation_cover(ndvi: np.ndarray, ndvi_soil: float = 0.05, ndvi_veg: float = 0.70) -> np.ndarray:
        denom = ndvi_veg - ndvi_soil
        fvc = ((ndvi - ndvi_soil) / denom) ** 2
        return np.clip(fvc, 0.0, 1.0)

    def compute_land_surface_emissivity(self, ndvi: np.ndarray, fvc: np.ndarray, eps_soil: float = 0.965, eps_veg: float = 0.985) -> np.ndarray:
        d_eps = (1.0 - eps_soil) * (1.0 - fvc) * 0.55 * eps_veg
        emissivity = np.where(
            ndvi < 0.0,
            PHYSICAL_CONSTANTS["EMISSIVITY_WATER"],
            np.where(
                ndvi < 0.15,
                eps_soil,
                np.where(
                    ndvi > 0.70,
                    eps_veg,
                    eps_veg * fvc + eps_soil * (1.0 - fvc) + d_eps
                )
            )
        )
        return np.clip(emissivity, 0.90, 0.995)

    def compute_lst(self, band10_dn: np.ndarray, red_band: np.ndarray, nir_band: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        radiance = self.compute_toa_radiance(band10_dn)
        bt = self.compute_brightness_temperature(radiance)
        ndvi = self.compute_ndvi(red_band, nir_band)
        fvc = self.compute_fractional_vegetation_cover(ndvi)
        emissivity = self.compute_land_surface_emissivity(ndvi, fvc)

        denom = 1.0 + ((self.wavelength * bt) / self.rho) * np.log(emissivity)
        lst_kelvin = bt / denom
        lst_celsius = lst_kelvin - 273.15
        return lst_celsius, ndvi, emissivity

    @classmethod
    def generate_synthetic_scene(cls, shape: Tuple[int, int] = (100, 100), urban_core_center: Tuple[float, float] = (0.5, 0.5), seed: int = 42) -> Dict[str, np.ndarray]:
        np.random.seed(seed)
        rows, cols = shape
        y, x = np.mgrid[0:rows, 0:cols]
        y_norm = y / rows
        x_norm = x / cols

        dist = np.sqrt((x_norm - urban_core_center[0])**2 + (y_norm - urban_core_center[1])**2)
        urban_density = np.exp(-dist * 3.5)
        water_mask = np.abs(y_norm - (0.45 + 0.1 * np.sin(x_norm * 6.0))) < 0.04
        park_1 = np.exp(-(((x_norm - 0.25)**2 + (y_norm - 0.7)**2) * 50))
        park_2 = np.exp(-(((x_norm - 0.75)**2 + (y_norm - 0.3)**2) * 60))
        parks = np.clip(park_1 + park_2, 0.0, 1.0)

        red = 0.25 * urban_density + 0.05 * (1.0 - urban_density) - 0.08 * parks + np.random.normal(0, 0.015, shape)
        nir = 0.15 * urban_density + 0.45 * (1.0 - urban_density) + 0.30 * parks + np.random.normal(0, 0.015, shape)
        red = np.where(water_mask, 0.03, np.clip(red, 0.02, 0.6))
        nir = np.where(water_mask, 0.01, np.clip(nir, 0.01, 0.8))

        base_dn = 28000 + (urban_density * 4500) - (parks * 3200) - (water_mask * 4000)
        band10_dn = base_dn + np.random.normal(0, 120, shape)

        return {
            "band10_dn": np.clip(band10_dn, 20000, 35000),
            "red": red,
            "nir": nir,
            "water_mask": water_mask
        }
