"""
SURF NDVI Analyzer with River Exclusion
"""
from __future__ import annotations
import logging
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class NdviAnalyzer:
    @staticmethod
    def classify_ndvi(value: float) -> str:
        if value < 0.0:
            return "Water Body"
        elif value < 0.40:
            return "Low Vegetation"
        elif value < 0.80:
            return "Moderate Vegetation"
        else:
            return "Dense Vegetation"

    def analyze_raster(self, ndvi_array: np.ndarray, river_mask: np.ndarray = None) -> Dict[str, Any]:
        if river_mask is not None:
            valid_ndvi = ndvi_array[~np.isnan(ndvi_array) & ~river_mask]
        else:
            valid_ndvi = ndvi_array[~np.isnan(ndvi_array)]

        if len(valid_ndvi) == 0:
            return {"mean_ndvi": 0.0, "green_coverage_pct": 0.0}

        total_pixels = len(valid_ndvi)
        mean_val = float(np.mean(valid_ndvi))
        mod_cnt = np.sum((valid_ndvi >= 0.40) & (valid_ndvi < 0.80))
        dense_cnt = np.sum(valid_ndvi >= 0.80)
        green_coverage = ((mod_cnt + dense_cnt) / total_pixels) * 100.0

        return {
            "mean_ndvi": round(mean_val, 3),
            "max_ndvi": round(float(np.max(valid_ndvi)), 3),
            "min_ndvi": round(float(np.min(valid_ndvi)), 3),
            "green_coverage_pct": round(float(green_coverage), 1),
            "vegetation_deficit_pct": round(float(100.0 - green_coverage), 1)
        }

    def generate_grid_geojson(self, center_lat: float, center_lng: float, ndvi_array: np.ndarray, river_mask: np.ndarray = None, grid_size_km: float = 8.0, subdivisions: int = 16) -> Dict[str, Any]:
        rows, cols = ndvi_array.shape
        d_lat = (grid_size_km / 111.0) / subdivisions
        d_lng = (grid_size_km / (111.0 * np.cos(np.radians(center_lat)))) / subdivisions
        start_lat = center_lat - (subdivisions / 2.0) * d_lat
        start_lng = center_lng - (subdivisions / 2.0) * d_lng
        features = []
        step_r = max(1, rows // subdivisions)
        step_c = max(1, cols // subdivisions)
        color_palette = {"Water Body": "#0284c7", "Low Vegetation": "#d97706", "Moderate Vegetation": "#65a30d", "Dense Vegetation": "#15803d"}

        for i in range(subdivisions):
            for j in range(subdivisions):
                r_idx = min(rows - 1, i * step_r)
                c_idx = min(cols - 1, j * step_c)
                if river_mask is not None and river_mask[r_idx, c_idx]:
                    continue

                val = float(ndvi_array[r_idx, c_idx])
                cls_name = self.classify_ndvi(val)
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
                        "ndvi": round(val, 3),
                        "classification": cls_name,
                        "fill_color": color_palette[cls_name],
                        "fill_opacity": 0.45
                    }
                })
        return {"type": "FeatureCollection", "features": features}
