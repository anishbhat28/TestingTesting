from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import hazards, places, routing
import json, db, os
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
DB = db.DB
SEEDS = os.path.join(os.path.dirname(__file__), "seeds")
seed_path = os.path.join(SEEDS, "hazards_seed.json")
if os.path.exists(seed_path):
    with open(seed_path, "r", encoding="utf-8") as f:
        seed_hazards = json.load(f)
        for i, h in enumerate(seed_hazards, start=1):
            if "id" not in h:
                h["id"] = i
            if "created_at" not in h:
                h["created_at"] = "2024-01-01T00:00:00"
            DB["hazards"].append(h)
@app.get("/api/health")
def health():
    return {"ok": True}
app.include_router(hazards.router, prefix="/api", tags=["hazards"])
app.include_router(places.router,  prefix="/api", tags=["places"])
app.include_router(routing.router, prefix="/api", tags=["routing"])



