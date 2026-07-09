plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.polaris.studykit"
    compileSdk = 34

    defaultConfig {
        minSdk = 26
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
}

dependencies {
    // No AI/LLM runtime — every feature is a pure Kotlin algorithm (SM-2, Levenshtein,
    // rule-table citations, Flesch–Kincaid). Nothing to download; runs on any device.
    testImplementation("junit:junit:4.13.2")
}
