package com.polaris.studykit.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.polaris.studykit.Flashcard
import com.polaris.studykit.PolarisStudy
import com.polaris.studykit.Sm2State

/**
 * Minimal usage example — a flashcard study loop powered by pure algorithms (no AI).
 * Generation and SM-2 scheduling are instant and synchronous — no model file, no background
 * thread, no network. Mirrors `ios-native/Example/ContentView.swift`.
 */
class MainActivity : ComponentActivity() {

    private val polaris = PolarisStudy()
    private val notes =
        "Mitochondria are the powerhouse of the cell. " +
            "Photosynthesis converts light energy into chemical energy stored in glucose."

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                var cards by remember { mutableStateOf(emptyList<Flashcard>()) }
                var index by remember { mutableStateOf(0) }
                var revealed by remember { mutableStateOf(false) }
                var state by remember { mutableStateOf(Sm2State.new(0L)) }

                Surface(modifier = Modifier.fillMaxSize()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        if (cards.isEmpty()) {
                            Text("Turn notes into flashcards — no AI, just algorithms.")
                            Button(onClick = { cards = polaris.makeFlashcards(notes) }) {
                                Text("Generate flashcards")
                            }
                        } else {
                            val card = cards[index]
                            Text("Card ${index + 1} / ${cards.size}")
                            Text(card.question, style = MaterialTheme.typography.titleMedium)
                            if (revealed) {
                                Text(card.answer, style = MaterialTheme.typography.titleMedium)
                                Text("Grade your recall (SM-2):")
                                Row {
                                    listOf("Again" to 1, "Hard" to 3, "Good" to 4, "Easy" to 5)
                                        .forEach { (label, g) ->
                                            OutlinedButton(onClick = {
                                                state = polaris.review(state, g)  // SM-2 schedules next
                                                revealed = false
                                                index = (index + 1) % cards.size
                                            }) { Text(label) }
                                        }
                                }
                            } else {
                                Button(onClick = { revealed = true }) { Text("Show answer") }
                            }
                        }
                    }
                }
            }
        }
    }
}
