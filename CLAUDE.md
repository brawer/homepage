# CLAUDE.md — brawer.ch

Personal Hugo site for Sascha Brawer. Deployed via GitHub Actions
(exact deploy target — container vs. scp — not yet decided). Working
in a content-first order: filling in real content before building
templates/CSS via `/design` mode.

## Site structure

- Sections: Art (`/art/`), Projects (`/projects/`, no entries yet —
  renamed from "Programming" partway through; if you see "Programming"
  or `/programming/` anywhere it's stale and should be fixed),
  Publications (`/publications/` — renamed from "papers" partway
  through; if you see "papers" anywhere it's stale and should be
  fixed), Résumé (`/resume/`, doesn't exist yet).
- Menu order (see `hugo.toml` weights): Résumé, Projects,
  Publications, Art.
- Homepage (`content/_index.*.md`) is deliberately just a greeting.
  Intro sentence, social icons, and section links are template-driven
  from `Site.Params.intro`, `Site.Params.social`, and
  `Site.Menus.main` respectively — not duplicated into content. Any
  homepage template needs to pull from those, not hardcode a list.

## Bilingual (EN/DE)

- `defaultContentLanguage = "en"`; English at `/`, German at `/de/`.
- Per-item content: `index.en.md` / `index.de.md` in the same page
  bundle, sharing bundle resources (images/PDFs) automatically.
- **Policy: fully bilingual, no exceptions.** Every content item needs
  both `index.en.md` and `index.de.md` (or a symlink between them if
  the text is genuinely identical in both languages — see below).
  Missing a translation is a content gap to fix, not an accepted
  asymmetry. This reverses an earlier decision in this project — if
  you see older notes or content saying "German-only is fine, it just
  won't appear on the English site," that policy no longer applies.
- **Identical-content items** (same text works in both languages) use
  a symlink — `ln -s index.en.md index.de.md` — rather than a
  duplicate file. Requires `core.symlinks true` in git config; verify
  with `git ls-files -s` (mode `120000` = correctly a symlink, not
  `100644`).
- Internal Markdown links are hand-written per language:
  `/tags/memes/` on English pages, `/de/tags/memes/` on German pages.
  Hugo does not auto-localize plain Markdown links — easy to get
  wrong when copy-pasting between language files.
- **Known gaps to fix** (as of last content session — check before
  assuming this list is current): `content/publications/JP6511221B2/`
  (the Japanese geographic-name-transliteration patent) has only
  `index.en.md` and needs a German version — this is the only
  remaining gap. `transliteration-with-icu/index.de.md` is now a
  symlink to the English file (same talk, same text in both
  languages), and the homepage (`content/_index.de.md`) now exists.
  Worth adding a build-time or CI check that fails when a bundle has
  one language file but not the other (excluding intentional symlink
  pairs, which will show up fine since the symlink itself satisfies
  the check).

## Typography (applies to content, not just templates)

- German content follows **Swiss conventions (de-CH)**, not
  German-German. Quotes: «guillemets» for double, ‹single guillemets›
  for nested — not „low-high" or ‚low-high'. No space between the
  guillemet and the text: «wie er sagte», not « wie er sagte ».
  Also de-CH drops ß in favor of ss throughout.
- English content: “curly double” / ‘curly single’ quotes.
- Dashes: English uses em dash (—, no surrounding spaces). German
  uses en dash (–, with surrounding spaces on both sides).
- Write these characters directly in Markdown source — don't rely on
  Goldmark's typographer extension to produce them automatically; its
  substitution table isn't per-language and won't produce guillemets.
- `hugo.toml`'s `[languages.de]` block sets `languageCode = "de-CH"`
  (not plain `de`) specifically to flag this convention, even though
  the language *key* (and therefore file suffixes/`de` URL prefix)
  stayed `de` — renaming the key would have forced renaming every
  German content file in the repo, which wasn't worth it just to
  change one config string.
- **Not yet retrofitted**: content written before this policy was
  decided still has German-German „low-high" quotes — e.g.
  `content/publications/programming-techniques-in-cl/index.de.md` has
  „Datenbank"-Anfragen, needs to become «Datenbank»-Anfragen. Do a
  full grep for „ and " across `content/**/index.de.md` before
  considering content complete. Separately, several `index.de.md`
  files still use plain em dashes (—) instead of the required en dash
  with surrounding spaces — at least `art/anti-joke-chicken`,
  `art/golden-retriever`, `tags/memes`, and
  `publications/programming-techniques-in-cl` need this fixed; grep
  for — across `content/**/index.de.md` and `content/**/_index.de.md`
  too (the symlinked `transliteration-with-icu/index.de.md` is exempt
  since its text is the English original, not German prose).
- See `DESIGN_BRIEF.md` for the template-side implications (don't
  hardcode straight quotes/plain hyphens in UI chrome strings).

## Tags (taxonomy)

- `[taxonomies] tag = "tags"` in `hugo.toml`.
- Some tags share one term across both languages (e.g. `Memes` — a
  loanword, deliberately not translated).
- Some tags are translated (`Animals`/`Tiere`, `Oil`/`Öl`) — each pair
  lives at `content/tags/<term>/_index.<lang>.md` in *different*
  folders, and each page MUST carry a matching `translationKey` (e.g.
  `tag-animals`) so Hugo knows they're the same concept — it can't
  infer that from differing folder names the way it does for
  `index.en.md`/`index.de.md` pairs. Naming convention:
  `tag-<english-term-lowercase>` (e.g. `tag-memes`, `tag-oil`).
- Tag pages can hold real body content — e.g.
  `content/tags/memes/_index.*.md` explains the "memes painted in
  oil, as a series" concept once; individual art pieces link to the
  tag page (`[Memes](/tags/memes/)`) instead of repeating it.
- Tag casing: Title Case by default (`Memes`, `Animals`, `Oil`,
  `Geo`, `NLP`), except acronyms/numeronyms with their own strong
  lowercase convention (`NLP` stays all-caps, `i18n` stays all
  lowercase — treat these as the general rule, not one-off
  exceptions).

## Art bundle front matter

`title`, `date`, `publishDate`, `tags`, `medium`, `height_cm`,
`width_cm` (deliberately two numeric fields, not one `dimensions`
string — art convention is height × width, so `height_cm` is always
the physical top-to-bottom measurement regardless of orientation),
`image` (WebP filename, shared across language variants).

## Publications bundle front matter

`title`, `date`, `publishDate`, `tags`, `kind` (one of `"talk"`,
`"paper"`, `"patent"`, `"book"`, `"lecture"` — lowercase, same value
in every language, since it's an internal value templates branch on,
not display text; translate it for display via i18n strings, e.g.
`{{ i18n (printf "kind_%s" .Params.kind) }}`, not by changing the
front matter value itself), `authors` (list, order matters —
verified against source for patents), `venue`, `abstract`.

- `venue` can contain inline Markdown links, not just plain text —
  e.g. `modellieren-raumbezogener-daten` links the coordinating body's
  name to its own site (`KOGIS` in German, `COGIS` in English — same
  body, different acronym per language, plus `swisstopo`, each with
  its own link). Templates must render `venue` through `markdownify`
  rather than outputting it as a raw string, or these links won't
  render.

- Type-specific optional fields: `degree` (thesis), `patent_number` +
  `patent_status` + `assignee` (patent — `assignee` is the entity the
  patent was assigned to, typically the employer at the time of
  invention, e.g. `"Google LLC"` — use the assignee's official current
  name (check patents.google.com), not an informal shorthand; a
  single string, same value in both
  languages since it's a fact, not display text — don't translate it
  the way `kind` gets translated for display).
- `original_title` + `original_language` (BCP-47 tag) — for when the
  source document's real title differs from the page's own working
  `title` (e.g. the Japanese patent's actual title vs. its English
  working title). This is unrelated to the EN/DE bundle mechanism —
  both language files of the same item carry the same
  `original_title`, since it's a fact about the source document, not
  about site language.
- Single-PDF items use a `pdf` field. Multi-resource items (e.g. the
  `programming-techniques-in-cl` lecture series with dozens of PDFs)
  have no `pdf` field — links go directly in the Markdown body as
  relative links to bundle resources, which Hugo resolves
  automatically; no custom front-matter schema needed for that case.

## Images

- Store as WebP, not JPEG/HEIC:
  `cwebp -q 90 -m 6 -metadata icc input.jpg -o output.webp`
  (`-metadata icc` preserves color profile — matters for paintings).
- Publication teaser images are manually curated per item (title
  slide, diagram, or a plain typographic card) — there's no
  automatic source the way there is for art.

## Git LFS

- `*.webp` and `*.pdf` are tracked via `.gitattributes`.
- CI checkout MUST use `actions/checkout@v4` with `lfs: true`, or
  PDFs/images silently come through as broken LFS pointer files
  instead of actual content — easy to miss since the build won't
  error, it'll just produce a broken site.

## Known open items (as of last content session)

- No Hugo layout templates exist yet at all — that's the immediate
  next step, via `/design` mode. A `hugo build` right now won't
  produce readable HTML regardless of content completeness.
- `content/resume/` doesn't exist yet — needs real biographical
  content from Sascha before it can be drafted.
- Section list pages (`content/art/_index.*.md`,
  `content/publications/_index.*.md`,
  `content/projects/_index.*.md`) don't exist yet. Optional —
  Hugo auto-generates a bare list page without them — but worth
  adding for section-level intro copy, same pattern as the tag pages.
- `content/projects/` has zero entries.
- `programming-techniques-in-cl` bundle: the Markdown body already
  links to all ~32 lecture PDFs + 6 listing files, but only 1 lecture
  PDF is actually present on disk — the rest need to be added as the
  linked filenames already specify.
- Missing German translation for `content/publications/JP6511221B2/`
  — see Bilingual section above for why this now matters
  (fully-bilingual is policy, not a nice-to-have).