from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from analysis import generate_summary

app = FastAPI(title="SURF API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "SURF Satellite Urban Resilience Framework"}

@app.get("/analysis")
def analysis():
    return generate_summary()
