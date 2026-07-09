# PolarisStudyKit (iOS) — on-device, **algorithms not AI**

A Swift study toolkit for iOS/iPadOS/macOS where every feature is a **classical, deterministic
algorithm** — no LLM, no model download, no network, no Apple-Intelligence requirement. It's
instant, fully offline, runs on **iOS 15+** (any device), and is unit-tested on CI.

> This replaces the earlier Foundation Models (on-device LLM) build. Mobile users get
> predictable, private, zero-cost features; the LLM-powered experience still lives in the
> Python/desktop app and the web app.

## The algorithms

| Feature | Algorithm | Type |
|---------|-----------|------|
| **Flashcards** | **SM-2** (SuperMemo 2) spaced repetition for scheduling; **cloze deletion** + **definition-pattern extraction** to generate cards from notes | `SpacedRepetition`, `FlashcardGenerator` |
| **Quizzing** | Multiple-choice generation with **nearest-length distractor selection**; **Levenshtein** edit-distance fuzzy grading; **Leitner** box system for adaptive review | `QuizEngine` |
| **Citations** | **Rule-table formatter** — APA / MLA / Chicago references + in-text citations, assembled deterministically from fields | `Citations` |
| **Essay** | **Flesch Reading Ease** + **Flesch–Kincaid grade level** (1975 formulas) with a vowel-group **syllable counter**; long-sentence & passive-voice heuristics | `Readability` |
| **CV Builder** | **Template rendering** of structured fields → Markdown résumé | `PolarisStudy.buildCV` |
| **Advisor** | **Rule-based scheduler**: priority = weight ÷ days-to-deadline; heavier work is front-loaded | `PolarisStudy.advise` |

## Use it

```swift
import PolarisStudyKit

let polaris = PolarisStudy()

// Flashcards + SM-2
let cards = polaris.makeFlashcards(from: myNotes)
var state = SM2State.new()
state = polaris.review(state, grade: 4)          // schedules the next review

// Quiz + fuzzy grading
let quiz = polaris.makeQuiz(from: cards)
let ok = polaris.grade("mitochondrion", answer: "mitochondria")   // true

// Citations
let (reference, inText) = polaris.citation(
    Source(authors: ["Smith, John Paul"], title: "On Photosynthesis", year: "2020",
           container: "Journal of Biology"),
    style: .apa)

// Essay readability
let report = polaris.analyzeWriting(myEssay)     // Flesch scores + structure
```

See `Example/ContentView.swift` for a SwiftUI flashcard-study loop.

## Build / test

```bash
cd ios-native
swift build
swift test        # pure algorithm tests — no device or model needed
```
