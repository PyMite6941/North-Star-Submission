import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Button, Output } from "../components/ui";

export default function Notes() {
  const [files, setFiles] = useState<File[]>([]);
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState("");
  const [ingestErr, setIngestErr] = useState("");
  const [chunks, setChunks] = useState<number | null>(null);

  const [q, setQ] = useState("What are the main points of my notes?");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [asking, setAsking] = useState(false);
  const [askErr, setAskErr] = useState("");

  async function refreshStats() {
    try {
      setChunks((await api.ragStats()).chunks);
    } catch {
      setChunks(null);
    }
  }
  useEffect(() => {
    refreshStats();
  }, []);

  async function ingest() {
    if (files.length === 0) return;
    setIngesting(true);
    setIngestErr("");
    setIngestMsg("");
    try {
      const r = await api.ragIngestUpload(files);
      setIngestMsg(`Indexed ${r.chunks_indexed} new/updated chunks from ${r.files.join(", ")}.`);
      setFiles([]);
      refreshStats();
    } catch (e) {
      setIngestErr(String(e));
    } finally {
      setIngesting(false);
    }
  }

  async function ask() {
    setAsking(true);
    setAskErr("");
    setAnswer("");
    setSources([]);
    try {
      const r = await api.ragAsk(q);
      setAnswer(r.answer);
      setSources(r.sources);
    } catch (e) {
      setAskErr(String(e));
    } finally {
      setAsking(false);
    }
  }

  return (
    <>
      <h2 className="section-title">Notes (RAG)</h2>
      <p className="section-sub">
        Build a private, on-device knowledge base from your documents, then get cited answers.
        {chunks !== null && <span className="badge" style={{ marginLeft: 10 }}>{chunks} chunks stored</span>}
      </p>

      <div className="grid cols-2">
        <div className="card">
          <h3>Add notes</h3>
          <p className="muted">Supports .md .txt .pdf .docx .pptx — re-uploading unchanged files is skipped.</p>
          <label className="field">Choose files</label>
          <input
            type="file"
            multiple
            accept=".md,.markdown,.txt,.rst,.pdf,.docx,.pptx"
            onChange={(e) => setFiles(Array.from(e.target.files ?? []))}
          />
          <div className="row" style={{ marginTop: 12 }}>
            <Button onClick={ingest} loading={ingesting} disabled={files.length === 0} icon="cloud-upload">
              Ingest {files.length > 0 ? `(${files.length})` : ""}
            </Button>
          </div>
          {ingestMsg && <div className="output">{ingestMsg}</div>}
          {ingestErr && <Output error={ingestErr} />}
        </div>

        <div className="card">
          <h3>Ask your notes</h3>
          <p className="muted">Answers are grounded in your documents and cite their sources.</p>
          <label className="field">Question</label>
          <textarea value={q} onChange={(e) => setQ(e.target.value)} />
          <div className="row" style={{ marginTop: 12 }}>
            <Button onClick={ask} loading={asking} icon="search">
              Ask
            </Button>
          </div>
          <Output text={answer} error={askErr} />
          {sources.length > 0 && (
            <div style={{ marginTop: 10 }}>
              <span className="muted" style={{ fontWeight: 600 }}>
                Sources:
              </span>
              <div className="chips">
                {sources.map((s) => (
                  <span key={s} className="chip" style={{ cursor: "default" }}>
                    <i className="bi bi-file-earmark-text" /> {s.split(/[\\/]/).pop()}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
