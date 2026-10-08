"""
SURF — Satellite Urban Resilience Framework
NASA MODIS Ingestion Module
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class ModisProcessor:
    LST_SCALE_FACTOR = 0.02
    NDVI_SCALE_FACTOR = 0.0001
    FILL_VALUE_LST = 0
    FILL_VALUE_NDVI = -3000

    @classmethod
    def calibrate_lst(cls, raw_lst: np.ndarray, apply_qc: bool = True, qc_mask: Optional[np.ndarray] = None) -> np.ndarray:
        calibrated_k = raw_lst.astype(float) * cls.LST_SCALE_FACTOR
        calibrated_c = calibrated_k - 273.15
        invalid_mask = (raw_lst == cls.FILL_VALUE_LST) | (calibrated_c < -40.0) | (calibrated_c > 75.0)
        if apply_qc and qc_mask is not None:
            qc_flag = qc_mask & 0b11
            invalid_mask |= (qc_flag > 1)
        return np.where(invalid_mask, np.nan, calibrated_c)

    @classmethod
    def calibrate_ndvi(cls, raw_ndvi: np.ndarray) -> np.ndarray:
        scaled = raw_ndvi.astype(float) * cls.NDVI_SCALE_FACTOR
        invalid_mask = (raw_ndvi <= cls.FILL_VALUE_NDVI) | (scaled < -1.0) | (scaled > 1.0)
        return np.where(invalid_mask, np.nan, scaled)

    @classmethod
    def compute_urban_thermal_anomaly(cls, urban_lst: np.ndarray, rural_buffer_lst: np.ndarray) -> Dict[str, float]:
        valid_urban = urban_lst[~np.isnan(urban_lst)]
        valid_rural = rural_buffer_lst[~np.isnan(rural_buffer_lst)]
        if len(valid_urban) == 0 or len(valid_rural) == 0:
            return {"suhi_intensity_c": 0.0, "urban_mean_c": 0.0, "rural_mean_c": 0.0}
        u_mean = float(np.mean(valid_urban))
        r_mean = float(np.mean(valid_rural))
        return {
            "suhi_intensity_c": round(u_mean - r_mean, 2),
            "urban_mean_c": round(u_mean, 2),
            "rural_mean_c": round(r_mean, 2)
        }

    @classmethod
    def simulate_temporal_trend(cls, base_lst: float, base_ndvi: float, years: List[int]) -> List[Dict[str, Any]]:
        trend_records = []
        n_years = len(years)
        for i, year in enumerate(years):
            fraction = i / max(n_years - 1, 1)
            annual_lst = base_lst + (fraction * 2.1) + np.random.normal(0, 0.25)
            annual_ndvi = max(0.05, base_ndvi - (fraction * 0.12) + np.random.normal(0, 0.02))
            built_up_pct = min(88.0, 52.0 + (fraction * 28.0) + np.random.normal(0, 1.0))
            trend_records.append({
                "year": year,
                "mean_lst_c": round(float(annual_lst), 2),
                "mean_ndvi": round(float(annual_ndvi), 3),
                "built_up_area_pct": round(float(built_up_pct), 1),
                "green_space_area_pct": round(max(5.0, 100.0 - built_up_pct - 8.0), 1)
            })
        return trend_records
