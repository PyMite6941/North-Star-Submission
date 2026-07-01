import Testing
@testable import PolarisStudyKit

// These tests cover the pure logic (area registry / key mapping). The on-device model
// itself requires a real Apple-Intelligence device, so generation is exercised in the app.

@Test func sixAreasExist() {
    #expect(PolarisArea.allCases.count == 6)
}

@Test func keysMatchPythonBuild() {
    #expect(PolarisArea(key: "cv_builder") == .cvBuilder)
    #expect(PolarisArea(key: "FLASHCARDS") == .flashcards)
    #expect(PolarisArea(key: "nonsense") == nil)
}

@Test func everyAreaHasPrompt() {
    for area in PolarisArea.allCases {
        #expect(!area.systemPrompt.isEmpty)
        #expect(!area.title.isEmpty)
    }
}
