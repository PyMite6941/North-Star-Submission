import { useEffect, useState } from "react";
import { api, type Club } from "../lib/api";
import { Button } from "../components/ui";

export default function Clubs() {
  const [clubs, setClubs] = useState<Club[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [joined, setJoined] = useState<Set<string>>(new Set());

  const load = (query?: string) => {
    setLoading(true);
    api
      .clubs(query)
      .then(setClubs)
      .catch(() => setClubs([]))
      .finally(() => setLoading(false));
  };
  useEffect(() => {
    load();
  }, []);

  async function join(id: string) {
    const updated = await api.joinClub(id).catch(() => null);
    if (updated) {
      setClubs((cs) => cs.map((c) => (c.id === id ? { ...c, members: updated.members } : c)));
      setJoined((j) => new Set(j).add(id));
    }
  }

  return (
    <>
      <h2 className="section-title">Club hub</h2>
      <p className="section-sub">Discover and join clubs. Search is semantic — try “coding”, “service”, or “art”.</p>

      <div className="card">
        <div className="row">
          <input
            type="text"
            placeholder="Search clubs by interest…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && load(q)}
          />
          <Button onClick={() => load(q)} loading={loading} icon="search">
            Search
          </Button>
          {q && (
            <Button onClick={() => { setQ(""); load(); }} ghost icon="x-lg">
              Clear
            </Button>
          )}
        </div>
      </div>

      <div className="grid cols-3" style={{ marginTop: 20 }}>
        {clubs.map((c) => (
          <div key={c.id} className="card">
            <div className="row" style={{ justifyContent: "space-between" }}>
              <span className="badge">{c.category || "Club"}</span>
              <span className="muted" style={{ fontSize: ".85rem" }}>
                <i className="bi bi-people" /> {c.members ?? 0}
              </span>
            </div>
            <h3 style={{ marginTop: 10 }}>{c.name}</h3>
            <p className="muted">{c.description}</p>
            {joined.has(c.id) ? (
              <Button onClick={() => {}} disabled ghost icon="check-lg">
                Joined
              </Button>
            ) : (
              <Button onClick={() => join(c.id)} ghost icon="plus-circle">
                Join
              </Button>
            )}
          </div>
        ))}
      </div>
      {loading && clubs.length === 0 && <p className="muted">Loading clubs…</p>}
      {clubs.length === 0 && !loading && <p className="muted">No clubs found.</p>}
    </>
  );
}
