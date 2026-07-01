import FoundationModels

/// On-device study assistant: routes a request to one of the six Polaris areas, then answers
/// with that area's specialized prompt — all running locally via Apple's Foundation Models.
///
/// This mirrors the LangGraph router→handler topology in `packages/study_llm`, but the graph
/// is two `LanguageModelSession` calls because the model executes entirely on the device.
@available(iOS 26.0, macOS 26.0, visionOS 26.0, *)
public actor PolarisStudy {

    public init() {}

    /// Structured router decision (Foundation Models guided generation).
    @Generable
    struct RouteDecision {
        @Guide(
            description: "The single best area key",
            .anyOf(["flashcards", "quizzing", "cv_builder", "advisor", "citation", "essay"])
        )
        var area: String

        @Guide(description: "One short sentence explaining the choice")
        var reason: String
    }

    public struct Answer: Sendable {
        public let area: PolarisArea
        public let reason: String
        public let text: String
    }

    public enum PolarisError: Error, Sendable {
        case modelUnavailable(String)
    }

    /// Whether the on-device model is ready (device supports Apple Intelligence and it's enabled).
    public func isAvailable() -> Bool {
        if case .available = SystemLanguageModel.default.availability { return true }
        return false
    }

    /// Route the prompt to an area, then generate the answer — fully on-device.
    public func answer(to prompt: String) async throws -> Answer {
        guard case .available = SystemLanguageModel.default.availability else {
            let reason: String
            if case let .unavailable(r) = SystemLanguageModel.default.availability {
                reason = String(describing: r)
            } else {
                reason = "unknown"
            }
            throw PolarisError.modelUnavailable(reason)
        }

        // 1. Route (structured output keeps the choice constrained to the 6 keys).
        let router = LanguageModelSession {
            """
            You route a student's request to exactly one capability area. Choose the single best fit.
            Areas:
            - flashcards: \(PolarisArea.flashcards.summary)
            - quizzing: \(PolarisArea.quizzing.summary)
            - cv_builder: \(PolarisArea.cvBuilder.summary)
            - advisor: \(PolarisArea.advisor.summary)
            - citation: \(PolarisArea.citation.summary)
            - essay: \(PolarisArea.essay.summary)
            """
        }
        let decision = try await router.respond(to: prompt, generating: RouteDecision.self)
        let area = PolarisArea(key: decision.content.area) ?? .advisor

        // 2. Answer with the chosen area's specialized prompt.
        let session = LanguageModelSession { area.systemPrompt }
        let response = try await session.respond(to: prompt)

        return Answer(area: area, reason: decision.content.reason, text: response.content)
    }
}
