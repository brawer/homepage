#!/usr/bin/env python3
"""Tests deploy_bunny.py's orphan-grace-period logic (brawer/homepage#121)
against an in-memory fake Bunny backend -- no real network, no real
credentials needed. Drives main() through several simulated deploy runs
with a controllable clock.

This exists because the property that actually matters here -- an
orphaned file's first-seen timestamp must be PRESERVED across separate
deploy runs, not reset each time -- has no other feedback loop: a
regression would be silent until someone hit the exact "pages broken
until reload" symptom that #121 was filed for in the first place, and
deploy_bunny.py runs on every push to main.

    python3 scripts/test_deploy_bunny.py
    python3 -m unittest scripts.test_deploy_bunny   (from the repo root)
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

_spec = importlib.util.spec_from_file_location(
    "deploy_bunny", os.path.join(os.path.dirname(__file__), "deploy_bunny.py"))
deploy_bunny = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(deploy_bunny)

T0 = 1_700_000_000.0  # arbitrary fixed epoch, so test output is deterministic


class FakeBackend:
    """In-memory stand-in for the Bunny Storage HTTP API, keyed exactly
    like the real one: object key -> (bytes, sha256-upper checksum)."""

    def __init__(self):
        self.store: dict[str, tuple[bytes, str]] = {}

    def list_dir(self, prefix: str):
        # Mimic Bunny's listing: direct children of `prefix` only, with
        # sub-prefixes reported as IsDirectory so remote_index() recurses
        # (needed for STATE_KEY, which lives under a ".deploy/" prefix).
        seen_dirs = set()
        entries = []
        pfx = (prefix + "/") if prefix else ""
        for key in self.store:
            if not key.startswith(pfx):
                continue
            rest = key[len(pfx):]
            if "/" in rest:
                d = rest.split("/", 1)[0]
                if d not in seen_dirs:
                    seen_dirs.add(d)
                    entries.append({"ObjectName": d, "IsDirectory": True})
            else:
                _, sha = self.store[key]
                entries.append({"ObjectName": rest, "IsDirectory": False,
                                 "Checksum": sha})
        return entries


def fake_request_for(backend: FakeBackend):
    import hashlib
    import io
    import urllib.error

    def not_found(key: str) -> urllib.error.HTTPError:
        # A real fp (not None) avoids a ResourceWarning when this gets
        # garbage-collected -- purely cosmetic, but keeps test output clean.
        return urllib.error.HTTPError(key, 404, "Not Found", {}, io.BytesIO())

    def fake_request(self, method, key, *, data=None, extra_headers=None):
        if method == "GET" and (key == "" or key.endswith("/")):
            return json.dumps(backend.list_dir(key.rstrip("/"))).encode()
        if method == "GET":
            if key not in backend.store:
                raise not_found(key)
            return backend.store[key][0]
        if method == "PUT":
            sha = (extra_headers or {}).get("Checksum") \
                or hashlib.sha256(data).hexdigest().upper()
            backend.store[key] = (data, sha)
            return b""
        if method == "DELETE":
            if key not in backend.store:
                raise not_found(key)
            del backend.store[key]
            return b""
        raise AssertionError(f"unexpected {method} {key}")

    return fake_request


class OrphanGraceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.public = os.path.join(self.tmp, "public")
        os.makedirs(self.public)
        self.backend = FakeBackend()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))

    def write(self, name: str, content: str):
        path = os.path.join(self.public, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)

    def remove(self, name: str):
        os.remove(os.path.join(self.public, name))

    def deploy(self, now: float, *, grace_hours: str = "72", dry_run: bool = False):
        env = {"BUNNY_STORAGE_PASSWORD": "x", "BUNNY_ORPHAN_GRACE_HOURS": grace_hours}
        if dry_run:
            env["BUNNY_DEPLOY_DRY_RUN"] = "1"
        with mock.patch.object(sys, "argv", ["deploy_bunny.py", self.public]), \
             mock.patch.dict(os.environ, env, clear=False), \
             mock.patch.object(deploy_bunny.Bunny, "_request", fake_request_for(self.backend)), \
             mock.patch.object(deploy_bunny.time, "time", lambda: now):
            deploy_bunny.main()

    def state(self) -> dict:
        raw = self.backend.store.get(deploy_bunny.STATE_KEY)
        return json.loads(raw[0]) if raw else {}

    # -- Tests -----------------------------------------------------------

    def test_first_deploy_uploads_everything_and_deletes_nothing(self):
        self.write("index.html", "<html>v1</html>")
        self.write("css/main.min.HASHAAA.css", "body{color:red}")
        self.deploy(T0)

        self.assertIn("index.html", self.backend.store)
        self.assertIn("css/main.min.HASHAAA.css", self.backend.store)
        self.assertEqual(self.state(), {})

    def test_orphaned_file_is_kept_not_deleted_within_grace(self):
        self.write("index.html", "x")
        self.write("css/main.min.HASHAAA.css", "red")
        self.deploy(T0)

        # Content changes -> new hash filename, matching how Hugo's
        # `fingerprint` actually behaves. Reusing the same filename here
        # would just be a same-key overwrite, never an orphan.
        self.remove("css/main.min.HASHAAA.css")
        self.write("css/main.min.HASHBBB.css", "blue")
        self.deploy(T0 + 3600)

        self.assertIn("css/main.min.HASHBBB.css", self.backend.store)
        self.assertIn("css/main.min.HASHAAA.css", self.backend.store,
                       "orphaned file was deleted immediately instead of "
                       "waiting out the grace period")
        self.assertEqual(self.state().get("css/main.min.HASHAAA.css"), T0 + 3600)

    def test_orphan_timestamp_is_preserved_across_runs(self):
        """The property that actually makes this fix correct: a file's
        orphan clock must NOT reset just because another deploy ran."""
        self.write("index.html", "x")
        self.write("css/main.min.HASHAAA.css", "red")
        self.deploy(T0)

        self.remove("css/main.min.HASHAAA.css")
        self.write("css/main.min.HASHBBB.css", "blue")
        first_orphaned_at = T0 + 3600
        self.deploy(first_orphaned_at)

        # Two more deploys, well within the 72h default grace period,
        # with nothing about the orphaned file changing.
        self.deploy(first_orphaned_at + 5 * 3600)
        self.deploy(first_orphaned_at + 10 * 3600)

        self.assertIn("css/main.min.HASHAAA.css", self.backend.store)
        self.assertEqual(
            self.state().get("css/main.min.HASHAAA.css"), first_orphaned_at,
            "orphan timestamp drifted -- it must stay pinned to when the "
            "file FIRST went orphaned, not the most recent deploy")

    def test_orphan_deleted_and_state_cleaned_up_after_grace_period(self):
        self.write("index.html", "x")
        self.write("css/main.min.HASHAAA.css", "red")
        self.deploy(T0)

        self.remove("css/main.min.HASHAAA.css")
        self.write("css/main.min.HASHBBB.css", "blue")
        orphaned_at = T0 + 3600
        self.deploy(orphaned_at)

        self.deploy(orphaned_at + 73 * 3600)  # past the 72h default

        self.assertNotIn("css/main.min.HASHAAA.css", self.backend.store)
        self.assertNotIn("css/main.min.HASHAAA.css", self.state())
        # Nothing else got caught in the blast radius.
        self.assertIn("css/main.min.HASHBBB.css", self.backend.store)
        self.assertIn("index.html", self.backend.store)

    def test_grace_period_env_override_is_honoured(self):
        self.write("index.html", "x")
        self.write("css/main.min.HASHAAA.css", "red")
        self.deploy(T0, grace_hours="1")

        self.remove("css/main.min.HASHAAA.css")
        self.write("css/main.min.HASHBBB.css", "blue")
        self.deploy(T0 + 3600, grace_hours="1")
        self.assertIn("css/main.min.HASHAAA.css", self.backend.store,
                       "deleted before even the 1h override grace elapsed")

        self.deploy(T0 + 3 * 3600, grace_hours="1")  # 2h later, past the 1h grace
        self.assertNotIn("css/main.min.HASHAAA.css", self.backend.store)

    def test_dry_run_never_mutates_the_backend(self):
        self.write("index.html", "x")
        self.write("a.css", "a")
        self.deploy(T0)
        self.remove("a.css")
        self.write("b.css", "b")

        before = dict(self.backend.store)
        self.deploy(T0 + 3600, dry_run=True)
        self.assertEqual(self.backend.store, before)

    def test_corrupted_state_file_fails_safe(self):
        self.write("index.html", "x")
        self.write("a.css", "a")
        self.deploy(T0)
        self.remove("a.css")
        self.write("b.css", "b")
        self.deploy(T0 + 10)  # a.css now orphaned, tracked

        self.backend.store[deploy_bunny.STATE_KEY] = (b"{not valid json", "DEADBEEF")

        self.deploy(T0 + 20)  # must not raise

        self.assertIn("a.css", self.backend.store,
                       "a corrupted state file should fail safe (treat as "
                       "empty / restart the clock), not crash or over-delete")

    def test_state_manifest_never_treated_as_a_site_file(self):
        self.write("index.html", "x")
        self.deploy(T0)
        self.deploy(T0 + 1)  # a second run must not try to "orphan" its own state file
        self.assertIn(deploy_bunny.STATE_KEY, self.backend.store)

    # -- Custom 404 error page (bunnycdn_errors/ convention) --------------

    def test_404_is_mirrored_to_bunnycdn_errors_convention(self):
        self.write("index.html", "x")
        self.write("404.html", "<html>not found</html>")
        self.deploy(T0)

        self.assertIn("bunnycdn_errors/404.html", self.backend.store)
        self.assertEqual(self.backend.store["bunnycdn_errors/404.html"][0],
                          b"<html>not found</html>")

    def test_404_mirror_updates_when_the_source_changes(self):
        self.write("index.html", "x")
        self.write("404.html", "<html>v1</html>")
        self.deploy(T0)
        self.assertEqual(self.backend.store["bunnycdn_errors/404.html"][0],
                          b"<html>v1</html>")

        self.write("404.html", "<html>v2</html>")
        self.deploy(T0 + 3600)
        self.assertEqual(self.backend.store["bunnycdn_errors/404.html"][0],
                          b"<html>v2</html>")

    def test_missing_404_is_skipped_not_fatal(self):
        """sync_error_page() is best-effort (see its own docstring) --
        deploy.yml's sanity gate is what makes a real deploy require a
        404.html, not this general-purpose script. Every other test in
        this file relies on this too (none of them write a 404.html)."""
        self.write("index.html", "x")
        self.deploy(T0)  # must not raise
        self.assertNotIn("bunnycdn_errors/404.html", self.backend.store)


if __name__ == "__main__":
    # buffer=True: deploy_bunny.main() prints a full trace of every
    # upload/delete/kept-orphan per run, which is useful on a FAILURE but
    # just noise across 8 passing tests x several simulated deploys each --
    # unittest's own buffering captures stdout per test and only shows it
    # for tests that actually fail.
    unittest.main(buffer=True)
