import { useEffect, useState } from "react";
import { api, humanError, type Health } from "../lib/api";

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

/** Error/answer output block; renders nothing when empty. Errors are humanized. */
export function Output({ text, error }: { text?: string; error?: unknown }) {
  if (error)
    return (
      <div className="output" style={{ borderColor: "var(--brand)", color: "var(--brand-dark)" }}>
        <i className="bi bi-exclamation-triangle" style={{ marginRight: 6 }} />
        {typeof error === "string" ? error : humanError(error)}
      </div>
    );
  if (!text) return null;
  return <div className="output">{text}</div>;
}

/** Slim, dismissible-free banner shown site-wide while the browser is offline. */
export function OfflineBanner() {
  const online = useOnline();
  if (online) return null;
  return (
    <div className="offline-banner" role="status">
      <i className="bi bi-wifi-off" /> You're offline — on-device features keep working. Cloud AI
      (Polly, chat) will resume when you reconnect.
    </div>
  );
}

/**
 * Fire `onSubmit` when the user presses ⌘/Ctrl+Enter inside a field. Attach the
 * returned handler to a textarea/input's `onKeyDown`.
 */
export function submitOnCmdEnter(onSubmit: () => void) {
  return (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      onSubmit();
    }
  };
}

/** Tracks online/offline state (browser connectivity). Polly features gate on this. */
export function useOnline(): boolean {
  const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);
  return online;
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
