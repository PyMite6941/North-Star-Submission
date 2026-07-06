import { useEffect, useState } from "react";
import { api, type Assignment, type WeekLoad, type WeeklyStudyPlan } from "../lib/api";
import { Button, Output } from "../components/ui";

export default function Planner() {
  // syllabus import
  const [files, setFiles] = useState<File[]>([]);
  const [importing, setImporting] = useState(false);
  const [importMsg, setImportMsg] = useState("");
  const [assignments, setAssignments] = useState<Assignment[]>([]);

  // workload + plan
  const [weeks, setWeeks] = useState<WeekLoad[]>([]);
  const [plan, setPlan] = useState<WeeklyStudyPlan | null>(null);
  const [planning, setPlanning] = useState(false);
  const [err, setErr] = useState("");

  // assistant
  const [q, setQ] = useState("What should I prioritize this week?");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  const refresh = () => {
    api.assignments().then(setAssignments).catch(() => {});
    api.workload().then(setWeeks).catch(() => {});
  };
  useEffect(() => {
    refresh();
  }, []);

  async function importSyllabus() {
    if (!files.length) return;
    setImporting(true);
    setImportMsg("");
    setErr("");
    try {
      const r = await api.syllabusImport(files);
      const course = (r.course as { name?: string })?.name ?? "course";
      const n = (r.assignments as unknown[])?.length ?? 0;
      setImportMsg(`Imported ${course} — ${n} assignments.`);
      setFiles([]);
      refresh();
    } catch (e) {
      setErr(String(e));
    } finally {
      setImporting(false);
    }
  }

  async function buildPlan() {
    setPlanning(true);
    setErr("");
    setPlan(null);
    try {
      setPlan(await api.weeklyPlan(2));
    } catch (e) {
      setErr(String(e));
    } finally {
      setPlanning(false);
    }
  }

  async function ask() {
    setAsking(true);
    setAnswer("");
    try {
      setAnswer((await api.assistant(q, ["assignment", "course"])).answer);
    } catch (e) {
      setAnswer(String(e));
    } finally {
      setAsking(false);
    }
  }

  const maxScore = Math.max(1, ...weeks.map((w) => w.score));

  return (
    <>
      <h2 className="section-title">Smart planner</h2>
      <p className="section-sub">Import a syllabus, see your workload, and get an AI weekly plan.</p>

      <div className="grid cols-2">
        <div className="card">
          <h3>Import syllabus</h3>
          <p className="muted">Upload a syllabus (PDF/DOCX/PPTX/MD/TXT) — Polaris extracts courses &amp; deadlines.</p>
          <input type="file" multiple accept=".pdf,.docx,.pptx,.md,.txt" onChange={(e) => setFiles(Array.from(e.target.files ?? []))} />
          <div className="row" style={{ marginTop: 12 }}>
            <Button onClick={importSyllabus} loading={importing} disabled={!files.length} icon="filetype-pdf">
              Import {files.length > 0 ? `(${files.length})` : ""}
            </Button>
          </div>
          {importMsg && <div className="output">{importMsg}</div>}
          {assignments.length > 0 && (
            <table className="deck">
              <thead>
                <tr>
                  <th>Assignment</th>
                  <th>Type</th>
                  <th>Due</th>
                </tr>
              </thead>
              <tbody>
                {assignments.slice(0, 12).map((a, i) => (
                  <tr key={i}>
                    <td>{a.title}</td>
                    <td className="muted">{a.type}</td>
                    <td className="muted">{a.due_date || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <h3>Workload</h3>
          <p className="muted">Detected intensity per week. Red = heavy — start early.</p>
          {weeks.length === 0 && <p className="muted">Import a syllabus to see your workload.</p>}
          <div style={{ marginTop: 10 }}>
            {weeks.map((w) => (
              <div key={w.week_start} style={{ marginBottom: 10 }}>
                <div className="row" style={{ justifyContent: "space-between", fontSize: ".85rem" }}>
                  <span>{w.week_start}</span>
                  <span className="muted">{w.count} items{w.heavy ? " · heavy" : ""}</span>
                </div>
                <div style={{ height: 10, background: "var(--bg-alt)", borderRadius: 999, overflow: "hidden" }}>
                  <div
                    style={{
                      width: `${(w.score / maxScore) * 100}%`,
                      height: "100%",
                      background: w.heavy ? "var(--brand)" : "linear-gradient(90deg, var(--blue), var(--purple))",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid cols-2" style={{ marginTop: 20 }}>
        <div className="card">
          <h3>AI weekly plan</h3>
          <Button onClick={buildPlan} loading={planning} icon="calendar-week">
            Build my week
          </Button>
          {err && <Output error={err} />}
          {plan && (
            <>
              <p style={{ marginTop: 12 }}>
                <strong>Focus:</strong> {plan.focus}
              </p>
              <table className="deck">
                <thead>
                  <tr>
                    <th>Day</th>
                    <th>Task</th>
                    <th>min</th>
                  </tr>
                </thead>
                <tbody>
                  {plan.blocks.map((b, i) => (
                    <tr key={i}>
                      <td>{b.day}</td>
                      <td>{b.task}</td>
                      <td>{b.minutes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>

        <div className="card">
          <h3>Ask Polaris</h3>
          <p className="muted">The free-API interpreter reasons over your syllabus data.</p>
          <textarea value={q} onChange={(e) => setQ(e.target.value)} />
          <div className="row" style={{ marginTop: 12 }}>
            <Button onClick={ask} loading={asking} icon="stars">
              Ask
            </Button>
          </div>
          <Output text={answer} />
        </div>
      </div>
    </>
  );
}
