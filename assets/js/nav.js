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

  // Fullscreen art viewer -- reflects open/closed state as ?view=full
  // in the address bar (issue #104). wireDialog above already makes
  // the right clicks open/close the dialog; everything here just layers
  // URL/history syncing on top of that, the same layering pattern the
  // drawer above uses for its own body-class side effect (a second
  // [data-*-open] click listener, plus the dialog's own 'close' event
  // for every dismissal method at once).
  //
  // Three ways the viewer ends up open, each needing different history
  // handling:
  //   1. Clicking the zoom button: no navigation happens, so this
  //      pushes the ?view=full URL itself, tagging the new entry with
  //      state.viewerOpen=true. That tag is what makes closing call
  //      history.back() instead of just editing the URL -- Back then
  //      always lands on the exact pre-open state, even through a real
  //      reload/bfcache restore of this same document (the History API
  //      restores history.state from the target entry regardless of
  //      how the navigation happened).
  //   2. A real page load that already carries ?view=full -- a shared/
  //      pasted link, or a Prev/Next hop *within* the viewer (still a
  //      normal <a href> full navigation on purpose -- see
  //      art/single.html's own comment for why that's not an in-dialog
  //      image swap). history.state is null here (nothing pushed it),
  //      so closing just cleans the URL in place via replaceState --
  //      there's no "opened from" entry to jump back to, and jumping to
  //      whatever IS one entry back (the referrer, or the previous
  //      piece in a hop chain) would leave the current piece's page
  //      entirely, which closing shouldn't do.
  //   3. Back/Forward landing on a ?view=full (or plain) entry: a
  //      popstate listener opens/closes the dialog to match, without
  //      touching history itself (the browser already moved it).
  //
  // No guard flag is needed to stop the popstate case from re-triggering
  // the 'close' handler's own history call: by the time 'close' fires
  // from a popstate-driven .close(), the URL has already moved off
  // ?view=full (browsers update the URL before dispatching popstate),
  // so that handler's own `?view=full` check is simply false.
  wireDialog("viewer", "[data-viewer-open]", "[data-viewer-close]");
  var viewer = document.getElementById("viewer");
  if (viewer) {
    if (new URLSearchParams(location.search).get("view") === "full") {
      viewer.showModal();
    }

    document.querySelectorAll("[data-viewer-open]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var url = new URL(location.href);
        url.searchParams.set("view", "full");
        history.pushState({ viewerOpen: true }, "", url.toString());
      });
    });

    viewer.addEventListener("close", function () {
      if (new URLSearchParams(location.search).get("view") !== "full") return;
      if (history.state && history.state.viewerOpen) {
        history.back();
      } else {
        history.replaceState(null, "", location.pathname + location.hash);
      }
    });

    window.addEventListener("popstate", function () {
      var isFull = new URLSearchParams(location.search).get("view") === "full";
      if (isFull && !viewer.open) viewer.showModal();
      else if (!isFull && viewer.open) viewer.close();
    });
  }

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
