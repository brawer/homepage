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

Upload ORDER matters and is the whole point of this script over a naive sync:

    1. every non-HTML file (hashed CSS/JS, images, PDFs, fonts, ...)
    2. then *.html + *.xml + robots.txt
    3. then DELETE remote paths no longer present locally

A visitor who loads a page mid-deploy then always gets a consistent set --
never new HTML referencing a content-hashed asset that has not finished
uploading (which the browser would cache as a 404), and never HTML pointing at
a file already deleted. This ordering is the precondition for raising the edge
immutable TTL -- brawer/production#13 -- and for keeping the Bunny account API
key out of CI entirely (no purge step; brawer/homepage#81).

Diffing is by SHA256: Bunny returns an uppercase-hex Checksum per object, we
compare it to the local file's and only PUT on a miss or mismatch. A first
deploy (empty zone) uploads everything and deletes nothing.
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


def sha256_upper(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


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

    password = os.environ.get("BUNNY_STORAGE_PASSWORD")
    if not password:
        die("BUNNY_STORAGE_PASSWORD is not set")
    endpoint = os.environ.get("BUNNY_STORAGE_ENDPOINT", "https://storage.bunnycdn.com")
    zone = os.environ.get("BUNNY_STORAGE_ZONE", "brawer-homepage")
    dry_run = bool(os.environ.get("BUNNY_DEPLOY_DRY_RUN"))

    bunny = Bunny(endpoint, zone, password, dry_run)
    print(f"Deploying {root}/ -> {zone} at {endpoint}"
          + ("  [DRY RUN]" if dry_run else ""))

    local = local_index(root)
    remote = bunny.remote_index()
    print(f"{len(local)} local file(s), {len(remote)} already in the zone")

    assets, pages = [], []
    for key, path in sorted(local.items()):
        sha = sha256_upper(path)
        if remote.get(key) == sha:
            continue
        (pages if is_html_like(key) else assets).append((bunny.upload, key, path, sha))

    deletions = [(bunny.delete, key) for key in sorted(remote) if key not in local]

    run_phase("Phase 1 (assets)", bunny, assets)
    run_phase("Phase 2 (HTML + feeds)", bunny, pages)
    run_phase("Phase 3 (delete removed)", bunny, deletions)

    changed = len(assets) + len(pages)
    print(f"Done: {changed} uploaded, {len(deletions)} deleted, "
          f"{len(local) - changed} unchanged.")


if __name__ == "__main__":
    main()
