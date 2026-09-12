// @ts-check
const { defineConfig, devices } = require("@playwright/test");

// Tests for assets/js/nav.js's interactive behavior (mobile drawer,
// fullscreen art viewer, safe-area padding) — see CLAUDE.md's
// "Browser/interaction tests" section. `webServer` below starts a real
// `hugo server` and waits for it to answer before any test runs (and
// tears it down after), so `npx playwright test` is the only command
// needed locally — no separate server to remember to start.
module.exports = defineConfig({
  // A bit above the 5s default, same reasoning as the capped `workers`
  // below: gives auto-retrying `expect()`s more headroom to catch a
  // same-document popstate-driven DOM change under CPU contention.
  expect: { timeout: 8_000 },
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  // Capped in CI, not left to auto-detect: found real flakiness under
  // full parallelism in a resource-constrained sandbox specifically on
  // the assertion that a same-document popstate-driven dialog re-open
  // actually completed (the URL updates immediately; the JS event
  // listener that reopens the dialog can lag behind it under CPU
  // contention) -- a real timing race exposed by parallel load, not a
  // bug in the reopen logic itself (reproduced reliably passing at
  // --workers=1, and manually confirmed the dialog does reopen, just
  // ~300ms after Playwright's goForward() promise resolves). A GitHub
  // Actions runner isn't guaranteed to be less contended than that.
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "retain-on-failure",
    // The drawer/viewer open-close animation (main.css) already fully
    // honors prefers-reduced-motion (drops every transition, instant
    // open/close) -- using it here means tests never need an arbitrary
    // sleep to wait out a slide/fade before checking DOM state or
    // computed layout.
    reducedMotion: "reduce",
  },
  projects: [
    // Chromium only, deliberately -- this suite exists to verify
    // nav.js's OWN logic (history/URL state, click hit-testing math)
    // and a couple of Chromium-only CDP hooks used to emulate a real
    // notched phone (Emulation.setSafeAreaInsetsOverride, see
    // safe-area.spec.js) that have no Firefox/WebKit equivalent in
    // Playwright. Real cross-browser rendering QA is still the
    // deferred manual pass CLAUDE.md already tracks separately.
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: {
    command:
      "hugo server -D --port 4173 --bind 127.0.0.1 --disableFastRender",
    url: "http://127.0.0.1:4173/",
    reuseExistingServer: !process.env.CI,
    // Generous: a cold `hugo server` build of this site processes 700+
    // images (art/publication teasers x every responsive size) and
    // measured ~50s on its own in this environment before the server
    // even starts accepting connections -- 60s cut it too close.
    timeout: 180_000,
  },
});
