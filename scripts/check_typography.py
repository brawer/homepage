#!/usr/bin/env python3
"""Enforce CLAUDE.md's typography policy across all content.

Checks both front matter (recursively, so nested fields like
resume's experience[].highlights[] are covered) and the Markdown
body, for every language:

  EN: no straight quotes/apostrophes anywhere -- policy is always
      "curly double"/'curly single' -- Goldmark's typographer
      extension is deliberately disabled (hugo.toml) so this can't
      be silently auto-fixed and hidden; it must be correct at the
      source.
  DE: no em dash (--), no German-German low-high quotes (../..), no
      straight quotes/apostrophes anywhere -- policy is en dash (-)
      and .guillemets./.single guillemets. (de-CH).

Exits non-zero (with every violation printed) if anything is found.
"""
import glob
import re
import sys

import yaml

EM_DASH = "—"
LOW9_DOUBLE = "„"
LOW9_SINGLE = "‚"

violations = []


def scan_string(lang, path, field, val):
    if lang == "de":
        if EM_DASH in val:
            violations.append(f"{path} [{field}]: em dash (—) -- use en dash (–)")
        if LOW9_DOUBLE in val or LOW9_SINGLE in val:
            violations.append(f"{path} [{field}]: German-German low-high quote -- use «guillemets»")
        if '"' in val:
            violations.append(f"{path} [{field}]: straight double quote -- use «guillemets»")
        if "'" in val:
            violations.append(f"{path} [{field}]: straight single quote -- use ‹single guillemets›")
    else:
        if '"' in val:
            violations.append(f'{path} [{field}]: straight double quote -- use “curly” quotes')
        if "'" in val:
            violations.append(f"{path} [{field}]: straight apostrophe/quote -- use ’curly’")


def scan_value(lang, path, field, val):
    if isinstance(val, str):
        scan_string(lang, path, field, val)
    elif isinstance(val, list):
        for i, v in enumerate(val):
            scan_value(lang, path, f"{field}[{i}]", v)
    elif isinstance(val, dict):
        for k, v in val.items():
            scan_value(lang, path, f"{field}.{k}", v)


for lang, pattern in [("en", "content/**/*.en.md"), ("de", "content/**/*.de.md")]:
    for f in sorted(glob.glob(pattern, recursive=True)):
        with open(f, encoding="utf-8") as fh:
            text = fh.read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
        if not m:
            violations.append(f"{f}: could not parse front matter delimiters")
            continue
        fm_text, body = m.groups()
        fm = yaml.safe_load(fm_text) or {}
        for k, v in fm.items():
            scan_value(lang, f, k, v)
        scan_string(lang, f, "body", body)

if violations:
    for v in violations:
        print(f"::error::{v}")
    print(f"\n{len(violations)} typography violation(s) found.", file=sys.stderr)
    sys.exit(1)
print("No typography violations found.")
