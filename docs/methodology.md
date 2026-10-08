# Scientific Methodology & Satellite Observation Framework

**SURF: Satellite Urban Resilience Framework v2.5**  
*NASA Space Apps Challenge*

---

## 1. Executive Summary
SURF transforms NASA Earth observation telemetry into actionable, scientifically defensible environmental intelligence for cities worldwide.

## 2. Multi-Temporal Remote Sensing Architecture
- **Landsat 8/9 TIRS (Band 10):** Radiometric calibration to at-satellite Brightness Temperature via Planck equation inversion.
- **Sobrino et al. (2004) Threshold Emissivity:** Land Surface Emissivity derived from Fractional Vegetation Cover ($P_v$).
- **River & Water Masking:** Negative NDVI filtering protects river networks (Bhairab, Rupsha, Buriganga) from thermal false alarms.
- **Continuous Thermal Interpolation:** Gaussian kernel density smoothing delivers continuous temperature fields.
- **Historical Trajectory Engine:** Synthesizes observations from 2015 to 2026.
