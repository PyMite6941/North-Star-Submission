// Example SwiftUI screen wiring PolarisStudyKit to a flashcard-study UI.
// Everything here is instant + offline — it's pure algorithms (SM-2 + cloze generation), no AI.
// Not part of the Swift package build (it needs an app target with SwiftUI).
import SwiftUI
import PolarisStudyKit

@available(iOS 15.0, *)
struct ContentView: View {
    @State private var notes = "Mitochondria are the powerhouse of the cell. "
        + "Photosynthesis converts light energy into chemical energy stored in glucose."
    @State private var cards: [Flashcard] = []
    @State private var index = 0
    @State private var revealed = false
    @State private var state = SM2State.new()

    private let polaris = PolarisStudy()

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 14) {
                if cards.isEmpty {
                    Text("Paste study notes — Polaris makes flashcards with no AI.")
                        .font(.subheadline).foregroundStyle(.secondary)
                    TextEditor(text: $notes).frame(height: 160).border(.quaternary)
                    Button("Generate flashcards") { cards = polaris.makeFlashcards(from: notes) }
                        .buttonStyle(.borderedProminent)
                } else {
                    let card = cards[index]
                    Text("Card \(index + 1) / \(cards.count)").font(.caption).foregroundStyle(.secondary)
                    Text(card.question).font(.title3).bold()
                    if revealed {
                        Text(card.answer).font(.title3).foregroundStyle(.green)
                        Text("How well did you recall it? (SM-2)").font(.caption)
                        HStack {
                            ForEach([("Again", 1), ("Hard", 3), ("Good", 4), ("Easy", 5)], id: \.0) { label, g in
                                Button(label) { grade(g) }.buttonStyle(.bordered)
                            }
                        }
                    } else {
                        Button("Show answer") { revealed = true }.buttonStyle(.borderedProminent)
                    }
                }
                Spacer()
            }
            .padding()
            .navigationTitle("Polaris Study")
        }
    }

    private func grade(_ g: Int) {
        state = polaris.review(state, grade: g)   // SM-2 schedules the next review
        revealed = false
        index = (index + 1) % cards.count
    }
}
