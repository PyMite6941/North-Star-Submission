// swift-tools-version: 6.2
import PackageDescription

// PolarisStudyKit — on-device implementation of the 6 Polaris areas for iOS/iPadOS/macOS
// using Apple's Foundation Models framework (iOS 26+). This is the on-device alternative to
// the Python thin-client path: the model runs entirely on the device, no Ollama, no network.
let package = Package(
    name: "PolarisStudyKit",
    platforms: [
        .iOS(.v26),
        .macOS(.v26),
        .visionOS(.v26),
    ],
    products: [
        .library(name: "PolarisStudyKit", targets: ["PolarisStudyKit"]),
    ],
    targets: [
        .target(name: "PolarisStudyKit"),
        .testTarget(name: "PolarisStudyKitTests", dependencies: ["PolarisStudyKit"]),
    ]
)
