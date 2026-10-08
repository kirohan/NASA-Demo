# SURF — Satellite Urban Resilience Framework

> **A Satellite-Powered Environmental Intelligence & Urban Climate Resilience Platform**  
> *NASA Space Apps Challenge Submission (v2.5 Release)*

---

## 🌍 1. Problem Statement
Cities across the globe are facing severe environmental challenges:
- **Urban Heat Islands (UHI):** Concrete structures and asphalt absorb solar radiation, driving urban surface temperatures 4°C to 10°C above rural baselines.
- **Vegetation Canopy Loss:** Rapid expansion strips natural buffers, diminishing shade and natural evapotranspirative cooling.
- **The Information Gap:** City planners lack accessible, evidence-grounded satellite data.

---

## 🛰️ 2. The Solution: SURF
**SURF** transforms NASA Earth Observation datasets into an interactive, scientifically defensible decision-support platform.
> *"Use NASA Earth observation data to understand how a city is changing and identify where climate action is needed."*

---

## 🚀 3. Key v2.5 Features
1. **Historical Time Machine Slider (2015–2026):** Scrub through previous years or hit Play to watch urban sprawl, canopy reduction, and heat intensification unfold over the last decade.
2. **Smooth Thermal Gradient (NASA Worldview Style):** Continuous bi-linear heat interpolation with zero blocky pixel squares.
3. **River & Water Body Masking:** Delineates the Bhairab and Rupsha rivers so deep blue river channels remain crystal-clear on the satellite map.
4. **Authentic Municipal Ward Boundaries:** Detailed Khulna City Corporation (KCC) and Dhaka wards with real measured areas (km² & hectares).
5. **Google Earth Pro 3D Export:** Generates `.kml` layers to inspect 3D terrain, historical satellite imagery (2000–present), and rooftop photogrammetry.
6. **Watermark-Free Satellite Basemaps:** Powered by Google Hybrid Satellite and OpenStreetMap with zero API keys required.

---

## ⚡ 4. Quickstart & Installation
```bash
# 1. Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python app.py
```
Open `http://localhost:8000` in your browser. (API Docs at `http://localhost:8000/docs`).

*Built for the NASA International Space Apps Challenge.*
