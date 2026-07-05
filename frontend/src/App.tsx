import { NavLink, Route, Routes } from "react-router-dom";
import { BackendStatus } from "./components/ui";
import Home from "./pages/Home";
import Study from "./pages/Study";
import Notes from "./pages/Notes";
import Fitness from "./pages/Fitness";

export default function App() {
  return (
    <>
      <nav className="nav">
        <div className="container">
          <NavLink to="/" className="logo">
            Polaris <span className="brand-gradient">Student</span> ⭐
          </NavLink>
          <div className="links">
            <NavLink to="/" end>
              Home
            </NavLink>
            <NavLink to="/study">Study</NavLink>
            <NavLink to="/notes">Notes</NavLink>
            <NavLink to="/fitness">Fitness</NavLink>
          </div>
          <BackendStatus />
        </div>
      </nav>

      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/study" element={<Study />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/fitness" element={<Fitness />} />
        </Routes>
      </main>

      <footer className="footer">
        <div className="container">
          Polaris Student — offline-first study &amp; fitness AI (LangGraph + Ollama). Runs on your device.
        </div>
      </footer>
    </>
  );
}
