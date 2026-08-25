# Navigation & detail page design spec

Personal portfolio site — mobile-first. Sections: Resume, Projects, Publications, Art. Cross-cutting tags (e.g. Oil, Drawing, Unicode, Patent). Utility: language (EN/DE), imprint.

See `WIREFRAME.html` for the full visual reference — open it in a browser; it follows your system light/dark preference.

---

## 1. Navigation architecture

Three tiers, don't mix them:

- **Primary nav** — Resume, Projects, Publications, Art. Identity-defining, always visible or one tap away.
- **Utility nav** — language switcher, imprint. Low-frequency, always-available, deliberately quiet.
- **Content taxonomy (tags)** — cross-cutting, discovery-oriented. Not a peer of primary nav.

## 2. Entry page

The site root. Shows:
- Logo (🌼) + one-line greeting/tagline
- The four sections as a **visible list with small representative icons/thumbnails** — not hidden behind the hamburger. Resume/Projects/Publications use icon tiles (CV, code, doc+PDF badge); Art uses an actual image thumbnail, since the image *is* the point there.
- A quiet footer row: `EN · DE · Imprint` — same muted weight for both, since hiding language entirely risks losing non-native visitors, but neither deserves primary-nav weight.

Logo (🌼) doubles as the home link from every other page — standard convention. The menu also includes an explicit "Home" row for sites where the logo isn't confidently recognizable as clickable.

**Overlap with the menu is intentional, not a smell.** The entry page and the menu list the same four destinations because the site only has four destinations. They serve different moments — entry page invites first-time browsing, menu gets someone already three levels deep back out fast — and use different presentation (icons/thumbnails vs. plain text) to signal that difference.

## 3. Menu (navigation drawer)

Terminology: **drawer**, states **collapsed / expanded** (Material Design convention). Avoid "hamburger" in documentation for other people — use it only as informal shorthand.

- Trigger (≡) sits in the header on every page, expanded state covers the screen with Home + four sections + language toggle + imprint.
- **Not a step in the navigation flow** — it's a component that overlays whatever page you triggered it from, and returns you to the same scroll position on close (✕ or tap outside).
- Document it once, as a component reference, not repeated at every page it can appear on.

## 4. Grid gallery (section & tag pages)

**Header — fixed two-line shape, used identically on every grid page** (section or tag), so the grid always starts at the same y-position:
- Line 1: title (+ back arrow on tag pages only)
- Line 2: muted item-count subtitle — `24 items` on a section page, `3 projects · 4 publications · 5 artworks` on a tag page (breakdown, not a flat count, since tag pages mix content types)
- ≡ trigger, top-right, always

**Tag chip row**, horizontally scrollable, deliberately clipped at the right edge as a scroll affordance (don't force it to fit).

**Grid tiles — mat + border, never edge-to-edge.** Solves two problems at once:
- Boring near-white document scans become invisible without a bordered card and inset padding around them; the mat gives them a visible container regardless of how light the content is.
- Vibrant, non-uniform artwork tiles stop clashing against each other when each has its own consistent card and gap, the way a gallery wall spaces individual pieces.

**Type badges, only where they carry information the thumbnail can't:**
- Publications/patents: small `PDF` badge, danger-colored
- Projects/code: `</>` badge, accent-colored — same glyph as the Projects icon on the entry page, for consistency
- Artwork: no badge — the image itself is already unambiguous, a badge there would be decoration, not information

## 5. Tag pages (pivot, not filter)

Tapping a tag chip **pivots to that tag across the whole site** (Art + Publications + Projects), not just within the current section — tags are cross-cutting by design, so scoping them to one section would defeat the point.

- **No "All" chip** — "All" only makes sense as a reset within a bounded parent scope (all of Art). A tag page has no such scope; back arrow or logo serves that role instead.
- Chip row: the current tag, active/non-dismissible, followed by tags that co-occur on items carrying it. Tapping a secondary chip **pivots again** (goes to that tag's page) rather than intersecting (AND-filtering) — on a catalog this size, intersections would frequently return zero or one result, a dead end. Revisit if the catalog grows large enough that faceted AND-filtering becomes genuinely useful.
- Back arrow returns to wherever you pivoted from, at the same scroll position.

**No dedicated "browse all tags" index page.** Worth building only when tags are the *primary* way people find content (large blogs, doc sites). Here, tags are a secondary refinement on a navigation structure that already works — organic discovery through the chip row, while already looking at something you care about, is more contextual than a cold tag-cloud link. Revisit if the tag vocabulary grows substantially.

## 6. Detail pages

**Consistent layout regardless of content type:**

1. Hero (see §7)
2. Title
3. Tag chip row — **always here, never on the hero.** Off the image means it never needs its own background-chip treatment to survive unpredictable image contrast; it just sits on the page background like any other text.
4. Metadata line (date, medium/format)
5. Description/abstract — clamped to ~3 lines with a "Read more" toggle, so prev/next stays reachable without scrolling past a wall of text. (Plain unclamped scrolling text is also acceptable — the clamp specifically helps if people are expected to flip through pieces quickly.)
6. Prev / next, bottom of page

**Call-to-action, by content type:**
- Publications/Projects (exit actions — leave the page for a file or another site): a labeled button, icon + text (`⬇ Download PDF`, GitHub mark + `Show on GitHub`). Icon alone isn't enough — visitors are mostly one-time and won't have learned a private icon vocabulary; text alone loses the fast visual scan.
- Artwork (within-page action — view larger, not leave): **no button.** The whole hero is tappable, signaled only by a small ⤢ icon top-right. Adding a labeled button next to something already tappable is redundant and inconsistent with the CTA's weight on the other two types.

## 7. Hero image treatment

**Never force-crop to the square grid thumbnail.** The teaser square is a deliberately chosen crop for the grid; the hero is the primary viewing experience and shouldn't lose content to cropping.

- Fixed-height hero **container** (not the image itself). The image sits inside at its native aspect ratio (`object-fit: contain`), centered.
- Portrait content (document scans, portrait artwork) → empty matte space left/right (**pillarbox**).
- Landscape content (talk slides, landscape artwork) → empty matte space top/bottom (**letterbox**).
- Because the container is fixed regardless of what's inside, all anchored elements — back arrow (top-left, always), CTA scrim (bottom, full width, publications/projects only), zoom icon (top-right, artwork only) — sit at the same position on every detail page, independent of image shape.
- CTA scrim is a **flat opaque panel**, not a gradient fade — guarantees legibility regardless of the source image's own contrast (a gradient assumes a dark image to fade into, which breaks on near-white scans).

### Matte color — by content type, not per image

Per-image (computed) matte color was considered and rejected: it reintroduces exactly the unpredictability the container was designed to remove. The fix is a two-branch **rule**, not a per-item decision — still fully deterministic, just type-aware rather than one flat value everywhere.

| Content type | Matte | Reasoning |
|---|---|---|
| Publications / documents | Standard neutral background token (light in light mode, dark in dark mode) | Reads like paper; a light mat is the natural association for a scanned page. |
| Art / Projects (photos, screenshots, paintings) | **Fixed dark neutral, `#2C2C2A`, independent of system theme** | Gallery/framing convention: light or white surrounds cause simultaneous contrast, visibly dulling color placed against them. A dark neutral is the standard choice for showing color accurately, in both light-mode and dark-mode browsing. |

**This is a deliberate exception to system-theme adaptation** and should be called out as such in the codebase (a comment, not just implicit behavior) — otherwise a future pass at theming will "fix" it by making the art matte follow the toggle, undoing the reason it's there.

Icon treatment (back arrow, zoom icon) inverts with the matte it sits on — light icon on translucent dark chip for the dark artwork matte, dark icon on light chip for the light document matte.

**Open question to confirm:** which bucket each section's teasers fall into. Publications/patents → light (scans). Art → dark (paintings/photos). Projects is ambiguous — code screenshots may read better on light or dark depending on your actual screenshot style; decide once you have real examples.

### System dark mode

The site follows the browser/OS `prefers-color-scheme` setting — no separate in-site toggle. All standard surface/text/border tokens flip automatically. The artwork matte above is the one deliberate exception that does *not* flip.

## 8. Fullscreen image viewer

Reached by tapping the hero image (artwork) or the ⤢ icon. Near-black background regardless of theme (viewer convention, isolates the image from any surrounding chrome). ✕ to dismiss (returns to the detail page at the same scroll position), image counter (`3 / 12`), edge chevrons for prev/next matching the detail page's relationship. No CTA inside — this view is for looking, not acting.

## 9. Responsive behavior

### Mobile portrait — primary target, fully specified above and in `WIREFRAME.html`.

### Mobile landscape

Not a separate designed state — a responsive reflow of the same components. Conventions to apply, no new wireframe needed:

- **Collapse header vertical chrome.** The two-line grid header (title + item-count subtitle) is the first casualty of limited vertical space in landscape — either drop to a single line (subtitle hidden or moved inline after a middot) or keep it but accept a shorter visible grid area above the fold.
- **Wider grid, more columns.** Landscape phone widths (roughly 568–926px) sit close to small-tablet territory — bump from 3 columns to 4–5 rather than keeping the portrait column count and getting oversized tiles.
- **Detail page: switch to two-column, not stacked.** The tall stacked hero-then-metadata layout doesn't fit a short, wide viewport well. Once width exceeds height (`orientation: landscape` + a height threshold, not a fixed pixel breakpoint — a landscape phone and a portrait tablet can share a width but need different treatment), move to hero-left, metadata/description/CTA-right — effectively borrowing the tablet/desktop detail layout rather than inventing a third one.
- **Narrower drawer, not full-width.** A full-viewport-width drawer makes sense on a narrow portrait screen; in landscape, a partial-width slide-in panel (max ~360–400px) reads better and leaves the underlying page visible for context.
- **Fullscreen viewer needs no change** — it's already orientation-agnostic (`contain`-fit image, corner-anchored controls), and landscape is in fact the *natural* orientation for landscape artwork and slides.
- **Account for safe-area insets.** Contemporary phones have rounded corners / camera cutouts on the long edges in landscape; pad interactive elements near the left/right edges with `env(safe-area-inset-left/right)` so controls aren't clipped or awkwardly close to a curve.

### Tablet / desktop

Covered earlier in this design process — brief recap:
- Primary nav collapses to a horizontal bar once there's room for all four labels + utility nav without crowding (~768–1024px).
- Language/imprint move directly into the header; imprint can stay footer-only by convention.
- Grid goes to 4–6 columns via `auto-fill`/`minmax`, same tile treatment.
- Detail page becomes two-column (hero left, metadata/CTA sidebar right) rather than the CTA floating over the image.
- Prev/next become larger circular arrow buttons at the image edges rather than a small text row — consider adding arrow-key support alongside, since desktop visitors are more likely to use a keyboard.
- Tag chip row keeps the same scrolling pattern rather than switching to a sidebar, for consistency across breakpoints, unless the tag vocabulary grows large.
