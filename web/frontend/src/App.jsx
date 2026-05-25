import { useState } from "react";
import Standings from "./pages/Standings";
import Schedule from "./pages/Schedule";

const PAGES = ["Standings", "Schedule", "Race", "Telemetry"];

export default function App() {
  const [page, setPage] = useState("Standings");

  return (
    <div style={{ display: "flex", background: "#111", minHeight: "100vh", color: "#eee", fontFamily: "sans-serif" }}>
      <aside style={{ width: 180, background: "#0d0d0d", borderRight: "1px solid #222", padding: "20px 0" }}>
        <div style={{ color: "#e8002d", fontWeight: 900, fontSize: 20, padding: "0 16px 20px" }}>F1 DASHBOARD</div>
        {PAGES.map(p => (
          <div key={p} onClick={() => setPage(p)}
            style={{ padding: "10px 16px", cursor: "pointer", color: page === p ? "#e8002d" : "#888", borderLeft: page === p ? "3px solid #e8002d" : "3px solid transparent", background: page === p ? "#1a0508" : "transparent" }}>
            {p}
          </div>
        ))}
      </aside>
      <main style={{ flex: 1, padding: 24 }}>
        {page === "Standings" && <Standings />}
        {page === "Schedule" && <Schedule />}
        {page === "Race" && <div>Race — yakında</div>}
        {page === "Telemetry" && <div>Telemetry — yakında</div>}
      </main>
    </div>
  );
}
