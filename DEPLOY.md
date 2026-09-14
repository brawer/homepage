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
the Bunny edge for up to its TTL (~5 min for HTML/feeds; the immutable-asset
TTL for hashed files, but those never change in place). To force it live now,
purge from a trusted machine that has the Bunny **account API key** — never
CI, which deliberately cannot purge:

```sh
KEY="$(cat ~/src/production/secrets/bunny_api_key)"

# One URL (preferred — targeted, fast):
curl -X POST -H "AccessKey: $KEY" \
  "https://api.bunny.net/purge?url=https%3A%2F%2Fdandelis.ch%2Fsome%2Fpage%2F&async=false"

# Whole pull zone (after a large change):
curl -X POST -H "AccessKey: $KEY" \
  "https://api.bunny.net/pullzone/<PULLZONE_ID>/purgeCache"
```

Pull-zone id: in `brawer/production`,
`cd bunny && tofu output -json pullzone_ids` (key `dandelis.ch` today; the
`brawer.ch` zone after the cutover, brawer/production#6).

The **brawer-homepage** zone currently backs **both** `dandelis.ch` (staging)
and, after cutover, `brawer.ch` — a deploy or purge affects whichever
hostnames front the zone.

## Edge cache TTLs

Not set here — Bunny storage origins drop `Cache-Control`, so caching is
pull-zone Edge Rules in `brawer/production` (`bunny/cdn.tf`). Short default for
HTML/feeds, longer for the content-hashed globs above. Raising the immutable
TTL is tracked in brawer/production#13.
