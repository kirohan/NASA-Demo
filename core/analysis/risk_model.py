"""
SURF Climate Risk Model
"""
from __future__ import annotations
import logging
from typing import Dict, Any, Optional
import numpy as np
from config import RISK_WEIGHTS

logger = logging.getLogger(__name__)

class ClimateRiskModel:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or RISK_WEIGHTS

    @classmethod
    def get_risk_tier(cls, score: float) -> str:
        if score < 40.0:
            return "Low"
        elif score < 60.0:
            return "Moderate"
        elif score < 80.0:
            return "High"
        else:
            return "Extreme"

    def compute_composite_risk(self, surface_temp_c: float, ndvi: float, ndbi: float, pop_density: float, elevation_m: float = 12.0, ward_id: Optional[str] = None) -> Dict[str, Any]:
        s_lst = np.clip(((surface_temp_c - 24.0) / 20.0) * 100.0, 0, 100)
        s_veg = np.clip((1.0 - ((ndvi - 0.05) / 0.70)) * 100.0, 0, 100)
        s_urb = np.clip(((ndbi + 0.3) / 0.8) * 100.0, 0, 100)
        s_pop = np.clip((pop_density / 35000.0) * 100.0, 0, 100)
        s_elev = 85.0 if elevation_m < 5.0 else 40.0

        sub = {
            "surface_temperature": s_lst,
            "vegetation_deficit": s_veg,
            "built_up_density": s_urb,
            "population_density": s_pop,
            "elevation_vulnerability": s_elev
        }
        score = sum(sub[k] * self.weights[k] for k in self.weights)
        score = round(float(np.clip(score, 0.0, 100.0)), 1)

        reasons = []
        if s_lst >= 65:
            reasons.append(f"Elevated Land Surface Temperature ({surface_temp_c:.1f}°C) driving high urban thermal stress")
        if s_veg >= 65:
            reasons.append(f"Severe vegetation canopy deficit (mean NDVI: {ndvi:.2f}) with insufficient vegetative cooling")
        if s_urb >= 60:
            reasons.append(f"High impervious surface density (NDBI: {ndbi:.2f}) exacerbating heat retention")
        if s_pop >= 60:
            reasons.append(f"High population exposure density ({int(pop_density):,} residents/km²)")
        if not reasons:
            reasons.append("Balanced environmental indicators with moderate canopy cover and low thermal anomaly.")

        return {
            "ward_id": ward_id or "Selected Area",
            "climate_risk_score": score,
            "resilience_score": round(100.0 - score, 1),
            "risk_level": self.get_risk_tier(score),
            "reasons": reasons
        }
