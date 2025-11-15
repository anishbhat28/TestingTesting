from fastapi import APIRouter
import json, os
router = APIRouter()
BASE = os.path.join(os.path.dirname(__file__), "..", "seeds")
def load(name: str):
    with open(os.path.join(BASE, name), "r", encoding = "utf-8") as f:
        return json.load(f)
@router.get("/places")
def places(ptype: str | None = None):
    item = load("places.json")
    return [p for p in item if (ptype is None or p.get("type") == ptype)]
    


