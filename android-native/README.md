# PolarisStudyKit (Android) — on-device, **algorithms not AI**

A Kotlin study library where every feature is a **classical, deterministic algorithm** — no
LLM, no MediaPipe, no `.task` model file to download, no network. It's instant, fully offline,
runs on **any** device (no high-end/NPU requirement), and every feature is a plain JVM unit test.

> This replaces the earlier MediaPipe LLM Inference build. The LLM-powered experience still
> lives in the Python/desktop app and the web app; the mobile kit is intentionally AI-free so
> it's predictable, private, and zero-cost on every phone.

## The algorithms

| Feature | Algorithm | Type |
|---------|-----------|------|
| **Flashcards** | **SM-2** spaced repetition for scheduling; **cloze deletion** + **definition-pattern extraction** to generate cards | `SpacedRepetition`, `FlashcardGenerator` |
| **Quizzing** | MCQ generation with **nearest-length distractors**; **Levenshtein** fuzzy grading; **Leitner** boxes | `QuizEngine` |
| **Citations** | **Rule-table formatter** — APA / MLA / Chicago | `Citations` |
| **Essay** | **Flesch–Kincaid** readability + syllable heuristic + long-sentence / passive-voice signals | `Readability` |
| **CV Builder** | **Template rendering** → Markdown résumé | `PolarisStudy.buildCV` |
| **Advisor** | **Rule-based scheduler** (urgency × importance, front-loading) | `PolarisStudy.advise` |

## Use it

```kotlin
val polaris = PolarisStudy()

// Flashcards + SM-2 (dates are epoch-days for testability)
val cards = polaris.makeFlashcards(myNotes)
var state = Sm2State.new(LocalDate.now().toEpochDay())
state = polaris.review(state, grade = 4)          // schedules the next review

// Quiz + fuzzy grading
val quiz = polaris.makeQuiz(cards)
val ok = polaris.grade("mitochondrion", "mitochondria")   // true

// Citations
val (reference, inText) = polaris.citation(
    Source(authors = listOf("Smith, John Paul"), title = "On Photosynthesis",
           year = "2020", container = "Journal of Biology"),
    CitationStyle.APA)

// Essay readability
val report = polaris.analyzeWriting(myEssay)
```

Everything is synchronous and cheap — no background thread, `AutoCloseable`, or model lifecycle.
See `example/…/MainActivity.kt` for a Compose flashcard loop.

## Build / test

```bash
cd android-native
./gradlew :polaris-study-kit:test   # pure algorithm unit tests — no device or model needed
```
