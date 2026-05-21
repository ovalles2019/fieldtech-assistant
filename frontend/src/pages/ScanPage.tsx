import { useState } from "react";
import { useNavigate } from "react-router-dom";
import QRScanner from "../components/QRScanner";
import { initAuth, resolveQR } from "../lib/api";
import { cacheEquipment } from "../lib/offlineCache";
import type { Equipment, ServiceTicket } from "../types";

export default function ScanPage() {
  const navigate = useNavigate();
  const [scanning, setScanning] = useState(false);
  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [tickets, setTickets] = useState<ServiceTicket[]>([]);
  const [manualPayload, setManualPayload] = useState("fieldtech://asset/hvac-ctrl-001");
  const [error, setError] = useState<string | null>(null);

  async function handlePayload(payload: string) {
    setScanning(false);
    setError(null);
    try {
      await initAuth();
      const res = await resolveQR(payload);
      setEquipment(res.equipment);
      setTickets(res.recent_tickets);
      await cacheEquipment(res.equipment);
      navigate("/", { state: { equipment: res.equipment } });
    } catch {
      setError("Unknown asset. Use a demo QR payload.");
    }
  }

  return (
    <div>
      <div className="card">
        <h2 style={{ margin: 0, fontSize: "1.1rem" }}>QR asset context</h2>
        <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
          Scan a panel QR to load equipment-specific manuals and service history into every answer.
        </p>
        {!scanning ? (
          <button type="button" className="btn btn-primary" onClick={() => setScanning(true)}>
            Open camera scanner
          </button>
        ) : (
          <QRScanner onScan={handlePayload} onClose={() => setScanning(false)} />
        )}

        <div style={{ marginTop: "1rem" }}>
          <label htmlFor="manual-qr" style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
            Or enter QR payload manually
          </label>
          <input
            id="manual-qr"
            className="input"
            style={{ marginTop: "0.35rem" }}
            value={manualPayload}
            onChange={(e) => setManualPayload(e.target.value)}
          />
          <button
            type="button"
            className="btn btn-outline"
            style={{ marginTop: "0.5rem" }}
            onClick={() => handlePayload(manualPayload)}
          >
            Load asset
          </button>
        </div>
        {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
      </div>

      {equipment && (
        <div className="card" style={{ marginTop: "1rem" }}>
          <h3 style={{ margin: 0 }}>{equipment.name}</h3>
          <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
            {equipment.manufacturer} {equipment.model}
          </p>
          {tickets.length > 0 && (
            <>
              <p style={{ fontWeight: 600, marginBottom: "0.5rem" }}>Recent tickets</p>
              <ul style={{ margin: 0, paddingLeft: "1.2rem" }}>
                {tickets.map((t) => (
                  <li key={t.id}>
                    {t.title} — {t.status}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
