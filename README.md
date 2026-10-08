# 🌍 SURF — Satellite Urban Resilience Framework

## NASA Space Apps Challenge Project

SURF is a satellite-powered urban climate intelligence platform that converts Earth observation data into actionable environmental insights.

## Vision

Cities are changing rapidly. SURF helps planners understand:

- Where are the hottest areas?
- Where is vegetation disappearing?
- Which areas are vulnerable?
- What climate actions should be prioritized?

## Architecture

```
NASA Earth Data
      |
      v
Data Processing Engine
      |
      v
Environmental Indicators
      |
      v
Interactive Map Dashboard
      |
      v
Climate Recommendations
```

## Core Features

### 1. Urban Heat Mapping 🌡️
Creates surface temperature risk maps.

Data:
- Landsat Thermal Data
- MODIS Land Surface Temperature

### 2. Vegetation Monitoring 🌱
Calculates vegetation health using NDVI.

Formula:

NDVI = (NIR - RED) / (NIR + RED)

### 3. Urban Change Detection 🏙️
Compares satellite observations over time.

Detects:
- Urban expansion
- Vegetation loss
- Land cover changes

### 4. Climate Risk Recommendation 🤖

Provides possible actions:
- Increase green coverage
- Cool roof implementation
- Solar rooftop opportunities

## Data Sources

- NASA Landsat
- NASA MODIS
- NASA Giovanni
- NASA AppEEARS

## Tech Stack

Backend:
- Python
- FastAPI
- GeoPandas
- Rasterio

Frontend:
- HTML
- CSS
- JavaScript
- Leaflet

## Run

Install:

```
pip install -r requirements.txt
```

Start API:

```
uvicorn app:app --reload
```

Open frontend/index.html

## Future Work

- Wind exposure estimation
- Flood risk mapping
- Solar potential analysis
- Climate intervention simulator