# Scientific Methodology & Mathematical Formulations
## SURF — Satellite Urban Resilience Framework

### 1. Land Surface Temperature (LST) Derivation
LST is computed from NASA Landsat 8/9 Thermal Infrared Sensor (TIRS) Band 10 (10.895 µm central wavelength) and validated against Terra/Aqua MODIS (MOD11A2 8-day composite).

#### A. Digital Number (DN) to Top-of-Atmosphere (TOA) Spectral Radiance
$$L_\lambda = M_L \cdot Q_{\text{cal}} + A_L$$
Where:
- $M_L = 0.0003342$ (Multiplicative rescaling factor)
- $A_L = 0.1$ (Additive rescaling factor)
- $Q_{\text{cal}}$ = Calibrated standard pixel value (DN)

#### B. Inversion of Planck's Radiation Law (At-Sensor Brightness Temperature)
$$T_b = \frac{K_2}{\ln\left(\frac{K_1}{L_\lambda} + 1\right)}$$
Calibration Constants for Landsat TIRS Band 10:
- $K_1 = 774.8853 \,\text{W} / (\text{m}^2 \cdot \text{sr} \cdot \mu\text{m})$
- $K_2 = 1321.0789 \,\text{K}$

#### C. Fractional Vegetation Cover ($P_v$) and Land Surface Emissivity ($\varepsilon$)
Utilizing the Sobrino et al. (2004) NDVI threshold framework:
$$P_v = \left(\frac{\text{NDVI} - \text{NDVI}_s}{\text{NDVI}_v - \text{NDVI}_s}\right)^2$$
Where $\text{NDVI}_s = 0.05$ (bare soil threshold) and $\text{NDVI}_v = 0.70$ (fully vegetated canopy threshold).
$$\varepsilon = \varepsilon_v P_v + \varepsilon_s (1 - P_v) + C_\lambda$$
Where $\varepsilon_v = 0.985$, $\varepsilon_s = 0.960$, and $C_\lambda = (1 - \varepsilon_s)\varepsilon_v F' (1 - P_v)$ accounts for internal cavity radiation in rough urban geometries.

#### D. Atmospheric Correction & Final LST
$$\text{LST} = \frac{T_b}{1 + \left(\frac{\lambda T_b}{\rho}\right) \ln(\varepsilon)} - 273.15 \quad (^{\circ}\text{C})$$
Where:
- $\lambda = 10.895 \,\mu\text{m}$ (central emitted wavelength)
- $\rho = \frac{h \cdot c}{\sigma} = 1.4388 \times 10^{-2} \,\text{m}\cdot\text{K} = 14,388 \,\mu\text{m}\cdot\text{K}$

---

### 2. Copernicus Sentinel-2 MSI Vegetation Indices
#### Normalized Difference Vegetation Index (NDVI)
$$\text{NDVI} = \frac{\text{NIR} - \text{RED}}{\text{NIR} + \text{RED}} = \frac{B_8 - B_4}{B_8 + B_4}$$
- Band 4 (Red): 665 nm (chlorophyll-a absorption peak)
- Band 8 (NIR): 842 nm (canopy mesophyll cell reflection)

#### Ecological Canopy Classification
- **Dense Vegetation ($0.8 \le \text{NDVI} \le 1.0$):** Multi-layered mangrove buffers, institutional botanical reserves.
- **Moderate Vegetation ($0.4 \le \text{NDVI} < 0.8$):** Peri-urban agricultural plots, homestead agroforestry.
- **Low Vegetation / Impervious ($0.0 \le \text{NDVI} < 0.4$):** Dense urban fabric, asphalt roadways, corrugated iron roofs.
- **Water Bodies ($\text{NDVI} < 0.0$):** Bhairab, Rupsha rivers, and tidal retention canals.

---

### 3. Transparent Climate Risk & Resilience Scoring (MCDA)
Unlike opaque single-score models, SURF decomposes urban climate risk into four verifiable multi-criteria indicators:
$$\text{Climate Risk Score} = (0.35 \cdot H) + (0.25 \cdot V) + (0.20 \cdot D) + (0.20 \cdot P)$$
1. **Heat Exposure ($H$, 35%):** Normalized LST anomaly above rural baseline ($30^{\circ}\text{C} \rightarrow 0, 40^{\circ}\text{C} \rightarrow 100$).
2. **Vegetation Deficit ($V$, 25%):** Canopy deficit relative to WHO minimum 9 m²/capita green space standard.
3. **Urban Density ($D$, 20%):** Built-up impervious surface fraction ($20\% \rightarrow 0, 80\% \rightarrow 100$).
4. **Population Exposure ($P$, 20%):** WorldPop 100m gridded building-density exposure.

$$\text{Climate Resilience Score} = 100 - \text{Climate Risk Score}$$
