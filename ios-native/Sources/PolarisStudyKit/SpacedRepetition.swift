import Foundation

/// SM-2 (SuperMemo 2) spaced-repetition scheduling — the algorithm behind flashcards.
///
/// No AI: given a card's current state and a recall grade 0–5, it deterministically computes
/// the next review interval, ease factor, and due date. Mirrors `packages/recall/sm2.py`.
public struct SM2State: Codable, Equatable, Sendable {
    public var ease: Double        // ease factor, floored at 1.3
    public var interval: Int       // days until next review
    public var repetitions: Int    // consecutive correct reviews
    public var due: Date           // next review date

    public init(ease: Double = 2.5, interval: Int = 0, repetitions: Int = 0, due: Date = Date()) {
        self.ease = ease
        self.interval = interval
        self.repetitions = repetitions
        self.due = due
    }

    public static func new(on day: Date = Date()) -> SM2State {
        SM2State(due: Calendar.current.startOfDay(for: day))
    }

    public var isDue: Bool { due <= Date() }
}

public enum SpacedRepetition {

    /// Advance an SM-2 state by a review graded 0–5 (>= 3 is a pass).
    /// - grade < 3: lapse — repetitions reset, review again tomorrow.
    /// - grade >= 3: interval grows (1, 6, then × ease); ease adjusts per SM-2.
    public static func schedule(_ state: SM2State, grade: Int, today: Date = Date()) -> SM2State {
        let g = max(0, min(5, grade))
        let cal = Calendar.current
        let start = cal.startOfDay(for: today)

        let repetitions: Int
        let interval: Int
        if g < 3 {
            repetitions = 0
            interval = 1
        } else {
            repetitions = state.repetitions + 1
            switch repetitions {
            case 1: interval = 1
            case 2: interval = 6
            default: interval = Int((Double(state.interval) * state.ease).rounded())
            }
        }

        // SM-2 ease update, floored at 1.3.
        let delta = 0.1 - Double(5 - g) * (0.08 + Double(5 - g) * 0.02)
        let ease = max(1.3, state.ease + delta)

        let due = cal.date(byAdding: .day, value: interval, to: start) ?? start
        return SM2State(ease: (ease * 1000).rounded() / 1000,
                        interval: interval, repetitions: repetitions, due: due)
    }

    /// Cards due today or earlier, soonest-due first.
    public static func due<T>(_ cards: [T], state: (T) -> SM2State, now: Date = Date()) -> [T] {
        cards.filter { state($0).due <= now }.sorted { state($0).due < state($1).due }
    }
}
