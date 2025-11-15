
const API = import.meta.env.VITE_API||"http://localhost:8000/api";
export async function getPlace() {
    const s = await fetch(`${API}/places`);
    return s.json();
  }
  export async function getHazard() {
    const r = await fetch(`${API}/hazards`);
    return r.json();
  }
export async function postHazard(lat: number, lng: number, severity = 3) {
    const t = await fetch(`${API}/hazards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat, lng, severity, type: "general" })
    });
    return t.json();}
    export async function getRoute(from: [number, number], to: [number, number]) {
        const params = new URLSearchParams({
          frm: `${from[0]},${from[1]}`,
          to: `${to[0]},${to[1]}`,
          k: "3"
        });
        const r = await fetch(`${API}/route?${params.toString()}`);
        return r.json();
      }