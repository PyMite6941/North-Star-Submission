import Foundation

/// PolarisStudy — the on-device study toolkit, powered entirely by **classical algorithms,
/// not AI**. Every feature is deterministic, offline, instant, and testable:
///
/// | Area        | Algorithm |
/// |-------------|-----------|
/// | Flashcards  | SM-2 spaced repetition + cloze/definition generation |
/// | Quizzing    | MCQ generation + Levenshtein grading + Leitner boxes |
/// | Citation    | Rule-table formatter (APA / MLA / Chicago) |
/// | Essay       | Flesch–Kincaid readability + structural heuristics |
/// | CV Builder  | Template rendering |
/// | Advisor     | Rule-based, deadline + spacing study scheduler |
///
/// No model download, no network, no `async`, no Apple-Intelligence requirement.
public struct PolarisStudy: Sendable {

    public init() {}

    // MARK: Flashcards (SM-2)
    public func makeFlashcards(from text: String, limit: Int = 20) -> [Flashcard] {
        FlashcardGenerator.generate(from: text, limit: limit)
    }

    public func review(_ state: SM2State, grade: Int) -> SM2State {
        SpacedRepetition.schedule(state, grade: grade)
    }

    // MARK: Quizzing
    public func makeQuiz(from cards: [Flashcard], choices: Int = 4) -> [QuizQuestion] {
        var rng = SystemRandomNumberGenerator()
        return QuizEngine.multipleChoice(from: cards, choices: choices, rng: &rng)
    }

    public func grade(_ given: String, answer: String) -> Bool {
        QuizEngine.isCorrect(given, answer: answer)
    }

    // MARK: Citation
    public func citation(_ source: Source, style: CitationStyle) -> (reference: String, inText: String) {
        (Citations.reference(source, style: style), Citations.inText(source, style: style))
    }

    // MARK: Essay
    public func analyzeWriting(_ text: String) -> ReadabilityReport {
        Readability.analyze(text)
    }

    // MARK: CV Builder (template)
    public struct Resume: Sendable {
        public var name = "", contact = "", summary = ""
        public var experience: [String] = [], education: [String] = [], skills: [String] = []
        public init() {}
    }

    /// Render a résumé as Markdown from structured fields — pure templating, no AI.
    public func buildCV(_ r: Resume) -> String {
        var out = ["# \(r.name)"]
        if !r.contact.isEmpty { out.append(r.contact) }
        if !r.summary.isEmpty { out += ["", "## Summary", r.summary] }
        func section(_ title: String, _ items: [String]) {
            guard !items.isEmpty else { return }
            out += ["", "## \(title)"] + items.map { "- \($0)" }
        }
        section("Experience", r.experience)
        section("Education", r.education)
        if !r.skills.isEmpty { out += ["", "## Skills", r.skills.joined(separator: " · ")] }
        return out.joined(separator: "\n")
    }

    // MARK: Advisor (rule-based scheduler)
    public struct Deadline: Sendable {
        public let title: String
        public let due: Date
        public let weightPct: Double
        public init(title: String, due: Date, weightPct: Double = 0) {
            self.title = title; self.due = due; self.weightPct = weightPct
        }
    }

    public struct PlanItem: Sendable {
        public let title: String
        public let start: Date
        public let priority: Double
    }

    /// Prioritize upcoming work by urgency × importance — no AI.
    /// priority = weight / max(1, days-until-due); suggested start backs off from the deadline
    /// by more days for heavier items (front-loading).
    public func advise(_ deadlines: [Deadline], now: Date = Date()) -> [PlanItem] {
        let cal = Calendar.current
        return deadlines.map { d in
            let days = max(1, cal.dateComponents([.day], from: now, to: d.due).day ?? 1)
            let priority = (d.weightPct > 0 ? d.weightPct : 10) / Double(days)
            let lead = min(days, Int((d.weightPct / 20).rounded()) + 1)   // heavier → start sooner
            let start = cal.date(byAdding: .day, value: -lead, to: d.due) ?? d.due
            return PlanItem(title: d.title, start: max(now, start), priority: priority)
        }
        .sorted { $0.priority > $1.priority }
    }
}
