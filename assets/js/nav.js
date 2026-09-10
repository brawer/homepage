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

  // Language switcher: record an explicit choice so later visits can
  // honour it. The redirect itself is done by the inline <head> script
  // (see head.html) — it has to run before paint. This only writes the
  // preference, which can happen late: the click also navigates via the
  // link's href, and the next page reads the freshly-written value.
  // Never inferred from navigator.language, only what was actually
  // clicked. A failed write (private mode) just means "not remembered".
  document.querySelectorAll("[data-lang-choice]").forEach(function (link) {
    link.addEventListener("click", function () {
      try {
        localStorage.setItem(
          "preferred-lang",
          link.getAttribute("data-lang-choice")
        );
      } catch (e) {}
    });
  });

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

  // Detail pages: ← / → step to the previous / next item in the
  // section, mirroring the circular buttons on the hero (hero-nav.html)
  // and the fullscreen viewer's own chevrons. A desktop affordance (the
  // hint under the hero is desktop-only via CSS), but the keys work at
  // any width. When the art viewer is open, drive ITS prev/next
  // instead. Ignored while typing in a field or when a modifier is
  // held, and never overrides a link/button that already handled the
  // key.
  var heroPrev = document.querySelector("a.hero-nav-prev");
  var heroNext = document.querySelector("a.hero-nav-next");
  if (heroPrev || heroNext) {
    document.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
      if (document.body.classList.contains("drawer-open")) return;
      var t = e.target;
      if (t && (t.isContentEditable ||
          /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
      var openViewer = document.getElementById("viewer");
      var inViewer = openViewer && openViewer.open;
      var prev = inViewer ? openViewer.querySelector(".viewer-prev") : heroPrev;
      var next = inViewer ? openViewer.querySelector(".viewer-next") : heroNext;
      var target = e.key === "ArrowLeft" ? prev : next;
      if (target && target.href) location.href = target.href;
    });
  }

  // Résumé: the header is position:sticky there (the one page long
  // enough for a pinned header to matter — see CLAUDE.md). Cast a shadow
  // under it only once the page has scrolled: a shadow implies floating
  // above moving content, which is only true after it detaches from the
  // top. CSS does the rest (.resume-page.is-scrolled header).
  if (document.body.classList.contains("resume-page")) {
    var setStuck = function () {
      document.body.classList.toggle("is-scrolled", window.scrollY > 4);
    };
    setStuck();
    window.addEventListener("scroll", setStuck, { passive: true });
  }
})();
