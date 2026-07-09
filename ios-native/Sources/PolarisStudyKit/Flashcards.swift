import Foundation

/// Algorithmic flashcard generation from study text — no AI.
///
/// Two deterministic strategies:
///  1. **Definition extraction** via "X is/are/means Y" sentence patterns → Q/A cards.
///  2. **Cloze deletion**: blank the most salient term in a sentence (longest non-stopword),
///     front = sentence with a blank, back = the term.
public struct Flashcard: Codable, Equatable, Sendable {
    public let question: String
    public let answer: String
    public init(question: String, answer: String) {
        self.question = question
        self.answer = answer
    }
}

public enum FlashcardGenerator {

    private static let stopwords: Set<String> = [
        "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "is", "are",
        "was", "were", "be", "been", "being", "that", "this", "these", "those", "it", "its",
        "as", "by", "with", "from", "at", "which", "who", "whom", "into", "than", "then",
    ]

    /// Generate up to `limit` cards from free-form study text.
    public static func generate(from text: String, limit: Int = 20) -> [Flashcard] {
        var cards: [Flashcard] = []
        var seen = Set<String>()
        for sentence in sentences(text) {
            if cards.count >= limit { break }
            if let card = definitionCard(sentence) ?? clozeCard(sentence),
               seen.insert(card.answer.lowercased()).inserted {
                cards.append(card)
            }
        }
        return cards
    }

    // MARK: - Strategies

    /// "Mitochondria are the powerhouse of the cell." -> Q: "What are mitochondria?" A: "the powerhouse…"
    private static func definitionCard(_ sentence: String) -> Flashcard? {
        for verb in [" is ", " are ", " means ", " refers to ", " is defined as "] {
            guard let range = sentence.range(of: verb) else { continue }
            let subject = String(sentence[..<range.lowerBound]).trimmingCharacters(in: .whitespaces)
            let predicate = String(sentence[range.upperBound...])
                .trimmingCharacters(in: CharacterSet(charactersIn: " ."))
            guard subject.split(separator: " ").count <= 5, !subject.isEmpty, !predicate.isEmpty
            else { continue }
            let isPlural = verb.contains("are")
            return Flashcard(question: "What \(isPlural ? "are" : "is") \(subject)?", answer: predicate)
        }
        return nil
    }

    /// Blank the most salient word in a sentence.
    private static func clozeCard(_ sentence: String) -> Flashcard? {
        let words = sentence.split(whereSeparator: { !$0.isLetter && $0 != "-" }).map(String.init)
        guard words.count >= 5 else { return nil }
        // Salience: longest word that isn't a stopword and is >= 4 chars.
        guard let key = words
            .filter({ $0.count >= 4 && !stopwords.contains($0.lowercased()) })
            .max(by: { $0.count < $1.count })
        else { return nil }
        let blanked = sentence.replacingOccurrences(of: key, with: "_____")
        return Flashcard(question: blanked, answer: key)
    }

    // MARK: - Helpers

    static func sentences(_ text: String) -> [String] {
        text.split(whereSeparator: { ".!?\n".contains($0) })
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { $0.split(separator: " ").count >= 4 }
    }
}
