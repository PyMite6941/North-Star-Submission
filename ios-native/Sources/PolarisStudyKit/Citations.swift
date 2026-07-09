import Foundation

/// Deterministic citation formatter — the algorithm behind the "Citation" feature.
///
/// No AI: builds APA / MLA / Chicago references by applying each style's fixed rule table to
/// the source's fields (author, title, year, …). Also produces the matching in-text citation.
public struct Source: Sendable {
    public var authors: [String]   // "Last, First" each
    public var title: String
    public var year: String
    public var container: String    // journal / book / site name
    public var publisher: String
    public var url: String

    public init(authors: [String] = [], title: String = "", year: String = "",
                container: String = "", publisher: String = "", url: String = "") {
        self.authors = authors
        self.title = title
        self.year = year
        self.container = container
        self.publisher = publisher
        self.url = url
    }
}

public enum CitationStyle: String, CaseIterable, Sendable { case apa, mla, chicago }

public enum Citations {

    public static func reference(_ s: Source, style: CitationStyle) -> String {
        switch style {
        case .apa: return apa(s)
        case .mla: return mla(s)
        case .chicago: return chicago(s)
        }
    }

    /// In-text citation, e.g. "(Smith, 2020)" / "(Smith)" / "(Smith 2020)".
    public static func inText(_ s: Source, style: CitationStyle) -> String {
        let name = firstAuthorLast(s) ?? shortTitle(s)
        switch style {
        case .apa: return "(\(name), \(s.year))"
        case .mla: return "(\(name))"
        case .chicago: return "(\(name) \(s.year))"
        }
    }

    // MARK: - Styles

    private static func apa(_ s: Source) -> String {
        // Authors (Last, F. M.) & final "&"; (Year). Title. Container. Publisher. URL
        let a = joinAuthors(s.authors, sep: ", ", last: ", & ", initialsOnly: true)
        var out = a.isEmpty ? "" : "\(a) "
        out += "(\(s.year)). \(s.title)."
        if !s.container.isEmpty { out += " \(italicHint(s.container))." }
        if !s.publisher.isEmpty { out += " \(s.publisher)." }
        if !s.url.isEmpty { out += " \(s.url)" }
        return collapse(out)
    }

    private static func mla(_ s: Source) -> String {
        // Author. "Title." Container, Publisher, Year, URL.
        let a = joinAuthors(s.authors, sep: ", ", last: ", and ", initialsOnly: false)
        var parts: [String] = []
        if !a.isEmpty { parts.append("\(a).") }
        parts.append("\"\(s.title).\"")
        var tail: [String] = []
        if !s.container.isEmpty { tail.append(italicHint(s.container)) }
        if !s.publisher.isEmpty { tail.append(s.publisher) }
        if !s.year.isEmpty { tail.append(s.year) }
        if !s.url.isEmpty { tail.append(s.url) }
        parts.append(tail.joined(separator: ", ") + ".")
        return collapse(parts.joined(separator: " "))
    }

    private static func chicago(_ s: Source) -> String {
        // Author. Title. Container. Publisher, Year. URL.
        let a = joinAuthors(s.authors, sep: ", ", last: ", and ", initialsOnly: false)
        var out = a.isEmpty ? "" : "\(a). "
        out += "\(s.title)."
        if !s.container.isEmpty { out += " \(italicHint(s.container))." }
        var pubYear: [String] = []
        if !s.publisher.isEmpty { pubYear.append(s.publisher) }
        if !s.year.isEmpty { pubYear.append(s.year) }
        if !pubYear.isEmpty { out += " \(pubYear.joined(separator: ", "))." }
        if !s.url.isEmpty { out += " \(s.url)." }
        return collapse(out)
    }

    // MARK: - Helpers

    private static func firstAuthorLast(_ s: Source) -> String? {
        guard let first = s.authors.first else { return nil }
        return first.split(separator: ",").first.map(String.init)?
            .trimmingCharacters(in: .whitespaces)
    }

    private static func shortTitle(_ s: Source) -> String {
        s.title.split(separator: " ").prefix(2).joined(separator: " ")
    }

    private static func italicHint(_ text: String) -> String { "*\(text)*" }  // markdown italics

    private static func joinAuthors(_ authors: [String], sep: String, last: String,
                                    initialsOnly: Bool) -> String {
        let formatted = authors.map { initialsOnly ? initialsForm($0) : $0 }
        switch formatted.count {
        case 0: return ""
        case 1: return formatted[0]
        default:
            return formatted.dropLast().joined(separator: sep) + last + formatted.last!
        }
    }

    /// "Smith, John Paul" -> "Smith, J. P." (APA-style initials).
    private static func initialsForm(_ name: String) -> String {
        let parts = name.split(separator: ",", maxSplits: 1).map {
            $0.trimmingCharacters(in: .whitespaces)
        }
        guard parts.count == 2 else { return name }
        let initials = parts[1].split(separator: " ")
            .compactMap { $0.first.map { "\($0)." } }
            .joined(separator: " ")
        return "\(parts[0]), \(initials)"
    }

    private static func collapse(_ s: String) -> String {
        s.replacingOccurrences(of: "  ", with: " ")
            .replacingOccurrences(of: " .", with: ".")
            .trimmingCharacters(in: .whitespaces)
    }
}
