"""
Transparent Multi-Criteria Climate Risk & Resilience Scoring (MCDA)
Calculates composite score with 4 explicit, verifiable components:
1. Heat Exposure: 35%
2. Vegetation Deficit: 25%
3. Urban Density: 20%
4. Population Exposure: 20%
"""
try:
    from ..config import (
        WEIGHT_HEAT_EXPOSURE, WEIGHT_VEGETATION_DEFICIT,
        WEIGHT_URBAN_DENSITY, WEIGHT_POPULATION_EXPOSURE
    )
except (ImportError, ValueError):
    try:
        from backend.config import (
            WEIGHT_HEAT_EXPOSURE, WEIGHT_VEGETATION_DEFICIT,
            WEIGHT_URBAN_DENSITY, WEIGHT_POPULATION_EXPOSURE
        )
    except (ImportError, ValueError):
        from config import (
            WEIGHT_HEAT_EXPOSURE, WEIGHT_VEGETATION_DEFICIT,
            WEIGHT_URBAN_DENSITY, WEIGHT_POPULATION_EXPOSURE
        )

def calculate_transparent_risk_score(lst_c, ndvi, built_up_pct, population_density):
    """
    Computes transparent risk and resilience metrics with component breakdowns.
    - lst_c: Land surface temperature (°C). Normalized 30°C -> 0.0, 40°C -> 1.0
    - ndvi: Normalized Difference Veg Index. Normalized 0.60 -> 0.0, 0.05 -> 1.0 (Deficit)
    - built_up_pct: Impervious percentage. Normalized 20% -> 0.0, 80% -> 1.0
    - population_density: People/km². Normalized 5,000 -> 0.0, 45,000 -> 1.0
    """
    # 1. Heat Exposure (35%)
    heat_norm = max(0.0, min(1.0, (lst_c - 30.0) / 9.5))
    heat_component = round(heat_norm * WEIGHT_HEAT_EXPOSURE * 100.0, 1)
    
    # 2. Vegetation Deficit (25%)
    # Lower NDVI means higher deficit
    veg_norm = max(0.0, min(1.0, (0.55 - ndvi) / 0.50))
    veg_component = round(veg_norm * WEIGHT_VEGETATION_DEFICIT * 100.0, 1)
    
    # 3. Urban Density (20%)
    density_norm = max(0.0, min(1.0, (built_up_pct - 20.0) / 60.0))
    density_component = round(density_norm * WEIGHT_URBAN_DENSITY * 100.0, 1)
    
    # 4. Population Exposure (20%)
    pop_norm = max(0.0, min(1.0, (population_density - 5000.0) / 35000.0))
    pop_component = round(pop_norm * WEIGHT_POPULATION_EXPOSURE * 100.0, 1)
    
    # Total Composite Climate Risk Score (0 - 100)
    composite_risk = int(round(heat_component + veg_component + density_component + pop_component))
    composite_risk = max(10, min(98, composite_risk))
    
    # Climate Resilience Score (Inverse of Risk)
    resilience_score = 100 - composite_risk
    
    if composite_risk >= 75:
        tier = "Extreme Risk"
        tier_color = "#d73027"
        recommendation = "Priority Urban Cooling: High-albedo cool roofs and bioswale green corridors required to mitigate acute heat accumulation."
    elif composite_risk >= 60:
        tier = "High Risk"
        tier_color = "#fc8d59"
        recommendation = "Canopy Enhancement: Introduce pocket parks and permeable pavers along transport corridors."
    elif composite_risk >= 45:
        tier = "Moderate Risk"
        tier_color = "#fee08b"
        recommendation = "Ecosystem Conservation: Protect existing water bodies and peri-urban agricultural wetlands."
    else:
        tier = "Low / Resilient"
        tier_color = "#91bfdb"
        recommendation = "Resilience Monitoring: Maintain current vegetative buffers and riparian setbacks."
        
    return {
        "composite_risk_score": composite_risk,
        "resilience_score": resilience_score,
        "risk_tier": tier,
        "tier_color": tier_color,
        "recommendation": recommendation,
        "components": {
            "heat_exposure": {
                "weight_pct": 35,
                "raw_value": f"{lst_c}°C",
                "normalized_pct": int(round(heat_norm * 100)),
                "contributed_pts": heat_component,
                "label": "Thermal Hazard (LST)"
            },
            "vegetation_deficit": {
                "weight_pct": 25,
                "raw_value": f"NDVI {ndvi}",
                "normalized_pct": int(round(veg_norm * 100)),
                "contributed_pts": veg_component,
                "label": "Canopy Depletion"
            },
            "urban_density": {
                "weight_pct": 20,
                "raw_value": f"{built_up_pct}% Built-up",
                "normalized_pct": int(round(density_norm * 100)),
                "contributed_pts": density_component,
                "label": "Impervious Surface"
            },
            "population_exposure": {
                "weight_pct": 20,
                "raw_value": f"{population_density:,} /km²",
                "normalized_pct": int(round(pop_norm * 100)),
                "contributed_pts": pop_component,
                "label": "Demographic Density"
            }
        }
    }
