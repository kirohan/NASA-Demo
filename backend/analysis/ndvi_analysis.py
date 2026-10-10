"""
Vegetation Health & Ecological Canopy Analysis
Measures green space deficit relative to WHO minimum standard (9 m²/capita).
"""
def compute_canopy_metrics(ndvi_score, built_up_pct, total_area_ha, population):
    """
    Computes green canopy hectarage, per-capita green space, and green deficit.
    """
    canopy_pct = max(5.0, min(80.0, (ndvi_score + 0.1) * 75.0))
    green_area_ha = round((canopy_pct / 100.0) * total_area_ha, 1)
    
    green_sqm = green_area_ha * 10000.0
    sqm_per_capita = round(green_sqm / max(population, 1), 2)
    
    # WHO recommends at least 9.0 m² green space per capita
    who_deficit_pct = max(0.0, round(((9.0 - sqm_per_capita) / 9.0) * 100.0, 1)) if sqm_per_capita < 9.0 else 0.0
    
    return {
        "canopy_pct": round(canopy_pct, 1),
        "green_area_ha": green_area_ha,
        "sqm_per_capita": sqm_per_capita,
        "who_standard_sqm": 9.0,
        "who_deficit_pct": who_deficit_pct
    }
