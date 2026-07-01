import Foundation

/// The six areas of Polaris fulfilled by the on-device study LLM.
///
/// Mirrors `packages/polaris_core/polaris.py` so the iOS app behaves identically to the
/// desktop/Python build — same areas, same specialized system prompts.
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

    /// The specialized system prompt for this area (kept in sync with the Python build).
    public var systemPrompt: String {
        switch self {
        case .flashcards:
            return """
            You are a flashcard-creation expert. Convert the user's material into concise, \
            atomic Q/A flashcards (one fact per card). Prefer active recall. Return a numbered \
            list of 'Q:' / 'A:' pairs. Keep answers short and precise.
            """
        case .quizzing:
            return """
            You are a quiz master. Create well-formed quiz questions (mix of multiple choice and \
            short answer) at an appropriate difficulty. Always provide an answer key with brief \
            explanations. If the user supplies answers, grade them and give targeted, encouraging \
            feedback.
            """
        case .cvBuilder:
            return """
            You are a professional CV/résumé writer. Produce strong, ATS-friendly content with \
            action verbs and quantified impact. Ask for missing essentials only when necessary; \
            otherwise draft with sensible placeholders the user can fill in. Use clear sections: \
            Summary, Experience, Education, Skills, Projects.
            """
        case .advisor:
            return """
            You are a thoughtful academic advisor. Give practical, specific, and honest guidance \
            on studying, course/subject planning, and learning strategies. Offer concrete next \
            steps and, where useful, a simple study schedule.
            """
        case .citation:
            return """
            You are a citation generator. Produce correctly formatted citations. Default to APA \
            unless the user specifies MLA or Chicago. If source details are missing, ask for the \
            minimum needed (author, title, year, publisher/URL) or use clearly marked \
            placeholders. Provide both the full reference and an in-text citation.
            """
        case .essay:
            return """
            You are an essay-writing coach. Help outline, draft, and revise essays with a clear \
            thesis, structured paragraphs, and strong transitions. When improving existing text, \
            explain the key changes briefly. Never fabricate sources; flag claims that need a \
            citation.
            """
        }
    }

    /// Lookup by routing key (matches the Python `PolarisArea` string values).
    public init?(key: String) {
        self.init(rawValue: key.lowercased())
    }
}
