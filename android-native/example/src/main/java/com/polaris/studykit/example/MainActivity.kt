package com.polaris.studykit.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.polaris.studykit.PolarisStudy
import com.polaris.studykit.PowerMode
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Minimal usage example — mirrors `ios-native/Example/ContentView.swift`.
 *
 * A real app would download/verify the model file on first run (see the module README);
 * this demo assumes a `.task` model has already been pushed to the path below (matches the
 * `adb push` step documented there). Inference runs off the main thread — it is not instant.
 */
class MainActivity : ComponentActivity() {

    private val modelPath = "/data/local/tmp/gemma3-1b-it-int4.task"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                var answer by remember { mutableStateOf("") }
                var loading by remember { mutableStateOf(false) }
                val scope = rememberCoroutineScope()

                Surface(modifier = Modifier.fillMaxSize()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Ask Polaris (on-device, ${PowerMode.LOW_POWER.name})")
                        Button(onClick = {
                            loading = true
                            scope.launch {
                                answer = withContext(Dispatchers.IO) {
                                    PolarisStudy(
                                        context = applicationContext,
                                        modelPath = modelPath,
                                        powerMode = PowerMode.LOW_POWER,
                                    ).use { polaris ->
                                        val result =
                                            polaris.answer("Quiz me on the French Revolution")
                                        "[${result.area.title}] ${result.text}"
                                    }
                                }
                                loading = false
                            }
                        }) {
                            Text(if (loading) "Thinking…" else "Ask a sample question")
                        }
                        Text(answer)
                    }
                }
            }
        }
    }
}
