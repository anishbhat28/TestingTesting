import { useEffect, useRef, useState } from "react";
import maplibregl, { LngLatLike } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";
import { getPlace, postHazard, getRoute } from "../services/api";
const CENTER: LngLatLike = [-117.1617, 32.7159];
type Place = {
  name: string;
  type: string;
  lat: number;
  lng: number;
  pets?: boolean;
  storage?: boolean;
  dignity_score?: number;
};
export default function MapView() {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const [map, setMap] = useState<maplibregl.Map | null>(null);
  const [route, setRoute] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any | null>(null);
  const [routeIdx, setRouteIdx] = useState(0);
  const [places, setPlaces] = useState<Place[]>([]);
  const [minDignity, setMinDignity] = useState<number>(1);
  useEffect(() => {
    const m = new maplibregl.Map({container: mapRef.current as HTMLDivElement, style: "https://demotiles.maplibre.org/style.json",center: CENTER,zoom: 14});
    m.addControl(new maplibregl.NavigationControl(), "top-right");
    m.on("load", async () => {
      m.addSource("route", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] }
      });
      m.addLayer({
        id: "route-solid",
        type: "line",
        source: "route",
        paint: { "line-color": "#16a34a", "line-width": 5 },
        filter: ["==", ["get", "rank"], 0]
      });
      m.addLayer({
        id: "route-dashed",
        type: "line",
        source: "route",
        paint: {
          "line-color": "#fde68a",
          "line-width": 4,
          "line-dasharray": [2, 2]
        },
        filter: [">", ["get", "rank"], 0]
      });
      const loadedPlaces: Place[] = await getPlace();
      setPlaces(loadedPlaces);
      loadedPlaces.forEach((p: Place) => {
        let color = "#22c55e"; 
        if (p.type === "shelter") {
          const d = p.dignity_score ?? 3;
          color = d >= 4 ? "#1e3a8a" : d >= 3 ? "#facc15" : "#f97316";
        }
        new maplibregl.Marker({ color })
          .setLngLat([p.lng, p.lat])
          .setPopup(
            new maplibregl.Popup().setHTML(
              `<b>${p.name}</b><br/>${p.type}${
                p.dignity_score
                  ? `<br/>Dignity: ${p.dignity_score.toFixed(1)}★`
                  : ""
              }`
            )
          )
          .addTo(m);
      });
      const from: [number, number] = [-117.1617, 32.7159];
      const to: [number, number] = [-117.1587, 32.7127];
      const data = await getRoute(from, to);
      setRoute(data.routes);
      drawRoutes(m, data.routes);
      setMetricsFrom(0, data.routes);
    });
    setMap(m);
    return () => {
      m.remove();
    };
  }, []);
  function drawRoutes(m: maplibregl.Map, list: any[]) {
    const fc = {
      type: "FeatureCollection",
      features: list.map((r: any, i: number) => ({
        type: "Feature",
        properties: { rank: i },
        geometry: {
          type: "LineString",
          coordinates: r.polyline.map((p: number[]) => [p[1], p[0]])
        }
      }))
    };
    (m.getSource("route") as any).setData(fc);
  }
  function setMetricsFrom(i: number, list: any[]) {
    const r = list[i];
    setMetrics({
      score: Math.round(r.safety_score),
      lux: r.lux_min.toFixed(1),
      expo: r.expo_avg.toFixed(2),
      len: Math.round(r.length_m)
    });
  }
  async function addHazardHere() {
    if (!map) return;
    const c = map.getCenter();
    await postHazard(c.lat, c.lng, 3);
    const data = await getRoute([-117.1617, 32.7159], [-117.1587, 32.7127]);
    setRoute(data.routes);
    drawRoutes(map!, data.routes);
    setRouteIdx(0);
    setMetricsFrom(0, data.routes);
    speak("Hazard reported. Switching to a safer route.");
  }
  function speak(text: string) {
    try {
      const u = new SpeechSynthesisUtterance(text);
      speechSynthesis.speak(u);
    } catch {}
  }
  function renderStars(score: number | undefined) {
    if (score === undefined || score <= 0) return "—";
    const full = Math.round(score); // 1..5
    return "★".repeat(full) + "☆".repeat(Math.max(0, 5 - full));
  }
  const filteredShelters = places.filter(
    (p) => p.type === "shelter" && (p.dignity_score ?? 1) >= minDignity
  );
  return (
    <>
      <div className="dignity-panel">
        <div className="dignity-header">
          <span>Shelter Dignity</span>
        </div>
        <div className="dignity-controls">
          <label>
            Min dignity:
            <select
              value={minDignity}
              onChange={(e) => setMinDignity(Number(e.target.value))}
            >
              <option value={1}>All</option>
              <option value={3}>3★+</option>
              <option value={4}>4★+</option>
            </select>
          </label>
        </div>
        <div className="dignity-list">
          {filteredShelters.length === 0 && (
            <div className="dignity-empty">No shelters available at this level</div>
          )}
          {filteredShelters.map((s) => (
            <div key={s.name} className="dignity-card">
              <div className="dignity-card-header">
                <span className="dignity-name">{s.name}</span>
                <span className="dignity-score">
                  {s.dignity_score?.toFixed(1)}★
                </span>
              </div>
              <div className="dignity-stars">{renderStars(s.dignity_score)}</div>
              <div className="dignity-tags">
                {s.pets && <span>Pets allowed here</span>}
                {s.storage && <span>Storage</span>}
                {!s.pets && !s.storage && <span>Basic shelter</span>}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="metrics">
        {metrics && (
          <>
            <div>
              SafetyScore: <b>{metrics.score}</b>
            </div>
            <div>
              Min Lux: <b>{metrics.lux}</b> | Exposure: <b>{metrics.expo}</b> |
              Length: <b>{metrics.len} m</b>
            </div>
            <button
              onClick={() => {
                const i = (routeIdx + 1) % route.length;
                setRouteIdx(i);
                setMetricsFrom(i, route);
              }}
            >
              Show next route
            </button>
            <button onClick={addHazardHere}>Report hazard</button>
          </>
        )}
      </div>
      <div ref={mapRef} className="map" />
    </>
  );
}