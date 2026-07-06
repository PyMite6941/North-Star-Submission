import { Link } from "react-router-dom";

const features = [
  { icon: "stack", title: "6 study areas", body: "Flashcards, quizzing, CV builder, advisor, citations, essay help — one local model, routed automatically.", to: "/study" },
  { icon: "lightning-charge", title: "Active recall", body: "Free, Quizlet-style spaced repetition (SM-2). AI-generate decks and review exactly what's due.", to: "/recall" },
  { icon: "calendar-week", title: "Smart planner", body: "Import a syllabus, auto-detect heavy weeks, and get an AI weekly study plan grounded in your deadlines.", to: "/planner" },
  { icon: "clock-history", title: "Focus timer", body: "Pomodoro sessions that log to a persistent streak so your focus habit sticks.", to: "/pomodoro" },
  { icon: "people", title: "Club hub", body: "Discover and join clubs with semantic search across interests.", to: "/clubs" },
  { icon: "search", title: "Cited notes (RAG)", body: "Upload notes (PDF/DOCX/PPTX/MD) and get accurate, source-cited answers — fully offline.", to: "/notes" },
];

export default function Home() {
  return (
    <>
      <section className="hero">
        <h1>
          Your academic journey, <span className="brand-gradient">organized</span>.
        </h1>
        <p>
          Polaris Student is an offline-first study &amp; fitness assistant. Flashcards, quizzes, CVs,
          citations, essays, cited notes, and personalized training plans — all powered by a local model
          on your own device. No accounts, no cloud required.
        </p>
        <div className="row">
          <Link to="/study" className="btn">
            <i className="bi bi-mortarboard" /> Start studying
          </Link>
          <Link to="/fitness" className="btn ghost" style={{ color: "#fff", borderColor: "rgba(255,255,255,.3)", background: "transparent" }}>
            <i className="bi bi-heart-pulse" /> Track fitness
          </Link>
        </div>
        <div className="metrics">
          <div className="m"><b>6</b><span>study areas</span></div>
          <div className="m"><b>100%</b><span>on-device</span></div>
          <div className="m"><b>0</b><span>API keys needed</span></div>
          <div className="m"><b>24/7</b><span>works offline</span></div>
        </div>
      </section>

      <div className="grid cols-3">
        {features.map((f) => (
          <Link key={f.title} to={f.to} className="card" style={{ color: "inherit" }}>
            <div className="icon"><i className={`bi bi-${f.icon}`} /></div>
            <h3>{f.title}</h3>
            <p className="muted">{f.body}</p>
          </Link>
        ))}
      </div>

      <h2 className="section-title">Everything a student needs, on one page</h2>
      <p className="section-sub">
        Each tool below runs against your local Polaris backend. Pick a tab in the nav to begin.
      </p>
      <div className="grid cols-3">
        <div className="card"><h3>Study</h3><p className="muted">Ask anything and Polaris routes it to the right area — or force one. Generate flashcard decks and take graded quizzes.</p></div>
        <div className="card"><h3>Notes</h3><p className="muted">Upload documents to build a private vector library, then ask questions and get cited, grounded answers.</p></div>
        <div className="card"><h3>Fitness</h3><p className="muted">Upload runs/rides to see metrics and trends, then get a reviewed growth plan you can export to your calendar.</p></div>
      </div>
    </>
  );
}
