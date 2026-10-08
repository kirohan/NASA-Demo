"""
SURF Heat Analyzer
"""
from __future__ import annotations
import logging
from typing import Dict, Any, Tuple
import numpy as np
from config import HEAT_RISK_THRESHOLDS

logger = logging.getLogger(__name__)

class HeatAnalyzer:
    def __init__(self, thresholds: Dict[str, Tuple[float, float]] = None):
        self.thresholds = thresholds or HEAT_RISK_THRESHOLDS

    def classify_temperature(self, temp_celsius: float) -> str:
        if temp_celsius < self.thresholds["LOW"][1]:
            return "Low"
        elif temp_celsius < self.thresholds["MODERATE"][1]:
            return "Moderate"
        elif temp_celsius < self.thresholds["HIGH"][1]:
            return "High"
        else:
            return "Extreme"

    def compute_heat_risk_score(self, lst_celsius: float, baseline_rural_celsius: float = 27.0) -> float:
        score = ((lst_celsius - baseline_rural_celsius) / 18.0) * 100.0
        return float(np.clip(score, 0.0, 100.0))

    def analyze_raster(self, lst_array: np.ndarray, rural_baseline_c: float = 26.5) -> Dict[str, Any]:
        valid_mask = ~np.isnan(lst_array)
        valid_lst = lst_array[valid_mask]
        if len(valid_lst) == 0:
            return {"mean_temperature_c": 0.0, "overall_risk_level": "Low"}
        mean_temp = float(np.mean(valid_lst))
        return {
            "mean_temperature_c": round(mean_temp, 2),
            "max_temperature_c": round(float(np.max(valid_lst)), 2),
            "min_temperature_c": round(float(np.min(valid_lst)), 2),
            "uhi_intensity_c": round(mean_temp - rural_baseline_c, 2),
            "overall_risk_level": self.classify_temperature(mean_temp),
            "heat_risk_score": round(self.compute_heat_risk_score(mean_temp, rural_baseline_c), 1)
        }

    def generate_grid_geojson(self, center_lat: float, center_lng: float, lst_array: np.ndarray, grid_size_km: float = 8.0, subdivisions: int = 16) -> Dict[str, Any]:
        rows, cols = lst_array.shape
        d_lat = (grid_size_km / 111.0) / subdivisions
        d_lng = (grid_size_km / (111.0 * np.cos(np.radians(center_lat)))) / subdivisions
        start_lat = center_lat - (subdivisions / 2.0) * d_lat
        start_lng = center_lng - (subdivisions / 2.0) * d_lng
        features = []
        step_r = max(1, rows // subdivisions)
        step_c = max(1, cols // subdivisions)
        color_palette = {"Low": "#38bdf8", "Moderate": "#facc15", "High": "#f97316", "Extreme": "#ef4444"}

        for i in range(subdivisions):
            for j in range(subdivisions):
                val = float(lst_array[min(rows - 1, i * step_r), min(cols - 1, j * step_c)])
                risk = self.classify_temperature(val)
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
                        "temperature_c": round(val, 1),
                        "risk_level": risk,
                        "fill_color": color_palette[risk],
                        "fill_opacity": 0.65
                    }
                })
        return {"type": "FeatureCollection", "features": features}
