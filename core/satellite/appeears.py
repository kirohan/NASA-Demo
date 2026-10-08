"""
SURF — Satellite Urban Resilience Framework
NASA AppEEARS API Client
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
import requests

from config import APPEEARS_API_URL, EARTHDATA_USERNAME, EARTHDATA_PASSWORD, EARTHDATA_TOKEN

logger = logging.getLogger(__name__)

class AppEEARSClient:
    def __init__(self, base_url: str = APPEEARS_API_URL, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token or EARTHDATA_TOKEN
        self.username = EARTHDATA_USERNAME
        self.password = EARTHDATA_PASSWORD
        self.session = requests.Session()
        self._authenticated = False

    def authenticate(self) -> bool:
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self._authenticated = True
            return True
        return False

    def list_products(self) -> List[Dict[str, Any]]:
        return [
            {"ProductAndVersion": "MOD11A2.061", "Description": "MODIS/Terra LST 8-Day 1km", "Platform": "Terra"},
            {"ProductAndVersion": "MOD13Q1.061", "Description": "MODIS/Terra NDVI 16-Day 250m", "Platform": "Terra"},
            {"ProductAndVersion": "ECO2LSTE.001", "Description": "ECOSTRESS LST Daily 70m", "Platform": "ISS"},
            {"ProductAndVersion": "NASADEM_NC.001", "Description": "NASADEM Global 30m DEM", "Platform": "SRTM/NASADEM"}
        ]
