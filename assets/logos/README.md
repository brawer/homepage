# Organisation marks — résumé timeline

Single-colour SVG marks for past employers/institutions, shown in the
`/resume/` timeline (`layouts/partials/resume-marker.html`). Rendered
inline and recoloured to the page's own text colour via
`fill: currentColor`, so they stay monochrome and work in dark mode.

## Why these are here

These are third-party trademarks. They are used **nominatively** — to
identify real past employers on a personal résumé, the same way a
LinkedIn profile shows an employer's logo. They do not imply
endorsement or sponsorship, and each is shown small, monochrome, and
next to the organisation's own name. This is a deliberate call by
Sascha (2026-09-07), reversing the earlier "generic iconography only"
line in `DESIGN_BRIEF.md`.

Organisations with no usable mark, or whose only mark is a busy crest
that turns to mush at ~42 px, get a generic glyph instead
(`../icons/building.svg` for a company, `../icons/mortarboard.svg` for a
university) — see the résumé front-matter `marker` field.

## Provenance & preparation

Each file was sourced by Sascha from the organisation's own brand/press
material, then sanitised for inline use: XML declaration, metadata,
`<style>` blocks, hard-coded fills, `width`/`height` and editor cruft
removed; namespaced elements flattened; a single `viewBox` kept;
`fill="currentColor"` set on the root. The pristine originals are kept
outside the repo.

| File | Mark | Notes |
|---|---|---|
| `apple.svg` | Apple | symbol; nudged up 7 % in CSS (bottom-heavy in its box) |
| `google.svg` | Google "G" | four colour segments flattened to one path group |
| `xerox.svg` | Xerox digital-X | `logo_scale: 0.52` (heavy solid shape reads large) |
| `niantic.svg` | Niantic balloon | |
| `saarland_university.svg` | Universität des Saarlandes seal | `logo_scale: 0.6` |
| `eth.svg` | ETH Zürich wordmark | `logo_wide: true` — 3:1 lockup, not a square symbol |
| `zurich_university.svg` | Universität Zürich wordmark | `logo_wide: true`, `logo_scale: 0.78` |
