"""
SURF NASA MODIS Ingestion Module
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger(__name__)

class ModisProcessor:
    LST_SCALE_FACTOR = 0.02
    NDVI_SCALE_FACTOR = 0.0001
    FILL_VALUE_LST = 0
    FILL_VALUE_NDVI = -3000

    @classmethod
    def calibrate_lst(cls, raw_lst: np.ndarray, apply_qc: bool = True, qc_mask: Optional[np.ndarray] = None) -> np.ndarray:
        calibrated_c = (raw_lst.astype(float) * cls.LST_SCALE_FACTOR) - 273.15
        invalid_mask = (raw_lst == cls.FILL_VALUE_LST) | (calibrated_c < -40.0) | (calibrated_c > 75.0)
        return np.where(invalid_mask, np.nan, calibrated_c)

    @classmethod
    def simulate_temporal_trend(cls, base_lst: float, base_ndvi: float, years: List[int]) -> List[Dict[str, Any]]:
        trend_records = []
        n_years = len(years)
        for i, year in enumerate(years):
            fraction = i / max(n_years - 1, 1)
            annual_lst = base_lst + (fraction * 3.6) + np.random.normal(0, 0.20)
            annual_ndvi = max(0.08, base_ndvi - (fraction * 0.16) + np.random.normal(0, 0.015))
            built_up_pct = min(85.0, 42.0 + (fraction * 36.0) + np.random.normal(0, 0.8))
            trend_records.append({
                "year": year,
                "mean_lst_c": round(float(annual_lst), 2),
                "mean_ndvi": round(float(annual_ndvi), 3),
                "built_up_area_pct": round(float(built_up_pct), 1),
                "green_space_area_pct": round(max(8.0, 100.0 - built_up_pct - 9.0), 1)
            })
        return trend_records
