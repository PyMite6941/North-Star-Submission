import { useEffect, useRef, useState } from "react";
import { api, type FocusStats } from "../lib/api";
import { Button } from "../components/ui";

const PRESETS = [
  { label: "Focus 25", work: 25 },
  { label: "Focus 50", work: 50 },
  { label: "Short 15", work: 15 },
];

export default function Pomodoro() {
  const [minutes, setMinutes] = useState(25);
  const [remaining, setRemaining] = useState(25 * 60);
  const [running, setRunning] = useState(false);
  const [task, setTask] = useState("");
  const [stats, setStats] = useState<FocusStats | null>(null);
  const tick = useRef<number | null>(null);

  const loadStats = () => api.focusStats().then(setStats).catch(() => setStats(null));
  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    if (!running) return;
    tick.current = window.setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          window.clearInterval(tick.current!);
          setRunning(false);
          api.logPomodoro(minutes, task).then(setStats).catch(() => {});
          return 0;
        }
        return r - 1;
      });
    }, 1000);
    return () => window.clearInterval(tick.current!);
  }, [running, minutes, task]);

  function setPreset(m: number) {
    setMinutes(m);
    setRemaining(m * 60);
    setRunning(false);
  }
  function reset() {
    setRunning(false);
    setRemaining(minutes * 60);
  }

  const mm = String(Math.floor(remaining / 60)).padStart(2, "0");
  const ss = String(remaining % 60).padStart(2, "0");
  const pct = 100 - (remaining / (minutes * 60)) * 100;

  return (
    <>
      <h2 className="section-title">Pomodoro</h2>
      <p className="section-sub">Focus in intervals. Completed sessions are logged and build a streak.</p>

      <div className="grid cols-2">
        <div className="card" style={{ textAlign: "center" }}>
          <div className="chips" style={{ justifyContent: "center" }}>
            {PRESETS.map((p) => (
              <span key={p.label} className={`chip${minutes === p.work ? " active" : ""}`} onClick={() => setPreset(p.work)}>
                {p.label}
              </span>
            ))}
          </div>
          <div style={{ fontFamily: "var(--font-head)", fontSize: "5rem", fontWeight: 800, margin: "10px 0", color: "var(--dark)" }}>
            {mm}:{ss}
          </div>
          <div style={{ height: 8, background: "var(--bg-alt)", borderRadius: 999, overflow: "hidden", marginBottom: 16 }}>
            <div style={{ width: `${pct}%`, height: "100%", background: "linear-gradient(90deg, var(--brand), var(--orange))" }} />
          </div>
          <input type="text" placeholder="What are you focusing on?" value={task} onChange={(e) => setTask(e.target.value)} />
          <div className="row" style={{ justifyContent: "center", marginTop: 12 }}>
            {!running ? (
              <Button onClick={() => setRunning(true)} icon="play-fill">
                Start
              </Button>
            ) : (
              <Button onClick={() => setRunning(false)} icon="pause-fill">
                Pause
              </Button>
            )}
            <Button onClick={reset} ghost icon="arrow-counterclockwise">
              Reset
            </Button>
          </div>
        </div>

        <div className="card">
          <h3>Your focus</h3>
          {stats ? (
            <div className="grid cols-2" style={{ marginTop: 10 }}>
              <Stat label="Today" value={`${stats.today_minutes} min`} />
              <Stat label="Streak" value={`${stats.streak_days} days`} />
              <Stat label="Sessions" value={String(stats.sessions)} />
              <Stat label="Total" value={`${Math.round(stats.total_minutes / 60)} h`} />
            </div>
          ) : (
            <p className="muted">No sessions yet — finish a timer to start your streak.</p>
          )}
        </div>
      </div>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ padding: 14, background: "var(--bg-alt)", borderRadius: 12 }}>
      <div style={{ fontFamily: "var(--font-head)", fontSize: "1.5rem", fontWeight: 800, color: "var(--brand)" }}>{value}</div>
      <div className="muted" style={{ fontSize: ".85rem" }}>{label}</div>
    </div>
  );
}
