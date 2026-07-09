package com.polaris.studykit

/**
 * Deterministic citation formatter — the algorithm behind the "Citation" feature.
 * Applies each style's fixed rule table (APA / MLA / Chicago) to the source fields.
 */
data class Source(
    val authors: List<String> = emptyList(),   // "Last, First" each
    val title: String = "",
    val year: String = "",
    val container: String = "",                 // journal / book / site
    val publisher: String = "",
    val url: String = "",
)

enum class CitationStyle { APA, MLA, CHICAGO }

object Citations {

    fun reference(s: Source, style: CitationStyle): String = when (style) {
        CitationStyle.APA -> apa(s)
        CitationStyle.MLA -> mla(s)
        CitationStyle.CHICAGO -> chicago(s)
    }

    fun inText(s: Source, style: CitationStyle): String {
        val name = firstAuthorLast(s) ?: s.title.split(" ").take(2).joinToString(" ")
        return when (style) {
            CitationStyle.APA -> "($name, ${s.year})"
            CitationStyle.MLA -> "($name)"
            CitationStyle.CHICAGO -> "($name ${s.year})"
        }
    }

    private fun apa(s: Source): String {
        val a = joinAuthors(s.authors, ", ", ", & ", initialsOnly = true)
        val sb = StringBuilder()
        if (a.isNotEmpty()) sb.append("$a ")
        sb.append("(${s.year}). ${s.title}.")
        if (s.container.isNotEmpty()) sb.append(" *${s.container}*.")
        if (s.publisher.isNotEmpty()) sb.append(" ${s.publisher}.")
        if (s.url.isNotEmpty()) sb.append(" ${s.url}")
        return collapse(sb.toString())
    }

    private fun mla(s: Source): String {
        val a = joinAuthors(s.authors, ", ", ", and ", initialsOnly = false)
        val parts = mutableListOf<String>()
        if (a.isNotEmpty()) parts.add("$a.")
        parts.add("\"${s.title}.\"")
        val tail = listOfNotNull(
            s.container.ifEmpty { null }?.let { "*$it*" },
            s.publisher.ifEmpty { null }, s.year.ifEmpty { null }, s.url.ifEmpty { null },
        )
        parts.add(tail.joinToString(", ") + ".")
        return collapse(parts.joinToString(" "))
    }

    private fun chicago(s: Source): String {
        val a = joinAuthors(s.authors, ", ", ", and ", initialsOnly = false)
        val sb = StringBuilder()
        if (a.isNotEmpty()) sb.append("$a. ")
        sb.append("${s.title}.")
        if (s.container.isNotEmpty()) sb.append(" *${s.container}*.")
        val pubYear = listOfNotNull(s.publisher.ifEmpty { null }, s.year.ifEmpty { null })
        if (pubYear.isNotEmpty()) sb.append(" ${pubYear.joinToString(", ")}.")
        if (s.url.isNotEmpty()) sb.append(" ${s.url}.")
        return collapse(sb.toString())
    }

    private fun firstAuthorLast(s: Source): String? =
        s.authors.firstOrNull()?.substringBefore(",")?.trim()?.ifEmpty { null }

    private fun joinAuthors(
        authors: List<String>, sep: String, last: String, initialsOnly: Boolean,
    ): String {
        val f = authors.map { if (initialsOnly) initialsForm(it) else it }
        return when (f.size) {
            0 -> ""
            1 -> f[0]
            else -> f.dropLast(1).joinToString(sep) + last + f.last()
        }
    }

    /** "Smith, John Paul" -> "Smith, J. P." */
    private fun initialsForm(name: String): String {
        val parts = name.split(",", limit = 2).map { it.trim() }
        if (parts.size != 2) return name
        val initials = parts[1].split(" ").filter { it.isNotEmpty() }
            .joinToString(" ") { "${it.first()}." }
        return "${parts[0]}, $initials"
    }

    private fun collapse(s: String): String =
        s.replace("  ", " ").replace(" .", ".").trim()
}
