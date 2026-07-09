// swift-tools-version: 6.0
import PackageDescription

// PolarisStudyKit — an on-device study toolkit for iOS/iPadOS/macOS built on classical,
// deterministic ALGORITHMS (no AI): SM-2 spaced repetition, cloze flashcard generation,
// Levenshtein grading, rule-table citation formatting, and Flesch–Kincaid readability.
// No model download, no network, no Apple-Intelligence requirement — runs on any modern OS.
let package = Package(
    name: "PolarisStudyKit",
    platforms: [
        .iOS(.v15),
        .macOS(.v12),
        .visionOS(.v1),
    ],
    products: [
        .library(name: "PolarisStudyKit", targets: ["PolarisStudyKit"]),
    ],
    targets: [
        .target(name: "PolarisStudyKit"),
        .testTarget(name: "PolarisStudyKitTests", dependencies: ["PolarisStudyKit"]),
    ]
)
