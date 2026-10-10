"""
Urban Heat Island (UHI) & LST Spatial Analysis
Evaluates Land Surface Temperature distribution, urban-rural thermal gradient,
and categorizes thermal hazards.
"""
def categorize_heat_hazard(lst_c):
    """
    Classify thermal stress based on deltaic urban thresholds:
    - Extreme (> 37°C): Severe thermal risk to informal settlement laborers
    - High (34 - 37°C): Sustained heat accumulation, commercial/industrial cores
    - Moderate (31 - 34°C): Residential with partial vegetative shading
    - Low (< 31°C): River buffers, wetlands, dense institutional tree canopies
    """
    if lst_c >= 37.0:
        return {"level": "Extreme Heat Stress", "color": "#d73027", "code": "EXTREME"}
    elif lst_c >= 34.0:
        return {"level": "High Heat Stress", "color": "#fc8d59", "code": "HIGH"}
    elif lst_c >= 31.0:
        return {"level": "Moderate Heat Stress", "color": "#fee08b", "code": "MODERATE"}
    else:
        return {"level": "Low / Buffered", "color": "#91bfdb", "code": "LOW"}

def calculate_uhi_intensity(urban_lst, rural_baseline_lst=30.2):
    """
    Urban Heat Island Intensity (UHII) = LST_urban - LST_rural_baseline (°C)
    """
    return round(urban_lst - rural_baseline_lst, 2)
