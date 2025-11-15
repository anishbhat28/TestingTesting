from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import List
import db 
router = APIRouter()
DB = db.DB
class HazardIn(BaseModel):
    lat: float
    lng: float
    type: str = "general"
    severity: int = 2 #I am just taking some random value here. Future version of app will include flexibility
class HazardGone(HazardIn):
    id: int
    created_at: str
@router.post("/hazards", response_model = HazardGone)
def make_hazard(h: HazardIn):
    _id = len(DB["hazards"]) + 1
    rec = {"id": _id,
    **h.model_dump(),
     "created_at": datetime.now(timezone.utc).isoformat()
    } 
    DB["hazards"].append(rec)
    return rec
@router.get("/hazards", response_model=List[HazardGone])
def list_hazards(hours: int = 12):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    out = [x for x in DB["hazards"]
           if datetime.fromisoformat(x["created_at"]) >= cutoff]
    return out

