#!/usr/bin/env python3
"""Check a built site against its own Content-Security-Policy.

Usage: check_csp.py [public-dir]

head.html puts a Content-Security-Policy in a <meta> tag and allows the
one inline <script> by the hash of its bytes (issue #106). If the two
ever disagree, browsers silently refuse to run the script -- the
remembered-language redirect just stops working, with nothing but a
console message. This reads every built HTML page and fails if:

  - a page runs scripts but has no policy,
  - an inline script's sha256 is not in the page's script-src, or sits
    above the policy (a meta policy only governs what follows it),
  - a script is loaded from another origin,
  - an element has an inline event handler (onclick= etc.), which a
    policy without 'unsafe-inline' blocks.

Run it on the tree that ships (`hugo --minify`): minifying rewrites
inline scripts, and the hash has to match those bytes. Standard library
only. JSON blocks and other non-JavaScript <script> types are data, not
code, and are skipped, as a browser skips them.
"""

import base64
import hashlib
import pathlib
import sys
from html.parser import HTMLParser

JS_TYPES = {"", "module", "text/javascript", "application/javascript"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.policy = None
        self.problems = []
        self.scripts = 0
        self._inline = None  # text of the inline script being read

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        for name in a:
            if name.startswith("on"):
                self.problems.append(f"inline event handler {name}= on <{tag}>")
        if tag == "meta" and a.get("http-equiv", "").lower() == "content-security-policy":
            if self.policy is None:
                self.policy = a.get("content", "")
        elif tag == "script" and a.get("type", "").lower() in JS_TYPES:
            self.scripts += 1
            src = a.get("src")
            if src is None:
                self._inline = []
            elif src.startswith("//") or "://" in src:
                self.problems.append(f"script from another origin: {src}")
            if self.policy is None:
                self.problems.append("script above (or without) the policy")

    def handle_data(self, data):
        if self._inline is not None:
            self._inline.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._inline is not None:
            text = "".join(self._inline)
            self._inline = None
            digest = base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()
            if self.policy is not None and f"'sha256-{digest}'" not in script_src(self.policy):
                self.problems.append(f"inline script not allowed by script-src: sha256-{digest}")


def script_src(policy):
    for directive in policy.split(";"):
        words = directive.split()
        if words and words[0].lower() == "script-src":
            return words[1:]
    return []


def check(root):
    failures = 0
    with_policy = 0
    pages = sorted(root.rglob("*.html"))
    for path in pages:
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        with_policy += page.policy is not None
        for problem in page.problems:
            failures += 1
            print(f"{path}: {problem}")
    print(f"{len(pages)} page(s), {with_policy} with a policy, {failures} problem(s)")
    if not pages:
        print(f"no HTML under {root} -- build the site first")
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(check(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "public")))
