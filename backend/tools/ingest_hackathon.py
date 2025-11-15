import csv, json, os, sys
from datetime import datetime, timezone 
def fill_rows(path):
    with open(path, newline = " ", encoding = "utf-8-sig") as f:
        for row in csv.DictReader(f):
            yield {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
def to_float(x, default = None):
    try: 
        return float(x)
    except Exception:
        return default
def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist = True)
    with open(path, "w", encoding = "utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent = 2)
def shelters_to_places(csv_path):
    #basically converting csv to json for the places router
    lat_k = {"lat", "latitude", "y", "Y", "LAT", "Latitude"}
    lon_k = {"lon", "lng", "longitude", "x", "X", "LON", "LONGITUDE", "Longitude"}
    name_k = {"name", "shelter_name", "facility", "Facility", "Name", "SITE_NAME"}
    pets_k = {"pets", "pet_friendly", "Pets", "AllowsPets"}
    storage_k = {"storage", "Storage", "lockers", "Lockers"}
    places = []
    for r in fill_rows(csv_path):
        lat = next((to_float(r[k]) for k in lat_k if k in r), None)
        lon = next((to_float(r[k]) for k in lon_k if k in r), None)
        if lat is None or lon is None:
            continue 
        name = next((r[k] for k in name_k if k in r), "Shelter")
        pets = next(((str(r[k]).lower() in {"1", "true", "yes", "y"}) for k in pets_k if k in r), False)
        storage = next(((str(r[k]).lower() in {"1", "true", "yes", "y"}) for k in storage_k if k in r), False)
        base = 3.0
        if pets: base += 0.5
        if storage: base+= 0.5
        dignity = max(1.0, min(5.0, base))
        places.append({
            "name": name,
            "type": "shelter",
            "lat": lat,
            "lng": lon,
            "pets": pets,
            "storage": storage,
            "dignity_score": dignity 
            })
    return places
def encampments_to_hazards(encamp_csv):
    lat_k = {"lat","latitude","Y","LAT"}
    lon_k = {"lon","lng","longitude","X","LON"}
    sev_k = {"severity","Severity"}
    date_k = {"created","created_at","CreatedDate","CreateDate","Date","date"}
    hazards=[]
    for r in fill_rows(encamp_csv):
        lat = next((to_float(r[k]) for k in lat_k if k in r), None)
        lon = next((to_float(r[k]) for k in lon_k if k in r), None)
        if lat is None or lon is None: continue
        sev = int(next((to_float(r[k]) for k in sev_k if k in r and r[k]), 2))
        dt_raw = next((r[k] for k in date_k if k in r and r[k]), None)
        created_iso = None
        if dt_raw:
            try:
                created_iso = datetime.fromisoformat(dt_raw.replace("Z","")).isoformat()
            except:
                created_iso = datetime.now(timezone.utc).isoformat()
        else:
            created_iso = datetime.now(timezone.utc).isoformat()

        hazards.append({
            "lat": lat,
            "lng": lon,
            "type": "encampment",
            "severity": sev,
            "created_at": created_iso
        })
    return hazards
def main():
    if len(sys.argv) < 3:
        print("Usage: python ingest_hackathon.py shelters.csv encampments.csv [out_dir]", file=sys.stderr)
        sys.exit(1)
    shelters_csv = sys.argv[1]
    encamp_csv   = sys.argv[2]
    out_dir      = sys.argv[3] if len(sys.argv) > 3 else "../seeds"
    places  = shelters_to_places(shelters_csv)
    hazards = encampments_to_hazards(encamp_csv)
    write_json(os.path.join(out_dir, "places.json"), places)
    write_json(os.path.join(out_dir, "hazards_seed.json"), hazards)
if __name__ == "__main__":
    main()