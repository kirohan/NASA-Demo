"""
SURF Heat Analyzer with River Masking and Continuous Gradient Generation
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List, Tuple
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

    def analyze_raster(self, lst_array: np.ndarray, river_mask: np.ndarray = None, rural_baseline_c: float = 26.5) -> Dict[str, Any]:
        if river_mask is not None:
            valid_lst = lst_array[~np.isnan(lst_array) & ~river_mask]
        else:
            valid_lst = lst_array[~np.isnan(lst_array)]

        if len(valid_lst) == 0:
            return {"mean_temperature_c": 0.0, "overall_risk_level": "Low"}

        mean_temp = float(np.mean(valid_lst))
        return {
            "mean_temperature_c": round(mean_temp, 2),
            "max_temperature_c": round(float(np.max(valid_lst)), 2),
            "min_temperature_c": round(float(np.min(valid_lst)), 2),
            "uhi_intensity_c": round(max(0.0, mean_temp - rural_baseline_c), 2),
            "overall_risk_level": self.classify_temperature(mean_temp),
            "heat_risk_score": round(self.compute_heat_risk_score(mean_temp, rural_baseline_c), 1)
        }

    def generate_smooth_heat_data(self, center_lat: float, center_lng: float, lst_array: np.ndarray, river_mask: np.ndarray = None, grid_size_km: float = 8.0) -> Dict[str, Any]:
        """
        Generate high-density sampling points with normalized thermal intensities for Leaflet.heat.
        Automatically clips out river and water pixels to keep the blue river water 100% clear.
        """
        rows, cols = lst_array.shape
        d_lat = (grid_size_km / 111.0) / rows
        d_lng = (grid_size_km / (111.0 * np.cos(np.radians(center_lat)))) / cols
        start_lat = center_lat - (rows / 2.0) * d_lat
        start_lng = center_lng - (cols / 2.0) * d_lng

        heat_points = []
        features = []
        color_palette = {"Low": "#38bdf8", "Moderate": "#facc15", "High": "#f97316", "Extreme": "#ef4444"}

        subdivisions = 16
        step_r = max(1, rows // subdivisions)
        step_c = max(1, cols // subdivisions)

        for i in range(subdivisions):
            for j in range(subdivisions):
                r_idx = min(rows - 1, i * step_r)
                c_idx = min(cols - 1, j * step_c)

                # Skip river water pixels so the natural blue river satellite photography is visible
                if river_mask is not None and river_mask[r_idx, c_idx]:
                    continue

                val = float(lst_array[r_idx, c_idx])
                lat_pt = start_lat + (i + 0.5) * (step_r * d_lat)
                lng_pt = start_lng + (j + 0.5) * (step_c * d_lng)

                # Normalized intensity: 26C = 0.1, 42C = 1.0
                intensity = float(np.clip((val - 26.0) / 16.0, 0.1, 1.0))
                heat_points.append([round(lat_pt, 5), round(lng_pt, 5), round(intensity, 3)])

                min_lat = start_lat + i * (step_r * d_lat)
                max_lat = min_lat + (step_r * d_lat)
                min_lng = start_lng + j * (step_c * d_lng)
                max_lng = min_lng + (step_c * d_lng)

                risk = self.classify_temperature(val)
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
                        "fill_opacity": 0.45
                    }
                })

        return {
            "heat_points": heat_points,
            "geojson": {"type": "FeatureCollection", "features": features}
        }
