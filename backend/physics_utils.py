from dataclasses import dataclass
from typing import List
import math, time
import numpy as np
EARTH_R = 6371000.0  #this value is in meters 
def haversine_m(a, b):
    (lat1, lng1), (lat2, lng2) = a, b
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    s = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(s))
def beer_lambert_law(r, visibility_km=12.0):
    if visibility_km <= 0:
        return 1.0
    k = 3.912 / (visibility_km * 1000.0)
    return math.exp(-k * r)


@dataclass
class Light:
    lat: float
    lng: float
    I_cd: float = 3000.0  #luminous intensity


@dataclass
class Hazard:
    lat: float
    lng: float
    severity: int = 2
    created_at: float = time.time()
def lux_at_point(p, lights: List[Light], visibility_km=12.0, cutoff_m=80.0):
    E = 0.0
    for L in lights:
        r = haversine_m(p, (L.lat, L.lng))
        r = max(1.0, r)
        if r > cutoff_m:
            continue
        E += (L.I_cd / (r * r)) * beer_lambert_law(r, visibility_km)
    return min(E, 200.0)
def hazard_field(p, hazards: List[Hazard], rho_m=75.0, half_life_h=6.0):
    out = 0.0
    now = time.time()
    for h in hazards:
        age_h = (now - h.created_at) / 3600.0
        decay = math.exp(-math.log(2) * max(age_h, 0) / half_life_h)
        d = haversine_m(p, (h.lat, h.lng))
        out += ((0.5 + 0.25 * (h.severity - 1)) * decay) / (1 + (d / rho_m) ** 2)
    return out
def exposure_proxy(p, vantages, radius_m=120.0):
    if not vantages:
        return 0.0
    near = [v for v in vantages if haversine_m(p, v) <= radius_m]
    return len(near) / max(1, len(vantages))
def wind_chill_C(Ta_C, V_ms):
    V = max(V_ms, 1.0)
    return 13.12 + 0.6215 * Ta_C - 11.37 * (V ** 0.16) + 0.3965 * Ta_C * (V ** 0.16)
def heat_index_C(T_C, RH):
    T_F = T_C * 9 / 5 + 32
    HI = (
        -42.379
        + 2.04901523 * T_F
        + 10.14333127 * RH
        - 0.22475541 * T_F * RH
        - 6.83783e-3 * T_F ** 2
        - 5.481717e-2 * RH ** 2
        + 1.22874e-3 * T_F ** 2 * RH
        + 8.5282e-4 * T_F * RH ** 2
        - 1.99e-6 * T_F ** 2 * RH ** 2
    )
    return (HI - 32) * 5 / 9
def edge_metrics(
    poly,
    *,
    lights,
    hazards,
    vantages,
    Ta_C=12.0,
    V_ms=3.0,
    RH=70.0,
    visibility_km=12.0
):
    if len(poly) < 2:
        return {
            "length_m": 0,
            "lux_avg": 0,
            "lux_min": 0,
            "expo_avg": 0,
            "pot": 0,
            "T_wc": 0,
            "HI": 0,
            "safety_score": 0,
            "cost": 0,
        }
    pts = [poly[0]]
    step = 40.0
    acc = 0.0
    for i in range(1, len(poly)):
        seg = haversine_m(poly[i - 1], poly[i])
        acc += seg
        if acc >= step:
            pts.append(poly[i])
            acc = 0.0
    if pts[-1] != poly[-1]:
        pts.append(poly[-1])
    L = [lux_at_point(p, lights, visibility_km) for p in pts]
    E = [exposure_proxy(p, vantages) for p in pts]
    H = [hazard_field(p, hazards) for p in pts]
    length = sum(haversine_m(poly[i - 1], poly[i]) for i in range(1, len(poly)))
    lux_avg = float(np.mean(L))
    lux_min = float(np.min(L))
    expo_avg = float(np.mean(E))
    pot = float(np.mean(H))
    T_wc = wind_chill_C(Ta_C, V_ms)
    HI = heat_index_C(Ta_C, RH)
    cold_pen = max(0.0, 10.0 - T_wc)
    heat_pen = max(0.0, HI - 32.0)
    WX_pen = (cold_pen + heat_pen) / 10.0
    unsafe = (
        0.35 * max(0.0, 10.0 - lux_avg)
        + 0.35 * (1.0 - expo_avg)
        + 0.20 * pot
        + 0.10 * WX_pen
    )
    safety_score = float(max(0.0, 100.0 - 100.0 * min(1.0, unsafe)))
    cost = (
        (length / 100.0)
        + 0.8 * max(0.0, 10.0 - lux_avg)
        - 0.6 * expo_avg
        + 0.7 * pot
        + 0.5 * cold_pen
        + 0.5 * heat_pen
    )
    return {
        "length_m": float(length),
        "lux_avg": lux_avg,
        "lux_min": lux_min,
        "expo_avg": expo_avg,
        "pot": pot,
        "T_wc": float(T_wc),
        "HI": float(HI),
        "safety_score": safety_score,
        "cost": float(cost),
    }

