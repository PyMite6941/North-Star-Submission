import Foundation

/// The six areas of Polaris — each fulfilled on-device by a classical algorithm (no AI).
///
/// The desktop/Python build uses an LLM for these; the mobile kit deliberately swaps in
/// deterministic algorithms so it runs instantly, offline, on any device. See `algorithm`.
public enum PolarisArea: String, CaseIterable, Sendable {
    case flashcards
    case quizzing
    case cvBuilder = "cv_builder"
    case advisor
    case citation
    case essay

    /// Human-readable title.
    public var title: String {
        switch self {
        case .flashcards: return "Flashcard Creation"
        case .quizzing: return "Quizzing"
        case .cvBuilder: return "CV Builder"
        case .advisor: return "Advisor"
        case .citation: return "Citation Generator"
        case .essay: return "Essay Helper"
        }
    }

    /// One-line description.
    public var summary: String {
        switch self {
        case .flashcards: return "Turn study material into clear question/answer flashcards."
        case .quizzing: return "Generate quizzes and grade answers with feedback."
        case .cvBuilder: return "Draft and refine a CV / résumé."
        case .advisor: return "General study and academic advice and planning."
        case .citation: return "Produce citations in APA / MLA / Chicago."
        case .essay: return "Outline, draft, and improve essays."
        }
    }

    /// The deterministic algorithm powering this area (no AI).
    public var algorithm: String {
        switch self {
        case .flashcards: return "SM-2 spaced repetition + cloze/definition generation"
        case .quizzing: return "MCQ generation + Levenshtein grading + Leitner boxes"
        case .cvBuilder: return "Template rendering"
        case .advisor: return "Rule-based deadline + spacing scheduler"
        case .citation: return "Rule-table formatter (APA / MLA / Chicago)"
        case .essay: return "Flesch–Kincaid readability + structural heuristics"
        }
    }

    /// Lookup by routing key (matches the Python `PolarisArea` string values).
    public init?(key: String) {
        self.init(rawValue: key.lowercased())
    }
}
