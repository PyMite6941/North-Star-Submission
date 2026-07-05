import { useEffect, useState } from "react";
import { api, type Health } from "../lib/api";

/** Primary action button with a built-in loading state. */
export function Button(props: {
  onClick: () => void;
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  ghost?: boolean;
  icon?: string;
}) {
  const { onClick, loading, disabled, children, ghost, icon } = props;
  return (
    <button className={`btn${ghost ? " ghost" : ""}`} onClick={onClick} disabled={loading || disabled}>
      {loading ? <span className="spinner" /> : icon ? <i className={`bi bi-${icon}`} /> : null}
      {children}
    </button>
  );
}

/** Error/answer output block; renders nothing when empty. */
export function Output({ text, error }: { text?: string; error?: string }) {
  if (error) return <div className="output" style={{ borderColor: "var(--brand)", color: "var(--brand-dark)" }}>{error}</div>;
  if (!text) return null;
  return <div className="output">{text}</div>;
}

/** Live backend/Ollama status pill (polls /health once). */
export function BackendStatus() {
  const [h, setH] = useState<Health | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => {
    api.health().then(setH).catch(() => setErr(true));
  }, []);
  if (err) return <span className="badge off">API offline</span>;
  if (!h) return <span className="badge">checking…</span>;
  return h.ollama_reachable ? (
    <span className="badge ok" title={h.models.join(", ")}>
      ● {h.models.length} models
    </span>
  ) : (
    <span className="badge off">Ollama offline</span>
  );
}
