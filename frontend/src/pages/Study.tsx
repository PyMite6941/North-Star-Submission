import { useState } from "react";
import { api, humanError, type Deck, type Quiz } from "../lib/api";
import { Button, Output, submitOnCmdEnter } from "../components/ui";

const AREAS = [
  { key: "", label: "Auto" },
  { key: "flashcards", label: "Flashcards" },
  { key: "quizzing", label: "Quizzing" },
  { key: "cv_builder", label: "CV Builder" },
  { key: "advisor", label: "Advisor" },
  { key: "citation", label: "Citation" },
  { key: "essay", label: "Essay" },
];

export default function Study() {
  // --- Ask ---
  const [prompt, setPrompt] = useState("Explain the causes of World War I");
  const [area, setArea] = useState("");
  const [answer, setAnswer] = useState("");
  const [chosen, setChosen] = useState<string | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askErr, setAskErr] = useState("");

  async function ask() {
    setAskLoading(true);
    setAskErr("");
    setAnswer("");
    try {
      const r = await api.studyAsk(prompt, area || undefined);
      setAnswer(r.answer);
      setChosen(r.area);
    } catch (e) {
      setAskErr(humanError(e));
    } finally {
      setAskLoading(false);
    }
  }

  // --- Flashcards ---
  const [fcTopic, setFcTopic] = useState("The Krebs cycle");
  const [fcN, setFcN] = useState(6);
  const [deck, setDeck] = useState<Deck | null>(null);
  const [fcLoading, setFcLoading] = useState(false);
  const [fcErr, setFcErr] = useState("");

  async function makeDeck() {
    setFcLoading(true);
    setFcErr("");
    setDeck(null);
    try {
      setDeck(await api.flashcards(fcTopic, fcN));
    } catch (e) {
      setFcErr(humanError(e));
    } finally {
      setFcLoading(false);
    }
  }

  function exportCsv() {
    if (!deck) return;
    const csv = deck.cards.map((c) => `"${c.question.replace(/"/g, '""')}","${c.answer.replace(/"/g, '""')}"`).join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `${deck.topic.replace(/\s+/g, "_")}_deck.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // --- Quiz ---
  const [qzTopic, setQzTopic] = useState("Photosynthesis");
  const [qzN, setQzN] = useState(4);
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [reveal, setReveal] = useState(false);
  const [qzLoading, setQzLoading] = useState(false);
  const [qzErr, setQzErr] = useState("");

  async function makeQuiz() {
    setQzLoading(true);
    setQzErr("");
    setQuiz(null);
    setReveal(false);
    try {
      setQuiz(await api.quiz(qzTopic, qzN, "medium"));
    } catch (e) {
      setQzErr(humanError(e));
    } finally {
      setQzLoading(false);
    }
  }

  return (
    <>
      <h2 className="section-title">Study</h2>
      <p className="section-sub">One local model fulfilling the 6 areas of Polaris.</p>

      <div className="grid cols-2">
        {/* Ask */}
        <div className="card">
          <h3>Ask anything</h3>
          <p className="muted">Polaris routes your request to the best area — or pin one.</p>
          <div className="chips">
            {AREAS.map((a) => (
              <span key={a.key} className={`chip${area === a.key ? " active" : ""}`} onClick={() => setArea(a.key)}>
                {a.label}
              </span>
            ))}
          </div>
          <label className="field">Your request</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={submitOnCmdEnter(ask)}
          />
          <div className="row" style={{ marginTop: 12, justifyContent: "space-between" }}>
            <div className="row" style={{ gap: 12 }}>
              <Button onClick={ask} loading={askLoading} icon="send">
                Ask Polaris
              </Button>
              {chosen && !askLoading && <span className="badge">area: {chosen}</span>}
            </div>
            <span className="muted" style={{ fontSize: ".8rem" }}>
              <kbd>⌘</kbd>/<kbd>Ctrl</kbd>+<kbd>↵</kbd>
            </span>
          </div>
          <Output text={answer} error={askErr} />
        </div>

        {/* Flashcards */}
        <div className="card">
          <h3>Flashcards</h3>
          <p className="muted">Generate an atomic deck and export it (Anki-ready CSV).</p>
          <label className="field">Topic</label>
          <input type="text" value={fcTopic} onChange={(e) => setFcTopic(e.target.value)} />
          <label className="field">Cards: {fcN}</label>
          <input type="range" min={3} max={20} value={fcN} onChange={(e) => setFcN(Number(e.target.value))} />
          <div className="row" style={{ marginTop: 12 }}>
            <Button onClick={makeDeck} loading={fcLoading} icon="card-text">
              Generate deck
            </Button>
            {deck && (
              <Button onClick={exportCsv} ghost icon="download">
                Export CSV
              </Button>
            )}
          </div>
          {fcErr && <Output error={fcErr} />}
          {deck && (
            <table className="deck">
              <thead>
                <tr>
                  <th style={{ width: 30 }}>#</th>
                  <th>Q</th>
                  <th>A</th>
                </tr>
              </thead>
              <tbody>
                {deck.cards.map((c, i) => (
                  <tr key={i}>
                    <td className="muted">{i + 1}</td>
                    <td>{c.question}</td>
                    <td>{c.answer}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Quiz */}
      <h2 className="section-title">Quiz yourself</h2>
      <p className="section-sub">Generate a quiz, then reveal the answer key.</p>
      <div className="card">
        <div className="row">
          <div style={{ flex: 1, minWidth: 220 }}>
            <label className="field">Topic</label>
            <input type="text" value={qzTopic} onChange={(e) => setQzTopic(e.target.value)} />
          </div>
          <div style={{ width: 120 }}>
            <label className="field">Questions</label>
            <input type="number" min={2} max={10} value={qzN} onChange={(e) => setQzN(Number(e.target.value))} />
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <Button onClick={makeQuiz} loading={qzLoading} icon="patch-question">
            Generate quiz
          </Button>
          {quiz && (
            <Button onClick={() => setReveal((r) => !r)} ghost icon={reveal ? "eye-slash" : "eye"}>
              {reveal ? "Hide answers" : "Reveal answers"}
            </Button>
          )}
        </div>
        {qzErr && <Output error={qzErr} />}
        {quiz &&
          quiz.questions.map((q, i) => (
            <div key={i} className="output" style={{ marginTop: 14 }}>
              <strong>
                {i + 1}. {q.question}
              </strong>
              {q.options.length > 0 && (
                <ul style={{ margin: "8px 0" }}>
                  {q.options.map((o, j) => (
                    <li key={j}>{o}</li>
                  ))}
                </ul>
              )}
              {reveal && (
                <div style={{ marginTop: 8, color: "var(--green)" }}>
                  <strong>Answer:</strong> {q.answer}
                  <div className="muted" style={{ color: "var(--text-muted)" }}>
                    {q.explanation}
                  </div>
                </div>
              )}
            </div>
          ))}
      </div>
    </>
  );
}
