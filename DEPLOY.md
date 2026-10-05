# Deploying brawer.ch

## Automatic (the normal path)

Every push to `main` that passes the content checks runs
`.github/workflows/deploy.yml`: `hugo --gc --minify`, then
`scripts/deploy_bunny.py` syncs `public/` to the Bunny **brawer-homepage**
storage zone (native Storage API, SHA256 diff, upload order
assets → HTML/feeds → delete-orphaned-past-grace-period). No cache purge.

A remote file that drops out of the local build (most often: a CSS/JS/image
whose content-hash filename just changed underneath it) isn't deleted the
moment it's noticed — it's kept for `BUNNY_ORPHAN_GRACE_HOURS` (default 72h)
after first going orphaned, tracked in `.deploy/orphan-state.json` inside the
same zone. This exists because there's no cache purge here: a visitor's
browser, or the CDN edge itself, can still be holding pre-deploy HTML that
references the old filename for up to the HTML edge TTL below — deleting
instantly would 404 that visitor's CSS until they reload. See
`scripts/deploy_bunny.py`'s module docstring for the full reasoning.

New pages and content-hashed assets (`/css/main.min.<hash>.css`,
`/js/nav.min.<hash>.js`, `…_hu_<hash>.webp/.avif`, `/fonts/*`) are visible
immediately — their URLs are new, so nothing is cached under them yet.

A manual run: **Actions → Deploy → Run workflow** (must be on `main` — the
`production` environment's branch rule blocks the storage secret otherwise).

## Manual instant propagation (rare)

A **changed** stable-URL file — an edit to an existing page, a replaced PDF,
`robots.txt`, the RSS/sitemap, the `noindex` flip at launch — stays cached at
the Bunny edge for up to its TTL (5 min for HTML/feeds; 30 days for hashed
files, but those never change in place). To force it live now,
purge from a trusted machine that has the Bunny **account API key** — never
CI, which deliberately cannot purge:

```sh
KEY="$(cat ~/src/production/secrets/bunny_api_key)"

# One URL (preferred — targeted, fast):
curl -X POST -H "AccessKey: $KEY" \
  "https://api.bunny.net/purge?url=https%3A%2F%2Fbrawer.ch%2Fsome%2Fpage%2F&async=false"

# Whole pull zone (after a large change):
curl -X POST -H "AccessKey: $KEY" \
  "https://api.bunny.net/pullzone/<PULLZONE_ID>/purgeCache"
```

Pull-zone id: in `brawer/production`,
`cd bunny && tofu output -json pullzone_ids` (key `brawer.ch` since the
2026-09-14 cutover, brawer/production#6; `dandelis.ch` before that).

The **brawer-homepage** zone backs `brawer.ch` (live since 2026-09-14) and
nothing else: `dandelis.ch`, the old staging domain, is decommissioned and no
longer fronts the zone.

## Edge cache TTLs

Not set here — Bunny storage origins drop `Cache-Control`, so caching is
pull-zone Edge Rules in `brawer/production` (`bunny/cdn.tf`):

- **HTML/feeds and everything else: 300 s.** Not planned to rise
  (brawer/production#19). The pull zone does not serve an expired copy while
  revalidating (brawer/production#49), so 300 s is a real upper bound on how
  old a served page can be — the orphan grace period above relies on that.
- **Content-hashed assets and `/fonts/*`: 30 days**, at the edge and in
  browsers (`immutable_max_age = 2592000`, brawer/production#45).

Two consequences of the 30 days:

- **Fonts have a stable URL** (`/fonts/karla-latin-variable.woff2`). A changed
  font file needs a **new filename in the same commit**. A purge clears the
  edge but not the copies already in visitors' browsers.
- **A 404 is cached too.** A hashed asset requested before it has been
  uploaded would stay missing at the edge for 30 days. The assets-before-HTML
  upload order in `scripts/deploy_bunny.py` prevents that; don't reorder it.
