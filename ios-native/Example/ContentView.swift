// Example SwiftUI screen wiring PolarisStudyKit to a chat-style UI.
// Drop this into an iOS 26 app target that depends on PolarisStudyKit.
//
// Not part of the Swift package build (it needs an app target with SwiftUI).
import SwiftUI
import PolarisStudyKit

@available(iOS 26.0, *)
struct ContentView: View {
    @State private var prompt = "Make flashcards on the Krebs cycle"
    @State private var answer = ""
    @State private var area = ""
    @State private var busy = false
    @State private var error: String?

    private let polaris = PolarisStudy()

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 12) {
                TextField("Ask anything (flashcards, quiz, CV, essay…)", text: $prompt, axis: .vertical)
                    .textFieldStyle(.roundedBorder)

                Button(busy ? "Thinking…" : "Ask Polaris") { Task { await ask() } }
                    .buttonStyle(.borderedProminent)
                    .disabled(busy || prompt.isEmpty)

                if !area.isEmpty {
                    Text("Area: \(area)").font(.caption).foregroundStyle(.secondary)
                }
                ScrollView { Text(answer).frame(maxWidth: .infinity, alignment: .leading) }

                if let error { Text(error).foregroundStyle(.red).font(.footnote) }
                Spacer()
            }
            .padding()
            .navigationTitle("Polaris Study")
        }
    }

    private func ask() async {
        busy = true; error = nil; answer = ""; area = ""
        defer { busy = false }
        do {
            let result = try await polaris.answer(to: prompt)
            area = result.area.title
            answer = result.text
        } catch {
            self.error = "On-device model unavailable: \(error). Requires an Apple-Intelligence device with iOS 26+."
        }
    }
}
