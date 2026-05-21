import { useEffect, useState } from "react";
import { Loader2, Send, Star } from "lucide-react";
import { ask, initAuth, submitFeedback } from "../lib/api";
import {
  cacheAnswer,
  findCachedAnswer,
  getCachedEquipment,
} from "../lib/offlineCache";
import { useOnline } from "../hooks/useOnline";
import type { AskResponse, Equipment } from "../types";

const DEMO_QUESTION =
  "The HVAC controller is showing error code E47. What does it mean and what should I inspect?";

export default function AskPage() {
  const online = useOnline();
  const [question, setQuestion] = useState("");
  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [rating, setRating] = useState(0);
  const [fromCache, setFromCache] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    initAuth();
    getCachedEquipment().then(setEquipment);
  }, []);

  async function handleAsk(q?: string) {
    const text = (q ?? question).trim();
    if (!text) return;
    setError(null);
    setLoading(true);
    setResult(null);
    setFromCache(false);
    setRating(0);

    const cached = await findCachedAnswer(text, equipment?.id);
    if (cached && !online) {
      setResult(cached.response);
      setFromCache(true);
      setLoading(false);
      return;
    }

    try {
      if (cached && online) {
        setResult(cached.response);
        setFromCache(true);
      }
      const res = await ask(text, equipment?.id);
      setResult(res);
      await cacheAnswer(text, res, equipment?.id);
    } catch {
      if (cached) {
        setResult(cached.response);
        setFromCache(true);
      } else {
        setError("Could not reach server. Scan an asset and try a cached question offline.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {equipment && (
        <div className="card" style={{ marginBottom: "1rem" }}>
          <span className="badge">Asset context</span>
          <p style={{ margin: "0.5rem 0 0", fontWeight: 600 }}>{equipment.name}</p>
          <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--muted)" }}>
            {equipment.asset_tag} · {equipment.location}
          </p>
        </div>
      )}

      <div className="card">
        <label htmlFor="question" style={{ fontWeight: 600 }}>
          Ask the manual
        </label>
        <textarea
          id="question"
          className="textarea"
          style={{ marginTop: "0.5rem" }}
          placeholder="e.g. Error code E47 — what should I inspect?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem", flexWrap: "wrap" }}>
          <button
            type="button"
            className="btn btn-primary"
            disabled={loading}
            onClick={() => handleAsk()}
          >
            {loading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
            Get answer
          </button>
          <button
            type="button"
            className="btn btn-outline"
            onClick={() => {
              setQuestion(DEMO_QUESTION);
              handleAsk(DEMO_QUESTION);
            }}
          >
            Try E47 demo
          </button>
        </div>
      </div>

      {error && (
        <p style={{ color: "var(--danger)", marginTop: "1rem" }}>{error}</p>
      )}

      {result && (
        <div className="card" style={{ marginTop: "1rem" }}>
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
            <span className={`badge badge-${result.confidence === "high" ? "high" : ""}`}>
              Confidence: {result.confidence}
            </span>
            {fromCache && <span className="badge">Cached / offline</span>}
          </div>
          <div style={{ marginTop: "0.75rem", whiteSpace: "pre-wrap" }}>{result.answer}</div>

          {result.suggested_inspections.length > 0 && (
            <>
              <h3 style={{ fontSize: "1rem", marginTop: "1rem" }}>Suggested inspections</h3>
              <ul style={{ paddingLeft: "1.2rem", margin: 0 }}>
                {result.suggested_inspections.map((s) => (
                  <li key={s} style={{ marginBottom: "0.35rem" }}>
                    {s}
                  </li>
                ))}
              </ul>
            </>
          )}

          {result.citations.length > 0 && (
            <>
              <h3 style={{ fontSize: "1rem", marginTop: "1rem" }}>Sources</h3>
              {result.citations.map((c) => (
                <div
                  key={`${c.document_id}-${c.score}`}
                  style={{
                    borderLeft: "3px solid var(--accent)",
                    paddingLeft: "0.75rem",
                    marginBottom: "0.75rem",
                  }}
                >
                  <strong>{c.title}</strong>
                  <span className="badge" style={{ marginLeft: "0.5rem" }}>
                    {c.doc_type}
                  </span>
                  <p style={{ fontSize: "0.85rem", color: "var(--muted)", margin: "0.35rem 0" }}>
                    {c.excerpt.slice(0, 220)}…
                  </p>
                </div>
              ))}
            </>
          )}

          <div style={{ marginTop: "1rem" }}>
            <p style={{ fontSize: "0.85rem", color: "var(--muted)" }}>Rate this answer</p>
            <div style={{ display: "flex", gap: "0.25rem" }}>
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => {
                    setRating(n);
                    submitFeedback({
                      question: question || DEMO_QUESTION,
                      answer: result.answer,
                      rating: n,
                      equipment_id: equipment?.id,
                      citation_ids: result.citations.map((c) => c.document_id),
                    });
                  }}
                  aria-label={`Rate ${n}`}
                >
                  <Star size={18} fill={rating >= n ? "var(--warning)" : "none"} />
                </button>
              ))}
            </div>
            {rating > 0 && (
              <p style={{ fontSize: "0.8rem", color: "var(--success)" }}>
                Thanks — feedback improves retrieval for your team.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
