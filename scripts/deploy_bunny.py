#!/usr/bin/env python3
"""Sync a built Hugo site to a Bunny.net Storage Zone over the native API.

    deploy_bunny.py <public-dir>

Environment:
    BUNNY_STORAGE_PASSWORD   (required) read-write storage password for the
                             zone -- `tofu output -json passwords` in
                             brawer/production, key "brawer-homepage".
    BUNNY_STORAGE_ZONE       zone name / bucket        (default brawer-homepage)
    BUNNY_STORAGE_ENDPOINT   native Storage API base   (default
                             https://storage.bunnycdn.com -- DE/Falkenstein,
                             Bunny's primary region; confirm against
                             `tofu output api_endpoints` in brawer/production)
    BUNNY_DEPLOY_DRY_RUN     if set to a non-empty value, log every upload and
                             delete without performing it.

Why the native API and not S3: the "brawer-homepage" zone is type "Standard",
which does not speak S3 (and converting it is destructive -- it cascade-deletes
the pull zone). See brawer/production/bunny/storage.tf.

Before the sync, the built 404.html is also mirrored to
bunnycdn_errors/404.html -- Bunny's own file-presence convention for a
zone-wide custom 404 page, needing no separate account-level API call.
See sync_error_page()'s own docstring.

Upload ORDER matters and is the whole point of this script over a naive sync:

    1. every non-HTML file (hashed CSS/JS, images, PDFs, fonts, ...)
    2. then *.html + *.xml + robots.txt
    3. then DELETE remote paths no longer present locally -- but only ones
       that have been gone from the local build for at least
       BUNNY_ORPHAN_GRACE_HOURS (see below), not immediately

A visitor who loads a page mid-deploy then always gets a consistent set --
never new HTML referencing a content-hashed asset that has not finished
uploading (which the browser would cache as a 404), and never HTML pointing at
a file already deleted. This ordering is the precondition for raising the edge
immutable TTL -- brawer/production#13 -- and for keeping the Bunny account API
key out of CI entirely (no purge step; brawer/homepage#81).

Diffing is by SHA256: Bunny returns an uppercase-hex Checksum per object, we
compare it to the local file's and only PUT on a miss or mismatch. A first
deploy (empty zone) uploads everything and deletes nothing.

Orphan grace period (brawer/homepage#121, found while verifying #39's own
fix): there is no cache purge on deploy, so for up to the HTML
Cache-Control max-age (brawer/production's bunny/cdn.tf), a visitor's
browser -- or the CDN edge itself -- can still be holding PRE-deploy HTML
that references a content-hashed CSS/JS/image whose bytes just changed
underneath it. Deleting the old hash file in the SAME deploy that orphans
it turns that into a 404 (missing CSS) until the visitor reloads. So a
remote file that has fallen out of the local build isn't deleted right
away -- it's tracked (in STATE_KEY, persisted in the zone itself, since CI
runners keep no state between invocations) and only actually removed once
it has been orphaned for BUNNY_ORPHAN_GRACE_HOURS. Losing that state file
(corrupt, briefly unreachable) fails safe: every currently tracked
orphan's clock just restarts, which only means keeping it a bit longer,
never deleting it early. This logic is covered by test_deploy_bunny.py
(an in-memory fake Bunny backend, no real network) -- run it after any
change here.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Bunny caps concurrent connections at 50; 16 keeps a full sync to a few
# seconds without crowding that.
WORKERS = 16
# Transient-failure retries (per request) with linear backoff.
RETRIES = 4
RETRY_BACKOFF_S = 2

HTML_SUFFIXES = (".html", ".xml")
HTML_EXACT = ("robots.txt",)

# Default for BUNNY_ORPHAN_GRACE_HOURS (hours an orphaned remote file is
# kept before actual deletion) -- see the "Orphan grace period" module
# docstring above for why this exists. Must stay >= the HTML Cache-Control
# max-age set in brawer/production's bunny/cdn.tf (planned: 24h) -- 72h/3
# days gives roughly 3x margin over that for clock skew, staggered per-PoP
# edge expiry, and any intermediate cache that doesn't strictly honour
# max-age. Revisit together if that max-age ever changes. Like every other
# env-driven setting here, actually read inside main(), not at import time.
DEFAULT_ORPHAN_GRACE_HOURS = 72

# Where the orphan-tracking manifest lives -- in the SAME zone, since CI
# holds no state between runs. Leading dot + nested path so it reads as
# deploy bookkeeping, not site content, in any listing; excluded from every
# local/remote diff below (never uploaded as if it were a build output,
# never treated as an orphan candidate itself). Note this doesn't make it
# secret: the linked pull zone will happily serve it over HTTP like any
# other stored object, same as everything else in the zone. That's fine --
# it holds nothing but a map of already-public asset paths to timestamps --
# and keeping this self-contained in one script/one zone was judged simpler
# than wiring up e.g. actions/cache in deploy.yml for the same purpose.
STATE_KEY = ".deploy/orphan-state.json"


def die(msg: str):
    print(f"::error::{msg}", file=sys.stderr)
    sys.exit(1)


class Bunny:
    def __init__(self, endpoint: str, zone: str, password: str, dry_run: bool):
        self.base = endpoint.rstrip("/") + "/" + zone.strip("/") + "/"
        self.headers = {"AccessKey": password}
        self.dry_run = dry_run

    def _url(self, key: str) -> str:
        # Percent-encode each path segment; keep the slashes.
        return self.base + urllib.parse.quote(key)

    def _request(self, method: str, key: str, *, data: bytes | None = None,
                 extra_headers: dict | None = None) -> bytes:
        headers = dict(self.headers)
        if extra_headers:
            headers.update(extra_headers)
        last_err: Exception | None = None
        for attempt in range(1, RETRIES + 1):
            req = urllib.request.Request(self._url(key), data=data,
                                         method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    return resp.read()
            except urllib.error.HTTPError as e:
                # 404 on a GET/DELETE is meaningful to the caller, not an error.
                if e.code == 404 and method in ("GET", "DELETE"):
                    raise
                if e.code in (401, 403):
                    die(f"Bunny rejected the credential ({e.code}) on "
                        f"{method} {key} -- check BUNNY_STORAGE_PASSWORD and "
                        f"BUNNY_STORAGE_ZONE.")
                last_err = e
                if e.code < 500 and e.code != 429:
                    break  # a non-retryable client error
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                last_err = e
            if attempt < RETRIES:
                time.sleep(RETRY_BACKOFF_S * attempt)
        die(f"{method} {key} failed after {RETRIES} attempts: {last_err}")

    def remote_index(self) -> dict[str, str]:
        """Map every stored object's key -> uppercase-hex SHA256 (recursive)."""
        index: dict[str, str] = {}
        stack = [""]
        while stack:
            prefix = stack.pop()
            try:
                raw = self._request("GET", prefix + "/" if prefix else "")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # directory does not exist yet (first deploy)
                raise
            for entry in json.loads(raw or b"[]"):
                name = entry["ObjectName"]
                key = f"{prefix}/{name}" if prefix else name
                if entry.get("IsDirectory"):
                    stack.append(key)
                else:
                    # Checksum can be null on very old objects -> force reupload.
                    index[key] = (entry.get("Checksum") or "").upper()
        return index

    def upload(self, key: str, path: str, sha_upper: str) -> None:
        if self.dry_run:
            print(f"  PUT    {key}")
            return
        with open(path, "rb") as fh:
            body = fh.read()
        self._request("PUT", key, data=body,
                      extra_headers={"Checksum": sha_upper,
                                     "Content-Type": "application/octet-stream"})
        print(f"  PUT    {key}")

    def delete(self, key: str) -> None:
        if self.dry_run:
            print(f"  DELETE {key}")
            return
        try:
            self._request("DELETE", key)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return  # already gone
            raise
        print(f"  DELETE {key}")

    def get_json(self, key: str, default):
        """GET + parse a small JSON object; 404 or anything unparseable
        returns `default` rather than raising -- see the orphan-state
        fail-safe note in the module docstring."""
        try:
            raw = self._request("GET", key)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return default
            raise
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"::warning::{key} is unreadable, ignoring it", file=sys.stderr)
            return default

    def put_json(self, key: str, data) -> None:
        if self.dry_run:
            print(f"  PUT    {key}  (deploy state, not counted above)")
            return
        body = json.dumps(data, sort_keys=True).encode("utf-8")
        self._request("PUT", key, data=body,
                      extra_headers={"Checksum": hashlib.sha256(body).hexdigest().upper(),
                                     "Content-Type": "application/json"})


def sha256_upper(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def sync_error_page(root: str) -> None:
    """Mirror the built 404 page to Bunny's custom-error-page convention:
    a storage zone serves <zone>/bunnycdn_errors/404.html (still with a
    real 404 status code) for any missing object in the whole zone, no
    pull-zone/account-level API config needed -- so this can run from
    CI with only the storage password already in scope here (see
    CLAUDE.md's "Static assets & fingerprinting" section). No official
    API for this -- it's a file-presence convention, confirmed via
    Bunny's own support docs.

    Hugo's layouts/404.html already renders to <root>/404.html (and,
    since the site is multilingual, also <root>/de/404.html -- but
    Bunny's fallback only ever serves ONE fixed file zone-wide, so only
    the root/English one is the candidate; see 404.html's own header
    comment for why its content is bilingual regardless of which of the
    two gets mirrored here). This just copies that one file to the path
    Bunny's convention expects, so it uploads through the normal walk
    in main() like any other file -- no separate upload/diff/orphan
    codepath needed, and it naturally gets re-uploaded whenever its
    content changes, same as everything else.

    Best-effort: a build without a 404.html (e.g. a unit-test fixture
    that never calls this) just skips rather than failing -- it's
    deploy.yml's own sanity gate that makes a real deploy require one,
    not this general-purpose script refusing to run without it."""
    src = os.path.join(root, "404.html")
    if not os.path.isfile(src):
        return
    dst_dir = os.path.join(root, "bunnycdn_errors")
    os.makedirs(dst_dir, exist_ok=True)
    with open(src, "rb") as fh:
        data = fh.read()
    with open(os.path.join(dst_dir, "404.html"), "wb") as fh:
        fh.write(data)


def is_html_like(key: str) -> bool:
    return key.endswith(HTML_SUFFIXES) or key.rsplit("/", 1)[-1] in HTML_EXACT


def local_index(root: str) -> dict[str, str]:
    """Map every file under root -> local key (posix, root-relative)."""
    out: dict[str, str] = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            full = os.path.join(dirpath, name)
            key = os.path.relpath(full, root).replace(os.sep, "/")
            out[key] = full
    return out


def run_phase(label: str, bunny: Bunny, jobs: list) -> None:
    if not jobs:
        print(f"{label}: nothing to do")
        return
    print(f"{label}: {len(jobs)} operation(s)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(fn, *args) for fn, *args in jobs]
        for fut in concurrent.futures.as_completed(futures):
            fut.result()  # re-raise; die() already handled the fatal cases


def main() -> None:
    if len(sys.argv) != 2:
        die("usage: deploy_bunny.py <public-dir>")
    root = sys.argv[1]
    if not os.path.isfile(os.path.join(root, "index.html")):
        die(f"{root}/index.html missing -- refusing to deploy a non-build")
    sync_error_page(root)

    password = os.environ.get("BUNNY_STORAGE_PASSWORD")
    if not password:
        die("BUNNY_STORAGE_PASSWORD is not set")
    endpoint = os.environ.get("BUNNY_STORAGE_ENDPOINT", "https://storage.bunnycdn.com")
    zone = os.environ.get("BUNNY_STORAGE_ZONE", "brawer-homepage")
    dry_run = bool(os.environ.get("BUNNY_DEPLOY_DRY_RUN"))
    grace_hours = float(os.environ.get("BUNNY_ORPHAN_GRACE_HOURS",
                                       DEFAULT_ORPHAN_GRACE_HOURS))

    bunny = Bunny(endpoint, zone, password, dry_run)
    print(f"Deploying {root}/ -> {zone} at {endpoint}"
          + ("  [DRY RUN]" if dry_run else ""))

    local = local_index(root)
    remote = bunny.remote_index()
    remote.pop(STATE_KEY, None)  # deploy bookkeeping, not a site file
    print(f"{len(local)} local file(s), {len(remote)} already in the zone")

    assets, pages = [], []
    for key, path in sorted(local.items()):
        sha = sha256_upper(path)
        if remote.get(key) == sha:
            continue
        (pages if is_html_like(key) else assets).append((bunny.upload, key, path, sha))

    # Orphan grace period -- see the module docstring's "Orphan grace
    # period" section. A remote file no longer in the local build isn't
    # deleted the moment it's noticed; it's timestamped in orphan_state
    # (first sighting = now, for one not already tracked) and only queued
    # for deletion once it's been orphaned for ORPHAN_GRACE_HOURS. Anything
    # that reappears locally (e.g. a revert) just isn't a candidate this
    # run, so it naturally drops out of the carried-forward state below.
    now = time.time()
    orphan_state = bunny.get_json(STATE_KEY, {})
    orphaned = sorted(key for key in remote if key not in local)
    deletions, kept = [], {}
    for key in orphaned:
        first_seen = orphan_state.get(key, now)
        age_hours = (now - first_seen) / 3600
        if age_hours >= grace_hours:
            deletions.append((bunny.delete, key))
        else:
            kept[key] = first_seen

    run_phase("Phase 1 (assets)", bunny, assets)
    run_phase("Phase 2 (HTML + feeds)", bunny, pages)
    run_phase(f"Phase 3 (delete orphaned >{grace_hours:.0f}h)", bunny, deletions)
    bunny.put_json(STATE_KEY, kept)

    if kept:
        print(f"Orphaned, within the {grace_hours:.0f}h grace period, kept:")
        for key, first_seen in sorted(kept.items()):
            print(f"  {key}  (orphaned {(now - first_seen) / 3600:.1f}h ago)")

    changed = len(assets) + len(pages)
    print(f"Done: {changed} uploaded, {len(deletions)} deleted, "
          f"{len(kept)} orphaned-but-kept, {len(local) - changed} unchanged.")


if __name__ == "__main__":
    main()
