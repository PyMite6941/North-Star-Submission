import Testing
import Foundation
@testable import PolarisStudyKit

// Every feature is a pure deterministic algorithm, so these run fully on CI (no device/model).

@Test func sixAreasHaveAlgorithms() {
    #expect(PolarisArea.allCases.count == 6)
    for area in PolarisArea.allCases {
        #expect(!area.algorithm.isEmpty)
        #expect(!area.title.isEmpty)
    }
    #expect(PolarisArea(key: "cv_builder") == .cvBuilder)
}

@Test func sm2PassGrowsIntervalThenLapseResets() {
    let day = Calendar.current.startOfDay(for: Date(timeIntervalSince1970: 1_700_000_000))
    var s = SM2State.new(on: day)
    s = SpacedRepetition.schedule(s, grade: 5, today: day)   // 1st pass
    #expect(s.interval == 1 && s.repetitions == 1)
    s = SpacedRepetition.schedule(s, grade: 5, today: day)   // 2nd pass
    #expect(s.interval == 6 && s.repetitions == 2)
    let grown = SpacedRepetition.schedule(s, grade: 4, today: day)  // grows × ease
    #expect(grown.interval > 6 && grown.repetitions == 3)
    let lapsed = SpacedRepetition.schedule(grown, grade: 1, today: day)
    #expect(lapsed.repetitions == 0 && lapsed.interval == 1 && lapsed.ease >= 1.3)
}

@Test func citationFormatsAPAandMLA() {
    let src = Source(authors: ["Smith, John Paul"], title: "On Photosynthesis",
                     year: "2020", container: "Journal of Biology")
    let apa = Citations.reference(src, style: .apa)
    #expect(apa.contains("Smith, J. P.") && apa.contains("(2020)"))
    #expect(Citations.inText(src, style: .apa) == "(Smith, 2020)")
    #expect(Citations.inText(src, style: .mla) == "(Smith)")
}

@Test func quizGradingIsFuzzy() {
    #expect(QuizEngine.isCorrect("mitochondria", answer: "Mitochondria"))
    #expect(QuizEngine.isCorrect("mitochondrion", answer: "mitochondria"))  // 1 edit
    #expect(!QuizEngine.isCorrect("nucleus", answer: "mitochondria"))
    #expect(QuizEngine.leitner(box: 2, correct: true) == 3)
    #expect(QuizEngine.leitner(box: 3, correct: false) == 0)
}

@Test func flashcardsAndReadability() {
    let text = "Mitochondria are the powerhouse of the cell. Photosynthesis converts light into energy."
    let cards = FlashcardGenerator.generate(from: text)
    #expect(!cards.isEmpty)
    let r = Readability.analyze(text)
    #expect(r.words > 0 && r.sentences == 2 && r.fleschReadingEase != 0)
}
