# Theme — Polaris Student brand

The UI is themed to match **[polarisstudent.com](https://polarisstudent.com)** ("Polaris
Student — Your Academic Journey, Organized"). These tokens were taken from the site's own
CSS (`css/styles.css`) so our surfaces stay visually consistent with it.

## Colors

| Token | Hex | Use |
|-------|-----|-----|
| `--brand` | `#b22222` | Primary (firebrick) — buttons, links, primary color |
| `--brand-dark` | `#9b1c1c` | Hover / gradient end |
| `--brand-darker` | `#7f1d1d` | Deep accents |
| `--brand-light` | `#fde8e8` | Tint backgrounds |
| `--brand-xlight` | `#fff5f5` | Subtle tint |
| `--orange` | `#f97316` | Secondary; brand gradient end (red → orange) |
| `--blue` | `#2563eb` | Accent |
| `--purple` | `#7c3aed` | Accent |
| `--green` | `#16a34a` | Success accent |
| `--dark` / `--dark-2` / `--dark-3` | `#1a1a2e` / `#16213e` / `#0f3460` | "Constellation" navy header/hero |
| `--text` | `#1e293b` | Body text |
| `--text-muted` | `#64748b` | Secondary text |
| `--border` | `#e2e8f0` | Borders |
| `--bg-alt` | `#f8fafc` | Alt background |
| `--white` | `#ffffff` | Background |

**Signature gradient:** `linear-gradient(180deg, #b22222 0%, #f97316 100%)` (brand → orange).
**Hero/dark:** navy constellation gradient with sky-blue / green / purple radial star-glows.

## Typography

- **Headings:** `Plus Jakarta Sans` (600–800)
- **Body:** `Inter` (300–700)
- Loaded from Google Fonts. Icons on the site use Bootstrap Icons.

## Shape & elevation

- Radius: `16px` (sm `10px`, lg `24px`)
- Shadows: sm `0 2px 8px rgba(0,0,0,.06)`, base `0 4px 24px rgba(0,0,0,.08)`,
  brand `0 8px 32px rgba(178,34,34,.25)`

## Where it's applied

- **Streamlit web UI** (`webui/app.py` + `.streamlit/config.toml`) — primary color, fonts,
  brand-gradient header ("Polaris Student ⭐") and buttons.
- Reuse these tokens for any future front-end (or the `ios-native` app) to stay on-brand.
