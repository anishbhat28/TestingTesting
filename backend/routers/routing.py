from fastapi import APIRouter, Query
from physics_utils import Light, Hazard, edge_metrics
import json, os, db, time
from datetime import datetime
router = APIRouter()
BASE = os.path.join(os.path.dirname(__file__), "..", "seeds")
DB = db.DB
def load(name: str):
    with open(os.path.join(BASE, name), "r", encoding="utf-8") as f:
        return json.load(f)
try:
    WEATHER = load("weather.json")
except Exception:
    WEATHER = {"Ta_C": 12.0, "V_ms": 3.0, "RH": 70.0}

DEMO_ROUTES = [
    [(32.7159, -117.1617), (32.7139, -117.1607), (32.7127, -117.1587)],
    [(32.7159, -117.1617), (32.7150, -117.1598), (32.7127, -117.1587)],
    [(32.7159, -117.1617), (32.7149, -117.1625), (32.7131, -117.1601), (32.7127, -117.1587)]
]
@router.get("/route")
def route(
    frm: str = Query(..., description="lng,lat"),
    to: str = Query(..., description="lng,lat"),
    k: int = Query(3, description="Number of routes")
):
    lights = [Light(**x) for x in load("lights.json")]
    vantages = [(p["lat"], p["lng"]) for p in load("places.json")]
    hazards = [
        Hazard(lat=h["lat"], lng=h["lng"], severity=h.get("severity", 2))
        for h in DB["hazards"]
    ]
    Ta_C = WEATHER.get("Ta_C", 12.0)
    V_ms = WEATHER.get("V_ms", 3.0)
    RH = WEATHER.get("RH", 70.0)   
    result = []
    for poly in DEMO_ROUTES[:max(1, min(k, len(DEMO_ROUTES)))]:
        m = edge_metrics(
            poly,
            lights=lights,
            hazards=hazards,
            vantages=vantages,
            Ta_C=Ta_C,
            V_ms=V_ms,
            RH=RH,
            visibility_km=12.0
        )
       
        polyline = [[p[0], p[1]] for p in poly]
        result.append({"polyline": polyline, **m})
    
    result.sort(key=lambda r: r["cost"])
    return {"routes": result}
