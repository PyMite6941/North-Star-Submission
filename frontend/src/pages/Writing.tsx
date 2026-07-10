import { useState } from "react";
import { api, type CoachReport, type WritingReport } from "../lib/api";
import { Button, Output, submitOnCmdEnter, useOnline } from "../components/ui";

const SAMPLE =
  "In order to succeed in school, you must be very very careful with your time. " +
  "The the results was clearly good due to the fact that we tried hard.";

export default function Writing() {
  const online = useOnline();
  const [text, setText] = useState(SAMPLE);

  const [report, setReport] = useState<WritingReport | null>(null);
  const [checking, setChecking] = useState(false);

  const [coach, setCoach] = useState<CoachReport | null>(null);
  const [rewrite, setRewrite] = useState("");
  const [pollyBusy, setPollyBusy] = useState(false);
  const [err, setErr] = useState<unknown>(null);

  async function check() {
    setChecking(true);
    setErr(null);
    try {
      setReport(await api.writingCheck(text));
    } catch (e) {
      setErr(e);
    } finally {
      setChecking(false);
    }
  }

  async function askPolly(mode: "coach" | "polish") {
    if (!online) return; // Polly is online-only
    setPollyBusy(true);
    setErr(null);
    setCoach(null);
    setRewrite("");
    try {
      if (mode === "coach") setCoach(await api.pollyCoach(text));
      else setRewrite((await api.pollyPolish(text)).rewrite);
    } catch (e) {
      setErr(e);
    } finally {
      setPollyBusy(false);
    }
  }

  return (
    <>
      <h2 className="section-title">Writing</h2>
      <p className="section-sub">
        A grammar &amp; style checker that runs offline, plus <strong>Polly</strong> — the AI coach
        that shows where to fix <em>and add</em> things, and why.
      </p>

      <div className="grid cols-2">
        <div className="card">
          <label className="field">Your text</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={submitOnCmdEnter(check)}
            style={{ minHeight: 200 }}
          />
          <div className="row" style={{ marginTop: 12, justifyContent: "space-between" }}>
            <div className="row" style={{ gap: 12 }}>
            <Button onClick={check} loading={checking} icon="check2-circle">
              Check (offline)
            </Button>
            <Button onClick={() => askPolly("coach")} loading={pollyBusy} disabled={!online} icon="stars">
              Ask Polly
            </Button>
            <Button onClick={() => askPolly("polish")} disabled={!online || pollyBusy} ghost icon="magic">
              Rewrite with Polly
            </Button>
            </div>
            <span className="muted" style={{ fontSize: ".8rem" }}>
              <kbd>⌘</kbd>/<kbd>Ctrl</kbd>+<kbd>↵</kbd> to check
            </span>
          </div>
          {!online && (
            <p className="muted" style={{ marginTop: 8 }}>
              <i className="bi bi-wifi-off" /> Offline — Polly is an online-only feature. The rule
              check still works.
            </p>
          )}
          {err != null && <Output error={err} />}
        </div>

        <div className="card">
          <h3>Score &amp; readability</h3>
          {report ? (
            <>
              <div className="row" style={{ gap: 24, marginTop: 8 }}>
                <div>
                  <div style={{ fontFamily: "var(--font-head)", fontSize: "2.2rem", fontWeight: 800, color: scoreColor(report.score) }}>
                    {report.score}
                  </div>
                  <div className="muted" style={{ fontSize: ".85rem" }}>/ 100</div>
                </div>
                <div className="muted" style={{ fontSize: ".9rem" }}>
                  {report.words} words · {report.sentences} sentences
                  <br />
                  Reading ease {report.flesch_reading_ease} · grade {report.flesch_kincaid_grade}
                </div>
              </div>
              <div className="chips" style={{ marginTop: 10 }}>
                {Object.entries(report.counts).map(([k, v]) => (
                  <span key={k} className="chip" style={{ cursor: "default" }}>
                    {v} {k}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <p className="muted">Run a check to see your score.</p>
          )}
        </div>
      </div>

      {report && report.issues.length > 0 && (
        <>
          <h3 className="section-title" style={{ fontSize: "1.2rem" }}>Issues to fix</h3>
          <div className="card">
            {report.issues.map((i, n) => (
              <div key={n} className="row" style={{ justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                <div>
                  <span className="badge" style={{ marginRight: 8 }}>{i.type}</span>
                  <strong>“{i.matched}”</strong> — {i.message}
                </div>
                {i.suggestion && <span className="muted">→ {i.suggestion}</span>}
              </div>
            ))}
          </div>
        </>
      )}

      {coach && (
        <>
          <h3 className="section-title" style={{ fontSize: "1.2rem" }}>
            <i className="bi bi-stars" /> Polly says
          </h3>
          <div className="card">
            <p>{coach.summary}</p>
            {coach.notes.map((note, n) => (
              <div key={n} className="output" style={{ marginTop: 10 }}>
                <span className="badge" style={{ background: note.kind === "add" ? "#e7f6ee" : "var(--brand-xlight)", color: note.kind === "add" ? "var(--green)" : "var(--brand)" }}>
                  {note.kind === "add" ? "ADD" : "FIX"}
                </span>{" "}
                <strong>{note.anchor === "overall" ? "Overall" : `“${note.anchor}”`}</strong> — {note.issue}
                <div className="muted" style={{ marginTop: 4 }}>Why: {note.why}</div>
                {note.suggestion && <div style={{ marginTop: 4, color: "var(--brand-dark)" }}>{note.suggestion}</div>}
              </div>
            ))}
          </div>
        </>
      )}

      {rewrite && (
        <>
          <h3 className="section-title" style={{ fontSize: "1.2rem" }}>Polly's rewrite</h3>
          <div className="card"><Output text={rewrite} /></div>
        </>
      )}
    </>
  );
}

function scoreColor(s: number): string {
  return s >= 80 ? "var(--green)" : s >= 60 ? "var(--orange)" : "var(--brand)";
}
