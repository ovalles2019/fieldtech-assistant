import { useEffect, useState } from "react";
import { initAuth, listEquipment } from "../lib/api";
import { cacheEquipment } from "../lib/offlineCache";
import type { Equipment } from "../types";

export default function AssetsPage() {
  const [assets, setAssets] = useState<Equipment[]>([]);

  useEffect(() => {
    initAuth().then(() => listEquipment().then(setAssets));
  }, []);

  return (
    <div>
      <div className="card">
        <h2 style={{ margin: 0, fontSize: "1.1rem" }}>Equipment registry</h2>
        <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
          Select an asset to scope RAG retrieval to its manuals and service records.
        </p>
      </div>
      {assets.map((a) => (
        <button
          key={a.id}
          type="button"
          className="card"
          style={{
            marginTop: "0.75rem",
            width: "100%",
            textAlign: "left",
            cursor: "pointer",
            color: "inherit",
          }}
          onClick={() => cacheEquipment(a)}
        >
          <strong>{a.name}</strong>
          <p style={{ margin: "0.25rem 0", color: "var(--muted)", fontSize: "0.85rem" }}>
            {a.asset_tag} · {a.location}
          </p>
          <span className="badge">{a.manufacturer}</span>
        </button>
      ))}
    </div>
  );
}
