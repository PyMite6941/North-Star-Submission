import { Suspense, lazy } from "react";
import { NavLink, Route, Routes, useLocation } from "react-router-dom";
import { BackendStatus, OfflineBanner } from "./components/ui";
import Home from "./pages/Home";

// Route-level code-splitting: each feature page is its own chunk, so the initial
// load stays small and pages fetch on demand.
const Study = lazy(() => import("./pages/Study"));
const Notes = lazy(() => import("./pages/Notes"));
const Fitness = lazy(() => import("./pages/Fitness"));
const Planner = lazy(() => import("./pages/Planner"));
const Pomodoro = lazy(() => import("./pages/Pomodoro"));
const Clubs = lazy(() => import("./pages/Clubs"));
const Recall = lazy(() => import("./pages/Recall"));
const Writing = lazy(() => import("./pages/Writing"));

const LINKS = [
  { to: "/study", label: "Study" },
  { to: "/recall", label: "Recall" },
  { to: "/writing", label: "Writing" },
  { to: "/notes", label: "Notes" },
  { to: "/planner", label: "Planner" },
  { to: "/pomodoro", label: "Focus" },
  { to: "/clubs", label: "Clubs" },
  { to: "/fitness", label: "Fitness" },
];

export default function App() {
  const location = useLocation();
  return (
    <>
      <OfflineBanner />
      <nav className="nav">
        <div className="container">
          <NavLink to="/" className="logo">
            Polaris <span className="brand-gradient">Student</span> ⭐
          </NavLink>
          <div className="links">
            {LINKS.map((l) => (
              <NavLink key={l.to} to={l.to}>
                {l.label}
              </NavLink>
            ))}
          </div>
          <BackendStatus />
        </div>
      </nav>

      <main className="container">
        <Suspense fallback={<p className="muted" style={{ padding: 40 }}>Loading…</p>}>
          {/* keyed on pathname so each navigation re-triggers the fade-in */}
          <div key={location.pathname} className="page-fade">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/study" element={<Study />} />
            <Route path="/recall" element={<Recall />} />
            <Route path="/writing" element={<Writing />} />
            <Route path="/notes" element={<Notes />} />
            <Route path="/planner" element={<Planner />} />
            <Route path="/pomodoro" element={<Pomodoro />} />
            <Route path="/clubs" element={<Clubs />} />
            <Route path="/fitness" element={<Fitness />} />
          </Routes>
          </div>
        </Suspense>
      </main>

      <footer className="footer">
        <div className="container">
          Polaris Student — offline-first study &amp; fitness AI (LangGraph + Ollama). Runs on your device.
        </div>
      </footer>
    </>
  );
}
