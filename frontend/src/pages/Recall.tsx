import { useEffect, useState } from "react";
import { api, humanError, type Card, type RecallDeck } from "../lib/api";
import { Button, Output } from "../components/ui";

const GRADES = [
  { g: 0, label: "Blackout", color: "#b22222" },
  { g: 2, label: "Hard", color: "#f97316" },
  { g: 3, label: "OK", color: "#2563eb" },
  { g: 5, label: "Easy", color: "#16a34a" },
];

export default function Recall() {
  const [decks, setDecks] = useState<RecallDeck[]>([]);
  const [name, setName] = useState("Biology unit 3");
  const [topic, setTopic] = useState("cellular respiration");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  // review session
  const [queue, setQueue] = useState<Card[]>([]);
  const [idx, setIdx] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [activeDeck, setActiveDeck] = useState<string | null>(null);

  const loadDecks = () => api.decks().then(setDecks).catch(() => setDecks([]));
  useEffect(() => {
    loadDecks();
  }, []);

  async function makeDeck(withAI: boolean) {
    setBusy(true);
    setErr("");
    try {
      await api.createDeck(name, withAI ? topic : undefined);
      await loadDecks();
    } catch (e) {
      setErr(humanError(e));
    } finally {
      setBusy(false);
    }
  }

  async function startReview(deckId: string) {
    setErr("");
    const q = await api.reviewQueue(deckId);
    setQueue(q);
    setIdx(0);
    setRevealed(false);
    setActiveDeck(deckId);
  }

  async function grade(g: number) {
    const card = queue[idx];
    if (!card) return;
    await api.gradeCard(card.id, g).catch(() => {});
    if (idx + 1 >= queue.length) {
      setActiveDeck(null);
      setQueue([]);
      loadDecks();
    } else {
      setIdx(idx + 1);
      setRevealed(false);
    }
  }

  const current = queue[idx];

  // Keyboard review: Space/Enter flips the card; 1–4 grade it once revealed.
  useEffect(() => {
    if (!activeDeck || !current) return;
    const onKey = (e: KeyboardEvent) => {
      if (!revealed && (e.key === " " || e.key === "Enter")) {
        e.preventDefault();
        setRevealed(true);
      } else if (revealed) {
        const map: Record<string, number> = { "1": 0, "2": 2, "3": 3, "4": 5 };
        if (e.key in map) grade(map[e.key]);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeDeck, current, revealed, idx, queue]);

  return (
    <>
      <h2 className="section-title">Active recall</h2>
      <p className="section-sub">Free, Quizlet-style spaced repetition (SM-2) — study what's due, when it's due.</p>

      {activeDeck && current ? (
        <div className="card" style={{ textAlign: "center" }}>
          <span className="badge">
            {idx + 1} / {queue.length} due
          </span>
          <div style={{ fontSize: "1.4rem", fontWeight: 600, margin: "26px 0", fontFamily: "var(--font-head)" }}>
            {current.question}
          </div>
          {revealed ? (
            <>
              <div className="output" style={{ textAlign: "left" }}>{current.answer}</div>
              <p className="muted" style={{ marginTop: 14 }}>How well did you recall it?</p>
              <div className="row" style={{ justifyContent: "center" }}>
                {GRADES.map((x, i) => (
                  <button key={x.g} className="btn" style={{ background: x.color, boxShadow: "none" }} onClick={() => grade(x.g)}>
                    {x.label} <kbd style={{ marginLeft: 6 }}>{i + 1}</kbd>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              <Button onClick={() => setRevealed(true)} icon="eye">
                Show answer
              </Button>
              <p className="muted" style={{ marginTop: 10, fontSize: ".8rem" }}>
                Press <kbd>Space</kbd> to flip · <kbd>1</kbd>–<kbd>4</kbd> to grade
              </p>
            </>
          )}
        </div>
      ) : (
        <>
          <div className="card">
            <h3>New deck</h3>
            <div className="row">
              <div style={{ flex: 1, minWidth: 200 }}>
                <label className="field">Deck name</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div style={{ flex: 1, minWidth: 200 }}>
                <label className="field">AI topic (optional)</label>
                <input type="text" value={topic} onChange={(e) => setTopic(e.target.value)} />
              </div>
            </div>
            <div className="row" style={{ marginTop: 12 }}>
              <Button onClick={() => makeDeck(true)} loading={busy} icon="magic">
                Generate with AI
              </Button>
              <Button onClick={() => makeDeck(false)} ghost icon="plus-lg">
                Empty deck
              </Button>
            </div>
            {err && <Output error={err} />}
          </div>

          <h3 className="section-title" style={{ fontSize: "1.2rem" }}>Your decks</h3>
          {decks.length === 0 && <p className="muted">No decks yet.</p>}
          <div className="grid cols-3">
            {decks.map((d) => (
              <div key={d.id} className="card">
                <h3>{d.name}</h3>
                <p className="muted">{d.cards ?? 0} cards · {d.due ?? 0} due</p>
                <Button onClick={() => startReview(d.id)} disabled={(d.due ?? 0) === 0} icon="lightning-charge">
                  {(d.due ?? 0) > 0 ? `Review ${d.due}` : "Nothing due"}
                </Button>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}
