import Foundation

/// Deterministic writing analysis for the "Essay" feature — no AI.
///
/// Computes **Flesch Reading Ease** and the **Flesch–Kincaid grade level** (classic 1975
/// formulas) plus simple structural signals (avg sentence length, long-sentence and
/// passive-voice heuristics) to give students concrete, rule-based feedback.
public struct ReadabilityReport: Sendable {
    public let words: Int
    public let sentences: Int
    public let syllables: Int
    public let fleschReadingEase: Double   // higher = easier (0–100+)
    public let fleschKincaidGrade: Double  // US grade level
    public let avgSentenceLength: Double
    public let longSentences: Int          // > 25 words
    public let passiveHits: Int            // heuristic

    public var summary: String {
        String(format: "Reading ease %.0f · grade %.1f · %d words, %d sentences (avg %.1f/sentence)",
               fleschReadingEase, fleschKincaidGrade, words, sentences, avgSentenceLength)
    }
}

public enum Readability {

    public static func analyze(_ text: String) -> ReadabilityReport {
        let sentenceList = text.split(whereSeparator: { ".!?".contains($0) })
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        let wordList = text.split(whereSeparator: { !$0.isLetter && $0 != "'" }).map(String.init)

        let nWords = max(1, wordList.count)
        let nSentences = max(1, sentenceList.count)
        let nSyll = wordList.reduce(0) { $0 + syllables(in: $1) }

        let wps = Double(nWords) / Double(nSentences)
        let spw = Double(nSyll) / Double(nWords)
        let ease = 206.835 - 1.015 * wps - 84.6 * spw
        let grade = 0.39 * wps + 11.8 * spw - 15.59

        let longS = sentenceList.filter { $0.split(separator: " ").count > 25 }.count
        let passive = passiveHeuristic(wordList)

        return ReadabilityReport(
            words: nWords, sentences: nSentences, syllables: nSyll,
            fleschReadingEase: round(ease * 10) / 10,
            fleschKincaidGrade: round(grade * 10) / 10,
            avgSentenceLength: round(wps * 10) / 10,
            longSentences: longS, passiveHits: passive)
    }

    /// Heuristic English syllable count (vowel-group based, with common adjustments).
    static func syllables(in word: String) -> Int {
        let w = word.lowercased().filter { $0.isLetter }
        guard !w.isEmpty else { return 0 }
        let vowels = Set("aeiouy")
        var count = 0
        var prevVowel = false
        for ch in w {
            let isVowel = vowels.contains(ch)
            if isVowel && !prevVowel { count += 1 }
            prevVowel = isVowel
        }
        if w.hasSuffix("e") && count > 1 { count -= 1 }         // silent 'e'
        return max(1, count)
    }

    /// Count "to be" + past-participle-ish patterns as a rough passive-voice signal.
    private static func passiveHeuristic(_ words: [String]) -> Int {
        let be: Set<String> = ["is", "are", "was", "were", "be", "been", "being"]
        var hits = 0
        for i in 0..<max(0, words.count - 1) {
            if be.contains(words[i].lowercased()), words[i + 1].lowercased().hasSuffix("ed") {
                hits += 1
            }
        }
        return hits
    }
}
