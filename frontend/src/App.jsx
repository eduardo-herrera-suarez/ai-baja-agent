import { useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline
} from "react-leaflet";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const LOCATIONS = {
  Tijuana: [32.5149, -117.0382],
  Rosarito: [32.3661, -117.055],
  "Puerto Nuevo": [32.247, -116.875],
  Ensenada: [31.8667, -116.6]
};

function MapView({ segments = [] }) {
  const points = segments
    .flatMap((s) => [LOCATIONS[s.from], LOCATIONS[s.to]])
    .filter(Boolean);

  if (!points.length) return null;

  return (
    <MapContainer
      center={points[0]}
      zoom={9}
      style={{ height: "400px", borderRadius: "12px" }}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      {points.map((pos, i) => (
        <Marker key={`${pos}-${i}`} position={pos}>
          <Popup>Stop {i + 1}</Popup>
        </Marker>
      ))}

      <Polyline positions={points} />
    </MapContainer>
  );
}

function Card({ title, children }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.05)",
        backdropFilter: "blur(10px)",
        border: "1px solid rgba(255,255,255,0.1)",
        padding: "20px",
        borderRadius: "16px"
      }}
    >
      <h3 style={{ marginBottom: "10px" }}>{title}</h3>
      {children}
    </div>
  );
}

export default function App() {
  const [message, setMessage] = useState("");
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | loading | success | error

  const sendMessage = async () => {
    if (!message.trim()) return;

    setStatus("loading");

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: "demo", message })
      });

      const json = await res.json();
      setData(json?.response || null);
      setStatus("success");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        background: "linear-gradient(135deg, #0f172a, #020617)",
        color: "white"
      }}
    >
      {/* LEFT PANEL */}
      <div
        style={{
          width: "30%",
          padding: "20px",
          borderRight: "1px solid #1e293b"
        }}
      >
        <h2 style={{ color: "#a78bfa" }}>🧠 AI Baja Agent</h2>
        <p style={{ color: "#94a3b8" }}>
          AI-powered travel planning with real-world routing
        </p>

        <textarea
          placeholder="Plan a 3-day Baja trip..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{ width: "100%", height: "100px", marginTop: "15px" }}
        />

        <button
          onClick={sendMessage}
          disabled={status === "loading"}
          style={{ marginTop: "15px", padding: "12px", width: "100%" }}
        >
          {status === "loading" ? "🧠 Thinking..." : "Generate Plan"}
        </button>

        {status === "loading" && (
          <p style={{ marginTop: "10px" }}>🚗 Optimizing route...</p>
        )}

        {status === "error" && (
          <p style={{ marginTop: "10px", color: "#f87171" }}>
            Something went wrong. Try again.
          </p>
        )}
      </div>

      {/* RIGHT PANEL */}
      <div
        style={{ width: "70%", padding: "20px", overflow: "auto" }}
      >
        {!data && status !== "loading" && (
          <div
            style={{
              textAlign: "center",
              marginTop: "100px",
              color: "#64748b"
            }}
          >
            <h2>🌎 Plan your next Baja trip</h2>
            <p>Try: "Plan a 3-day Baja beach trip"</p>
          </div>
        )}

        {data && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* ROUTE */}
            {data?.route && (
              <Card title="🚗 Route">
                <div
                  style={{
                    padding: "15px",
                    borderRadius: "12px",
                    background:
                      "linear-gradient(135deg, #6366f1, #8b5cf6)",
                    marginBottom: "15px"
                  }}
                >
                  <strong>
                    {data.route.summary?.total_distance_human} • {" "}
                    {data.route.summary?.total_duration_human}
                  </strong>
                  <p>{data.route.summary?.travel_style}</p>
                </div>

                <MapView segments={data.route.segments} />

                {data.route.segments?.map((s, i) => (
                  <div key={`${s.from}-${s.to}-${i}`}>
                    {s.from} → {s.to} ({s.distance_human})
                  </div>
                ))}
              </Card>
            )}

            {/* TRAVEL */}
            {data?.travel && (
              <Card title="📅 Travel">
                {Object.entries(data.travel).map(([day, items]) => (
                  <div key={day}>
                    <strong>{day}</strong>
                    {items.map((a, i) => (
                      <p key={i}>
                        {a.time} - {a.activity}
                      </p>
                    ))}
                  </div>
                ))}
              </Card>
            )}

            {/* FOOD */}
            {data?.food && (
              <Card title="🍽️ Food">
                {Object.entries(data.food).map(([day, items]) => (
                  <div key={day}>
                    <strong>{day}</strong>
                    {items.map((f, i) => (
                      <p key={i}>
                        {f.meal}: {f.description}
                      </p>
                    ))}
                  </div>
                ))}
              </Card>
            )}

            {/* BUDGET */}
            {data?.budget && (
              <Card title="💰 Budget">
                <p>Accommodation: ${data.budget.accommodation}</p>
                <p>Food: ${data.budget.food}</p>
                <p>Transport: ${data.budget.transportation}</p>
                <p>Activities: ${data.budget.activities}</p>
                <strong>Total: ${data.budget.total}</strong>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
