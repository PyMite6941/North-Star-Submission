// Typed client for the Polaris FastAPI backend. In dev, requests go through the Vite
// proxy at /api → the backend; override with VITE_API_BASE for a deployed backend.
const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

async function jpost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

async function jget<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

async function upload<T>(path: string, files: File[], fields: Record<string, string> = {}): Promise<T> {
  const fd = new FormData();
  for (const f of files) fd.append("files", f);
  for (const [k, v] of Object.entries(fields)) fd.append(k, v);
  const res = await fetch(`${BASE}${path}`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

// ---- Types ----
export interface Health {
  version: string;
  ollama_reachable: boolean;
  models: string[];
}
export interface AskResult {
  area: string | null;
  answer: string;
}
export interface Flashcard {
  question: string;
  answer: string;
}
export interface Deck {
  topic: string;
  cards: Flashcard[];
}
export interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
  explanation: string;
}
export interface Quiz {
  topic: string;
  questions: QuizQuestion[];
}
export interface RagAnswer {
  answer: string;
  sources: string[];
}
export interface AnalyzeResult {
  metrics: string;
  trend: string;
  analysis: string;
  plan: string;
}
export interface Workout {
  day: string;
  title: string;
  description: string;
  duration_min: number;
}
export interface Schedule {
  goal: string;
  workouts: Workout[];
}

export const api = {
  health: () => jget<Health>("/health"),
  studyAsk: (prompt: string, area?: string) => jpost<AskResult>("/study/ask", { prompt, area: area ?? null }),
  flashcards: (topic: string, count: number) => jpost<Deck>("/study/flashcards", { topic, count }),
  quiz: (topic: string, count: number, difficulty: string) =>
    jpost<Quiz>("/study/quiz", { topic, count, difficulty }),
  ragIngestUpload: (files: File[]) => upload<{ chunks_indexed: number; files: string[] }>("/rag/ingest-upload", files),
  ragAsk: (question: string) => jpost<RagAnswer>("/rag/ask", { question }),
  ragStats: () => jget<{ chunks: number }>("/rag/stats"),
  fitnessAnalyzeUpload: (files: File[], goal: string, log: boolean) =>
    upload<AnalyzeResult>("/fitness/analyze-upload", files, { goal, log: String(log) }),
  fitnessTrend: () => jget<Record<string, unknown>>("/fitness/trend"),
  fitnessSchedule: (goal: string) => jpost<Schedule>("/fitness/schedule", { goal, context: "" }),
};
