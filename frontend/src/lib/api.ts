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

// ---- Student-life feature types ----
export interface Course {
  name: string;
  code?: string | null;
  instructor?: string | null;
}
export interface Assignment {
  title: string;
  type: string;
  due_date?: string | null;
  weight_pct?: number | null;
  course?: string;
}
export interface WeekLoad {
  week_start: string;
  score: number;
  heavy: boolean;
  count: number;
}
export interface StudyBlock {
  day: string;
  task: string;
  minutes: number;
}
export interface WeeklyStudyPlan {
  focus: string;
  blocks: StudyBlock[];
}
export interface FocusStats {
  sessions: number;
  total_minutes: number;
  today_minutes: number;
  streak_days: number;
}
export interface Club {
  id: string;
  name: string;
  category?: string;
  description?: string;
  members?: number;
}
export interface RecallDeck {
  id: string;
  name: string;
  description?: string;
  cards?: number;
  due?: number;
}
export interface Card {
  id: string;
  question: string;
  answer: string;
  due?: string;
}

// ---- Writing assistant ----
export interface WritingIssue {
  start: number;
  end: number;
  type: string;
  message: string;
  suggestion?: string | null;
  matched: string;
}
export interface WritingReport {
  issues: WritingIssue[];
  words: number;
  sentences: number;
  flesch_reading_ease: number;
  flesch_kincaid_grade: number;
  score: number;
  counts: Record<string, number>;
}
export interface CoachNote {
  kind: string; // 'fix' | 'add'
  anchor: string;
  issue: string;
  why: string;
  suggestion: string;
}
export interface CoachReport {
  summary: string;
  notes: CoachNote[];
}

export const api = {
  health: () => jget<Health>("/health"),

  // --- writing (rule check = offline-capable; Polly coach/polish = online only) ---
  writingCheck: (text: string) => jpost<WritingReport>("/writing/check", { text }),
  pollyCoach: (text: string) => jpost<CoachReport>("/writing/coach", { text }),
  pollyPolish: (text: string, tone = "neutral") =>
    jpost<{ rewrite: string }>("/writing/polish", { text, tone }),


  // --- syllabus ---
  syllabusImport: (files: File[]) => upload<Record<string, unknown>>("/syllabus/import-upload", files),
  syllabusImportText: (text: string) => jpost<Record<string, unknown>>("/syllabus/import-text", { text }),
  courses: () => jget<Course[]>("/syllabus/courses"),
  assignments: () => jget<Assignment[]>("/syllabus/assignments"),

  // --- planner ---
  workload: () => jget<WeekLoad[]>("/planner/workload"),
  weeklyPlan: (hours: number) => jpost<WeeklyStudyPlan>("/planner/week", { study_hours_per_day: hours }),

  // --- pomodoro ---
  logPomodoro: (minutes: number, task: string) => jpost<FocusStats>("/pomodoro/session", { minutes, task }),
  focusStats: () => jget<FocusStats>("/pomodoro/stats"),

  // --- clubs ---
  clubs: (q?: string) => jget<Club[]>(`/clubs${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  joinClub: (id: string) => jpost<Club>(`/clubs/${encodeURIComponent(id)}/join`, {}),

  // --- recall ---
  decks: () => jget<RecallDeck[]>("/recall/decks"),
  createDeck: (name: string, topic?: string, count = 10) =>
    jpost<RecallDeck>("/recall/decks", topic ? { name, topic, count } : { name }),
  reviewQueue: (deckId?: string) => jget<Card[]>(`/recall/review${deckId ? `?deck_id=${deckId}` : ""}`),
  gradeCard: (cardId: string, grade: number) => jpost<Card>(`/recall/review/${cardId}`, { grade }),

  // --- assistant (free-API interpreter over the vector store) ---
  assistant: (question: string, kinds?: string[]) =>
    jpost<{ answer: string; used: { kind: string; id: string }[] }>("/assistant/ask", { question, kinds }),

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
