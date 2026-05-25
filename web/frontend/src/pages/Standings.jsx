import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export default function Standings() {
  const [year, setYear] = useState(2024);
  const [drivers, setDrivers] = useState([]);
  const [constructors, setConstructors] = useState([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const [d, c] = await Promise.all([
        axios.get(`${API}/standings/${year}/drivers`),
        axios.get(`${API}/standings/${year}/constructors`),
      ]);
      setDrivers(d.data);
      setConstructors(c.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  return (
    <div>
      <h2 style={{ color: "#e8002d", marginBottom: 16 }}>🏆 Season Standings</h2>
      <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
        <input type="number" value={year} onChange={e => setYear(e.target.value)}
          style={{ background: "#222", border: "1px solid #333", color: "#eee", padding: "6px 12px", borderRadius: 4, width: 80 }} />
        <button onClick={load}
          style={{ background: "#e8002d", color: "white", border: "none", padding: "6px 18px", borderRadius: 4, cursor: "pointer", fontWeight: 700 }}>
          {loading ? "Yükleniyor..." : "Load"}
        </button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ background: "#1a1a1a", borderRadius: 6, border: "1px solid #2a2a2a" }}>
          <div style={{ padding: "12px 16px", borderBottom: "1px solid #2a2a2a", fontWeight: 700, textAlign: "center" }}>Driver Standings</div>
          {drivers.map((d, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 16px", borderBottom: "1px solid #1d1d1d" }}>
              <span style={{ color: "#e8002d", fontWeight: 700, width: 30 }}>P{d.position}</span>
              <span style={{ fontWeight: 700, width: 40 }}>{d.code || d.driverCode}</span>
              <span style={{ flex: 1, color: "#888", fontSize: 13 }}>{d.name || d.driverName}</span>
              <span style={{ fontWeight: 700 }}>{d.points} pts</span>
            </div>
          ))}
        </div>
        <div style={{ background: "#1a1a1a", borderRadius: 6, border: "1px solid #2a2a2a" }}>
          <div style={{ padding: "12px 16px", borderBottom: "1px solid #2a2a2a", fontWeight: 700, textAlign: "center" }}>Constructor Standings</div>
          {constructors.map((c, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 16px", borderBottom: "1px solid #1d1d1d" }}>
              <span style={{ color: "#e8002d", fontWeight: 700, width: 30 }}>P{c.position}</span>
              <span style={{ flex: 1, fontWeight: 600 }}>{c.name || c.constructorName}</span>
              <span style={{ fontWeight: 700 }}>{c.points} pts</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}