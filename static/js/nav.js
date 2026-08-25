// Navigation drawer, tag-page back button, and art fullscreen viewer.
// NAVIGATION_DESIGN_SPEC.md. First JS in this repo — deliberately
// plain, no build step, progressively enhances markup that already
// works (as a link/fallback) without it.

(function () {
  "use strict";

  function wireDialog(dialogId, openSelector, closeSelector) {
    var dialog = document.getElementById(dialogId);
    if (!dialog) return;
    document.querySelectorAll(openSelector).forEach(function (btn) {
      btn.addEventListener("click", function () {
        dialog.showModal();
      });
    });
    dialog.querySelectorAll(closeSelector).forEach(function (btn) {
      btn.addEventListener("click", function () {
        dialog.close();
      });
    });
    // Clicking the ::backdrop fires 'click' with the dialog itself as
    // the target (no descendant was hit) — close on that, not on any
    // click bubbling up from real dialog content.
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) dialog.close();
    });
  }

  // Drawer: prevent background scroll while open (native showModal()
  // already makes the background inert/unreachable — this only stops
  // it from visually scrolling behind the drawer).
  var drawer = document.getElementById("nav-drawer");
  if (drawer) {
    wireDialog("nav-drawer", "[data-drawer-open]", "[data-drawer-close]");
    drawer.addEventListener("close", function () {
      document.body.classList.remove("drawer-open");
    });
    document.querySelectorAll("[data-drawer-open]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.body.classList.add("drawer-open");
      });
    });
  }

  // Fullscreen art viewer.
  wireDialog("viewer", "[data-viewer-open]", "[data-viewer-close]");

  // Tag-page back arrow: return to wherever the visitor actually
  // pivoted from (a tag can be reached from many different parent
  // pages), at the same scroll position. The href="/" on the same
  // element is the no-JS/no-history fallback.
  document.querySelectorAll("[data-history-back]").forEach(function (link) {
    link.addEventListener("click", function (e) {
      if (window.history.length > 1) {
        e.preventDefault();
        window.history.back();
      }
    });
  });

  // Auto-reopen the fullscreen viewer after a Prev/Next navigation
  // inside it (a real page load, not an in-dialog image swap — see
  // NAVIGATION_DESIGN_SPEC.md plan §6 for why). Strip the marker from
  // the URL afterwards so browser Back doesn't reopen it a second time.
  if (new URLSearchParams(location.search).get("view") === "full") {
    var viewer = document.getElementById("viewer");
    if (viewer) viewer.showModal();
    history.replaceState(null, "", location.pathname + location.hash);
  }
})();
