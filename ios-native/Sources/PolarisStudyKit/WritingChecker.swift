import Foundation

/// Offline, deterministic writing checker (grammar / style / clarity) — no AI.
///
/// This is the on-device, works-offline tier of the writing assistant, mirroring
/// `packages/writing/rules.py`. The AI coach ("Polly") is an **online-only** feature: call its
/// API only when the device has connectivity; this checker always works.
public struct WritingIssue: Sendable, Equatable {
    public let range: Range<String.Index>
    public let type: String        // grammar | style | clarity | punctuation
    public let message: String
    public let suggestion: String?
    public let matched: String
}

public enum WritingChecker {

    private static let wordiness: [String: String] = [
        "in order to": "to", "due to the fact that": "because", "in the event that": "if",
        "at this point in time": "now", "a large number of": "many", "a majority of": "most",
        "for the purpose of": "to", "has the ability to": "can", "with regard to": "about",
        "each and every": "every", "in spite of the fact that": "although",
    ]
    private static let weasel: Set<String> = [
        "very", "really", "quite", "rather", "somewhat", "fairly", "actually", "basically",
        "clearly", "obviously", "simply", "just", "totally", "extremely",
    ]
    private static let confusables: [String: String] = [
        "its": "it's", "it's": "its", "their": "there/they're", "there": "their/they're",
        "your": "you're", "you're": "your", "affect": "effect", "effect": "affect",
        "then": "than", "than": "then", "loose": "lose",
    ]

    /// Analyze `text` and return located issues (grammar/style/clarity/punctuation).
    public static func check(_ text: String) -> [WritingIssue] {
        var issues: [WritingIssue] = []
        let lower = text.lowercased()

        // Wordy phrases.
        for (phrase, repl) in wordiness {
            for range in ranges(of: phrase, in: lower, source: text) {
                issues.append(.init(range: range, type: "clarity", message: "Wordy — tighten this",
                                    suggestion: repl, matched: String(text[range])))
            }
        }

        // Per-word: weasel words + confusables + repeated words.
        let words = tokenize(text)
        for (i, tok) in words.enumerated() {
            let w = tok.text.lowercased()
            if weasel.contains(w) {
                issues.append(.init(range: tok.range, type: "style",
                                    message: "Weak intensifier “\(tok.text)” — cut or strengthen",
                                    suggestion: "(delete)", matched: tok.text))
            } else if let alt = confusables[w] {
                issues.append(.init(range: tok.range, type: "grammar",
                                    message: "Commonly confused: check “\(tok.text)” vs “\(alt)”",
                                    suggestion: nil, matched: tok.text))
            }
            if i > 0, words[i - 1].text.lowercased() == w {  // repeated adjacent word
                let r = words[i - 1].range.lowerBound..<tok.range.upperBound
                issues.append(.init(range: r, type: "grammar", message: "Repeated word “\(tok.text)”",
                                    suggestion: tok.text, matched: String(text[r])))
            }
        }

        // Passive voice.
        passive(text, into: &issues)
        // Double spaces.
        for range in regexRanges("  +", in: text) {
            issues.append(.init(range: range, type: "punctuation", message: "Extra space",
                                suggestion: " ", matched: String(text[range])))
        }
        // Long sentences.
        for sentence in sentenceRanges(text) {
            let n = tokenize(String(text[sentence])).count
            if n > 30 {
                issues.append(.init(range: sentence, type: "clarity",
                                    message: "Long sentence (\(n) words) — consider splitting",
                                    suggestion: nil, matched: String(text[sentence]).trimmed(40)))
            }
        }

        return issues.sorted { $0.range.lowerBound < $1.range.lowerBound }
    }

    /// A 0–100 quality score from the issue mix (matches the Python scoring).
    public static func score(_ text: String, issues: [WritingIssue]) -> Int {
        let words = max(1, tokenize(text).count)
        let weights = ["grammar": 4, "clarity": 3, "style": 2, "punctuation": 1]
        let penalty = issues.reduce(0.0) { $0 + Double(weights[$1.type] ?? 2) }
        let density = penalty / (Double(words) / 100 + 1)
        return max(0, min(100, Int((100 - density).rounded())))
    }

    // MARK: - Helpers

    private struct Token { let text: String; let range: Range<String.Index> }

    private static func tokenize(_ text: String) -> [Token] {
        var tokens: [Token] = []
        var start: String.Index?
        for i in text.indices {
            if text[i].isLetter || text[i] == "'" {
                if start == nil { start = i }
            } else if let s = start {
                tokens.append(Token(text: String(text[s..<i]), range: s..<i)); start = nil
            }
        }
        if let s = start { tokens.append(Token(text: String(text[s...]), range: s..<text.endIndex)) }
        return tokens
    }

    private static func ranges(of phrase: String, in lower: String,
                               source: String) -> [Range<String.Index>] {
        var out: [Range<String.Index>] = []
        var search = lower.startIndex
        while let r = lower.range(of: phrase, range: search..<lower.endIndex) {
            // Map the lowercased offsets back onto the source (same length).
            let lo = source.index(source.startIndex, offsetBy: lower.distance(from: lower.startIndex, to: r.lowerBound))
            let hi = source.index(source.startIndex, offsetBy: lower.distance(from: lower.startIndex, to: r.upperBound))
            out.append(lo..<hi)
            search = r.upperBound
        }
        return out
    }

    private static func regexRanges(_ pattern: String, in text: String) -> [Range<String.Index>] {
        guard let re = try? NSRegularExpression(pattern: pattern) else { return [] }
        let ns = text as NSString
        return re.matches(in: text, range: NSRange(location: 0, length: ns.length)).compactMap {
            Range($0.range, in: text)
        }
    }

    private static func passive(_ text: String, into issues: inout [WritingIssue]) {
        let pattern = "\\b(is|are|was|were|be|been|being|get|got)\\s+\\w+ed\\b"
        for range in regexRanges(pattern, in: text) {
            issues.append(.init(range: range, type: "clarity",
                                message: "Passive voice — prefer an active subject",
                                suggestion: nil, matched: String(text[range])))
        }
    }

    private static func sentenceRanges(_ text: String) -> [Range<String.Index>] {
        var out: [Range<String.Index>] = []
        var start = text.startIndex
        for i in text.indices where ".!?".contains(text[i]) {
            let next = text.index(after: i)
            out.append(start..<next); start = next
        }
        if start < text.endIndex { out.append(start..<text.endIndex) }
        return out
    }
}

private extension String {
    func trimmed(_ n: Int) -> String {
        let t = trimmingCharacters(in: .whitespacesAndNewlines)
        return t.count <= n ? t : String(t.prefix(n)) + "…"
    }
}
