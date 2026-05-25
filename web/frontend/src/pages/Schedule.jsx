import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export default function Schedule() {
  const [year, setYear] = useState(2024);
  const [races, setRaces] = useState([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/schedule/${year}`);
      setRaces(res.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  return (
    <div>
      <h2 style={{ color: "#e8002d", marginBottom: 16 }}>📅 Race Schedule</h2>
      <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
        <input type="number" value={year} onChange={e => setYear(e.target.value)}
          style={{ background: "#222", border: "1px solid #333", color: "#eee", padding: "6px 12px", borderRadius: 4, width: 80 }} />
        <button onClick={load}
          style={{ background: "#e8002d", color: "white", border: "none", padding: "6px 18px", borderRadius: 4, cursor: "pointer", fontWeight: 700 }}>
          {loading ? "Yükleniyor..." : "Load"}
        </button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        {races.map((r, i) => (
          <div key={i} style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 6, padding: "14px 16px" }}>
            <div style={{ color: "#e8002d", fontWeight: 700, fontSize: 12, marginBottom: 6 }}>R{r.round || i + 1}</div>
            <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{r.name || r.raceName}</div>
            <div style={{ fontSize: 12, color: "#666" }}>{r.date}</div>
            <div style={{ fontSize: 12, color: "#555", marginTop: 2 }}>{r.circuit || r.circuitName}</div>
          </div>
        ))}
      </div>
    </div>
  );
}