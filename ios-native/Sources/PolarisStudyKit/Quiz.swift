import Foundation

/// Algorithmic quizzing — no AI.
///
/// - **Generation**: turns Q/A cards into multiple-choice questions, drawing distractors from
///   other cards' answers (nearest-length heuristic so options look plausible).
/// - **Grading**: fuzzy free-text matching via normalized **Levenshtein** edit distance.
/// - **Adaptive review**: a **Leitner** box system promotes/demotes items by correctness.
public struct QuizQuestion: Sendable {
    public let prompt: String
    public let options: [String]   // shuffled; one is `answer`
    public let answer: String
}

public enum QuizEngine {

    /// Build multiple-choice questions from cards. `choices` includes the correct answer.
    public static func multipleChoice(from cards: [Flashcard], choices: Int = 4,
                                      rng: inout SystemRandomNumberGenerator) -> [QuizQuestion] {
        let answers = cards.map(\.answer)
        return cards.map { card in
            let distractors = answers
                .filter { $0 != card.answer }
                .sorted { abs($0.count - card.answer.count) < abs($1.count - card.answer.count) }
                .prefix(max(0, choices - 1))
            var options = Array(distractors) + [card.answer]
            options.shuffle(using: &rng)
            return QuizQuestion(prompt: card.question, options: options, answer: card.answer)
        }
    }

    /// Is a free-text answer correct? Accepts near-matches
    /// (default 80% similarity — tolerant of typos / singular-plural).
    public static func isCorrect(_ given: String, answer: String, threshold: Double = 0.80) -> Bool {
        similarity(normalize(given), normalize(answer)) >= threshold
    }

    /// 1 - (edit distance / max length). 1.0 == identical.
    public static func similarity(_ a: String, _ b: String) -> Double {
        if a.isEmpty && b.isEmpty { return 1 }
        let dist = levenshtein(Array(a), Array(b))
        return 1.0 - Double(dist) / Double(max(a.count, b.count))
    }

    // MARK: - Leitner boxes (adaptive review)

    /// Move an item between Leitner boxes (0…maxBox); correct promotes, wrong resets to 0.
    public static func leitner(box: Int, correct: Bool, maxBox: Int = 5) -> Int {
        correct ? min(maxBox, box + 1) : 0
    }

    // MARK: - Helpers

    private static func normalize(_ s: String) -> String {
        s.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: " ")
    }

    private static func levenshtein(_ a: [Character], _ b: [Character]) -> Int {
        if a.isEmpty { return b.count }
        if b.isEmpty { return a.count }
        var prev = Array(0...b.count)
        var cur = [Int](repeating: 0, count: b.count + 1)
        for i in 1...a.count {
            cur[0] = i
            for j in 1...b.count {
                let cost = a[i - 1] == b[j - 1] ? 0 : 1
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            }
            swap(&prev, &cur)
        }
        return prev[b.count]
    }
}
