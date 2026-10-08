# Scientific Methodology & Satellite Observation Framework

**SURF: Satellite Urban Resilience Framework**  
*NASA Space Apps Challenge*

---

## 1. Executive Summary
Rapid urbanization and climate warming amplify Urban Heat Islands (UHI), deplete vegetative cooling, and escalate urban vulnerability. SURF transforms multi-spectral and thermal Earth observation data from NASA missions (Landsat 8/9, Terra/Aqua MODIS, SRTM/NASADEM, and AppEEARS) into scientifically defensible environmental intelligence and decision-support indicators.

---

## 2. Satellite Datasets & NASA Missions
- **Landsat 8/9 TIRS (Band 10):** Thermal infrared (100m resampled to 30m) for Brightness Temperature.
- **Landsat 8/9 OLI (Bands 4, 5, 6):** Red, NIR, and SWIR for NDVI and NDBI.
- **MODIS MOD11A2 / MYD11A2:** 8-day composite Land Surface Temperature (LST, 1km).
- **MODIS MOD13Q1:** 16-day composite Normalized Difference Vegetation Index (NDVI, 250m).
- **SRTM / NASADEM:** 30m Global Digital Elevation Model for elevation analysis.
- **NASA AppEEARS & Giovanni:** Area-of-interest data extraction and atmospheric validation.

---

## 3. Mathematical & Physical Derivations

### 3.1 Radiance Conversion (Landsat TIRS Band 10)
$$L_\lambda = M_L \cdot Q_{\text{cal}} + A_L$$
Where $M_L = 0.0003342$, $A_L = 0.1$.

### 3.2 Brightness Temperature (Planck Inversion)
$$T_B = \frac{K_2}{\ln\left(\frac{K_1}{L_\lambda} + 1\right)}$$
Where $K_1 = 774.8853$, $K_2 = 1321.0789$.

### 3.3 NDVI and Fractional Vegetation Cover
$$\text{NDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{RED}}}{\rho_{\text{NIR}} + \rho_{\text{RED}}}$$
$$P_v = \left(\frac{\text{NDVI} - \text{NDVI}_{\text{soil}}}{\text{NDVI}_{\text{veg}} - \text{NDVI}_{\text{soil}}}\right)^2$$

### 3.4 Land Surface Emissivity (Sobrino et al. 2004)
$$\varepsilon = \varepsilon_{\text{veg}} \cdot P_v + \varepsilon_{\text{soil}} \cdot (1 - P_v) + d\varepsilon$$

### 3.5 Land Surface Temperature (LST)
$$\text{LST} = \frac{T_B}{1 + \left(\frac{\lambda \cdot T_B}{\rho}\right) \cdot \ln(\varepsilon)}$$
$$T_{\text{Celsius}} = \text{LST} - 273.15$$

---

## 4. Multi-Criteria Climate Risk Score (MCDA)
$$\text{Climate Risk Score} = 0.30 \cdot I_{\text{LST}} + 0.25 \cdot I_{\text{Veg}} + 0.20 \cdot I_{\text{NDBI}} + 0.15 \cdot I_{\text{Pop}} + 0.10 \cdot I_{\text{Elev}}$$

---

## 5. Scientific Limitations
SURF provides satellite-derived indicators and estimated environmental impacts. It does not generate deterministic daily weather or future rainfall forecasts.
