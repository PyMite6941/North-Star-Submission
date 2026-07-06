import { useState } from "react";
import { api, type AnalyzeResult, type Schedule } from "../lib/api";
import { Button, Output } from "../components/ui";

export default function Fitness() {
  const [files, setFiles] = useState<File[]>([]);
  const [goal, setGoal] = useState("Run a sub-25 minute 5K");
  const [log, setLog] = useState(true);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function analyze() {
    if (files.length === 0) return;
    setLoading(true);
    setErr("");
    setResult(null);
    try {
      setResult(await api.fitnessAnalyzeUpload(files, goal, log));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  const [trend, setTrend] = useState<string>("");
  const [trendLoading, setTrendLoading] = useState(false);
  async function loadTrend() {
    setTrendLoading(true);
    try {
      const t = await api.fitnessTrend();
      setTrend(
        "message" in t
          ? String(t.message)
          : `Fitness (CTL): ${fmt(t.ctl)}   Fatigue (ATL): ${fmt(t.atl)}   Form (TSB): ${fmt(t.tsb)}\n` +
              `Sessions: ${t.n_sessions}   Total: ${fmt(t.total_distance_km)} km   Last 7d: ${fmt(t.last7_distance_km)} km`,
      );
    } catch (e) {
      setTrend(String(e));
    } finally {
      setTrendLoading(false);
    }
  }

  const [sgGoal, setSgGoal] = useState("Run a sub-25 minute 5K");
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [sgLoading, setSgLoading] = useState(false);
  const [sgErr, setSgErr] = useState("");
  async function makeSchedule() {
    setSgLoading(true);
    setSgErr("");
    setSchedule(null);
    try {
      setSchedule(await api.fitnessSchedule(sgGoal));
    } catch (e) {
      setSgErr(String(e));
    } finally {
      setSgLoading(false);
    }
  }

  function exportIcs() {
    if (!schedule) return;
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const today = new Date();
    const lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Polaris//Fitness//EN"];
    schedule.workouts.forEach((w, i) => {
      const target = Math.max(0, days.indexOf(w.day));
      const d = new Date(today);
      d.setDate(today.getDate() + ((target - today.getDay() + 7) % 7));
      const start = new Date(d.getFullYear(), d.getMonth(), d.getDate(), 7, 0);
      const end = new Date(start.getTime() + w.duration_min * 60000);
      const f = (x: Date) => x.toISOString().replace(/[-:]/g, "").split(".")[0];
      lines.push(
        "BEGIN:VEVENT",
        `UID:polaris-${Date.now()}-${i}@local`,
        `DTSTART:${f(start)}`,
        `DTEND:${f(end)}`,
        `SUMMARY:${w.title}`,
        `DESCRIPTION:${w.description.replace(/\n/g, " ")}`,
        "END:VEVENT",
      );
    });
    lines.push("END:VCALENDAR");
    const url = URL.createObjectURL(new Blob([lines.join("\r\n")], { type: "text/calendar" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "polaris_plan.ics";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <h2 className="section-title">Fitness</h2>
      <p className="section-sub">Upload activities for metrics, trends, and an AI-reviewed growth plan.</p>

      <div className="card">
        <h3>Analyze activity</h3>
        <p className="muted">Upload .fit / .tcx / .gpx / .csv / .json files.</p>
        <input
          type="file"
          multiple
          accept=".fit,.tcx,.gpx,.csv,.json"
          onChange={(e) => setFiles(Array.from(e.target.files ?? []))}
        />
        <label className="field">Goal</label>
        <input type="text" value={goal} onChange={(e) => setGoal(e.target.value)} />
        <label className="row" style={{ marginTop: 10, cursor: "pointer" }}>
          <input type="checkbox" checked={log} onChange={(e) => setLog(e.target.checked)} style={{ width: "auto" }} />
          <span className="muted">Log to progress history</span>
        </label>
        <div className="row" style={{ marginTop: 12 }}>
          <Button onClick={analyze} loading={loading} disabled={files.length === 0} icon="activity">
            Analyze {files.length > 0 ? `(${files.length})` : ""}
          </Button>
        </div>
        {err && <Output error={err} />}
        {result && (
          <>
            {result.trend && (
              <div className="output" style={{ background: "var(--brand-xlight)", borderColor: "var(--brand-light)" }}>
                {result.trend}
              </div>
            )}
            <h4 style={{ marginTop: 18 }}>Metrics</h4>
            <div className="output">{result.metrics}</div>
            <h4 style={{ marginTop: 18 }}>Analysis</h4>
            <div className="output">{result.analysis}</div>
            <h4 style={{ marginTop: 18 }}>Growth plan (reviewed)</h4>
            <div className="output">{result.plan}</div>
          </>
        )}
      </div>

      <div className="grid cols-2" style={{ marginTop: 20 }}>
        <div className="card">
          <h3>Progress trend</h3>
          <p className="muted">Fitness / fatigue / form from your logged history.</p>
          <Button onClick={loadTrend} loading={trendLoading} ghost icon="graph-up">
            Load trend
          </Button>
          <Output text={trend} />
        </div>

        <div className="card">
          <h3>Weekly schedule → calendar</h3>
          <p className="muted">Generate a structured week and export to .ics.</p>
          <label className="field">Goal</label>
          <input type="text" value={sgGoal} onChange={(e) => setSgGoal(e.target.value)} />
          <div className="row" style={{ marginTop: 12 }}>
            <Button onClick={makeSchedule} loading={sgLoading} icon="calendar-week">
              Build week
            </Button>
            {schedule && (
              <Button onClick={exportIcs} ghost icon="calendar-plus">
                Export .ics
              </Button>
            )}
          </div>
          {sgErr && <Output error={sgErr} />}
          {schedule && (
            <table className="deck">
              <thead>
                <tr>
                  <th>Day</th>
                  <th>Session</th>
                  <th>min</th>
                </tr>
              </thead>
              <tbody>
                {schedule.workouts.map((w, i) => (
                  <tr key={i}>
                    <td>{w.day}</td>
                    <td>
                      <strong>{w.title}</strong>
                      <div className="muted">{w.description}</div>
                    </td>
                    <td>{w.duration_min}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}

function fmt(x: unknown): string {
  return typeof x === "number" ? x.toFixed(1) : String(x ?? "-");
}
