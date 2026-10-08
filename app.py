from fastapi import FastAPI
from core.recommendation import recommend

app = FastAPI(title="SURF")

@app.get("/")
def home():
    return {
        "project": "SURF",
        "description": "Satellite Urban Resilience Framework"
    }

@app.get("/analyze")
def analyze():
    return recommend()