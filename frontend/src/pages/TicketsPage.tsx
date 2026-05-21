import { useEffect, useState } from "react";
import { initAuth, createTicket } from "../lib/api";
import { getCachedEquipment } from "../lib/offlineCache";
import type { Equipment } from "../types";

export default function TicketsPage() {
  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [errorCodes, setErrorCodes] = useState("E47");
  const [submitted, setSubmitted] = useState<string | null>(null);

  useEffect(() => {
    getCachedEquipment().then((eq) => {
      setEquipment(eq);
      if (eq?.id.includes("hvac")) {
        setTitle("HVAC communication fault — E47");
        setDescription("Indoor/outdoor comm lost per technician inspection. Following manual sequence.");
      }
    });
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!equipment) return;
    await initAuth();
    const ticket = await createTicket({
      equipment_id: equipment.id,
      title,
      description,
      priority,
      error_codes: errorCodes.split(",").map((s) => s.trim()).filter(Boolean),
    });
    setSubmitted(ticket.id);
  }

  return (
    <div>
      <div className="card">
        <h2 style={{ margin: 0, fontSize: "1.1rem" }}>Service ticket</h2>
        <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
          Generate a ticket from the jobsite with linked asset and error codes.
        </p>
        {!equipment ? (
          <p style={{ color: "var(--warning)" }}>Scan or select an asset first.</p>
        ) : (
          <p style={{ fontSize: "0.9rem" }}>
            Asset: <strong>{equipment.asset_tag}</strong>
          </p>
        )}
      </div>

      <form className="card" style={{ marginTop: "1rem" }} onSubmit={handleSubmit}>
        <label>Title</label>
        <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <label style={{ display: "block", marginTop: "0.75rem" }}>Description</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
        <label style={{ display: "block", marginTop: "0.75rem" }}>Error codes (comma-separated)</label>
        <input className="input" value={errorCodes} onChange={(e) => setErrorCodes(e.target.value)} />
        <label style={{ display: "block", marginTop: "0.75rem" }}>Priority</label>
        <select
          className="input"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <button
          type="submit"
          className="btn btn-primary"
          style={{ marginTop: "1rem", width: "100%" }}
          disabled={!equipment}
        >
          Create ticket
        </button>
        {submitted && (
          <p style={{ color: "var(--success)", marginTop: "0.75rem" }}>
            Ticket created: {submitted.slice(0, 8)}…
          </p>
        )}
      </form>
    </div>
  );
}
