"""
SURF Urban Change Detector
"""
from __future__ import annotations
import logging
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class UrbanChangeDetector:
    @staticmethod
    def compute_ndbi(swir: np.ndarray, nir: np.ndarray) -> np.ndarray:
        denom = swir + nir
        safe_denom = np.where(denom == 0, 1e-6, denom)
        return np.clip((swir - nir) / safe_denom, -1.0, 1.0)

    def detect_changes(self, t1_ndvi: np.ndarray, t2_ndvi: np.ndarray, t1_ndbi: np.ndarray, t2_ndbi: np.ndarray, year_t1: int = 2015, year_t2: int = 2026) -> Dict[str, Any]:
        total_pixels = t1_ndvi.size
        built_t1_pct = (np.sum(t1_ndbi > 0.05) / total_pixels) * 100.0
        built_t2_pct = (np.sum(t2_ndbi > 0.05) / total_pixels) * 100.0
        rel_built = ((built_t2_pct - built_t1_pct) / max(built_t1_pct, 1.0)) * 100.0
        veg_t1_pct = (np.sum(t1_ndvi > 0.40) / total_pixels) * 100.0
        veg_t2_pct = (np.sum(t2_ndvi > 0.40) / total_pixels) * 100.0
        rel_veg = ((veg_t2_pct - veg_t1_pct) / max(veg_t1_pct, 1.0)) * 100.0

        return {
            "period": f"{year_t1} - {year_t2}",
            "metrics": {
                "built_up_change_pct": round(float(rel_built), 1),
                "built_up_t1_area_pct": round(float(built_t1_pct), 1),
                "built_up_t2_area_pct": round(float(built_t2_pct), 1),
                "vegetation_change_pct": round(float(rel_veg), 1),
                "vegetation_t1_area_pct": round(float(veg_t1_pct), 1),
                "vegetation_t2_area_pct": round(float(veg_t2_pct), 1)
            },
            "summary_statement": f"Between {year_t1} and {year_t2}, satellite observations indicate a {rel_built:+.1f}% expansion in built-up area and a {rel_veg:+.1f}% change in vegetation canopy."
        }

    def generate_change_geojson(self, center_lat: float, center_lng: float, t1_ndvi: np.ndarray, t2_ndvi: np.ndarray, t1_ndbi: np.ndarray, t2_ndbi: np.ndarray, river_mask: np.ndarray = None, grid_size_km: float = 8.0, subdivisions: int = 16) -> Dict[str, Any]:
        rows, cols = t1_ndvi.shape
        d_lat = (grid_size_km / 111.0) / subdivisions
        d_lng = (grid_size_km / (111.0 * np.cos(np.radians(center_lat)))) / subdivisions
        start_lat = center_lat - (subdivisions / 2.0) * d_lat
        start_lng = center_lng - (subdivisions / 2.0) * d_lng
        delta_ndvi = t2_ndvi - t1_ndvi
        delta_ndbi = t2_ndbi - t1_ndbi
        features = []
        step_r = max(1, rows // subdivisions)
        step_c = max(1, cols // subdivisions)

        for i in range(subdivisions):
            for j in range(subdivisions):
                r_idx = min(rows - 1, i * step_r)
                c_idx = min(cols - 1, j * step_c)
                if river_mask is not None and river_mask[r_idx, c_idx]:
                    continue

                d_veg = float(delta_ndvi[r_idx, c_idx])
                d_urb = float(delta_ndbi[r_idx, c_idx])
                if d_urb > 0.10 and d_veg < -0.05:
                    cat, color = "Urban Expansion", "#ec4899"
                elif d_veg < -0.12:
                    cat, color = "Vegetation Loss", "#ef4444"
                elif d_veg > 0.12:
                    cat, color = "Greening Gain", "#22c55e"
                else:
                    cat, color = "Stable Urban/Matrix", "#64748b"

                min_lat = start_lat + i * d_lat
                max_lat = min_lat + d_lat
                min_lng = start_lng + j * d_lng
                max_lng = min_lng + d_lng
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[round(min_lng, 5), round(min_lat, 5)], [round(max_lng, 5), round(min_lat, 5)], [round(max_lng, 5), round(max_lat, 5)], [round(min_lng, 5), round(max_lat, 5)], [round(min_lng, 5), round(min_lat, 5)]]]
                    },
                    "properties": {
                        "change_category": cat,
                        "fill_color": color,
                        "fill_opacity": 0.45 if cat != "Stable Urban/Matrix" else 0.15
                    }
                })
        return {"type": "FeatureCollection", "features": features}
