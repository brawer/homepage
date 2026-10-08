// Remembered language choice -- inlined into <head> by head.html, which
// explains why it is inline and render-blocking.
//
// This text must be IDENTICAL on every page: the Content-Security-Policy
// in head.html allows it by the hash of its bytes. So nothing per-page
// may be written into it; the page's own language comes from <html lang>
// and its translations' URLs from the #lang-urls JSON block that
// head.html emits just above (data, not script -- a CSP ignores it).
//
// ONE local variable, reused, on purpose. head.html minifies this file
// and hashes the result; `hugo --minify` then minifies the page, inline
// script included, a second time. With two variables that second pass
// swapped their short names and the hash no longer matched. Keep the
// minified form stable under re-minifying -- scripts/check_csp.py
// (CI + deploy) fails if it is not.
(function () {
  try {
    var v = localStorage.getItem("preferred-lang");
    if (!v || v === document.documentElement.lang) return;
    v = JSON.parse(document.getElementById("lang-urls").textContent)[v];
    if (v) location.replace(v);
  } catch (e) {}
})();
