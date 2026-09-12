// Covers the env(safe-area-inset-*) padding added for notched phones
// (CLAUDE.md's Design checklist item; see main.css's .site-header-inner
// / .footer-inner / main / .drawer-header / .drawer-body / .viewer-chrome
// / .viewer-prev / .viewer-next comments). Real hardware/simulator is
// the ultimate confirmation and this session has neither, but Chromium
// exposes a CDP hook — Emulation.setSafeAreaInsetsOverride — that makes
// env(safe-area-inset-*) resolve to real values without either, which
// is enough to check the actual computed CSS (the max(<base>, env(...))
// fallback math) rather than just reading the rules and trusting them.
//
// Two things every test needs before env() means anything: `viewport-
// fit=cover` in the page's own <head> (already there — see head.html;
// without it env() always resolves to 0, which the plain zero-inset
// case below also happens to demonstrate) and the CDP override applied
// via the page's OWN CDP session before navigating.
const { test, expect } = require("@playwright/test");
const { firstArtPieceUrl, secondArtPieceUrl } = require("./helpers");

const PORTRAIT_INSETS = { top: 59, bottom: 34, left: 0, right: 0 };
// Deliberately not a literal current-device combination: real notched
// iPhones are all >=768px wide in landscape, which is main.css's own
// desktop-nav/drawer-trigger breakpoint (the drawer never shows there
// today — see the drawer test below). This still checks the CSS
// mechanism itself behaves correctly under side insets, independent of
// whether a specific device reaches it right now.
const LANDSCAPE_INSETS = { top: 0, bottom: 21, left: 47, right: 47 };

async function withInsets(page, insets) {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setSafeAreaInsetsOverride", { insets });
}

function computedPadding(page, selector) {
  return page.evaluate((sel) => {
    const el = document.querySelector(sel);
    const cs = getComputedStyle(el);
    return { top: cs.paddingTop, right: cs.paddingRight, bottom: cs.paddingBottom, left: cs.paddingLeft };
  }, selector);
}

test.describe("portrait notch (top/bottom)", () => {
  test.use({ viewport: { width: 393, height: 852 } });

  test("header/footer/main pad for the notch, falling back to the plain value otherwise", async ({ page }) => {
    await withInsets(page, PORTRAIT_INSETS);
    await page.goto("/");
    expect(await computedPadding(page, ".site-header-inner")).toMatchObject({ top: "59px", left: "16px", right: "16px" });
    // Footer's base bottom padding (2.5rem = 40px) is already bigger
    // than this 34px inset, so max() must keep the base value here --
    // this is the other half of the fallback, not just "does it grow".
    expect(await computedPadding(page, ".footer-inner")).toMatchObject({ bottom: "40px" });
  });

  test("with no inset at all, padding is unchanged from the plain values", async ({ page }) => {
    await withInsets(page, { top: 0, bottom: 0, left: 0, right: 0 });
    await page.goto("/");
    expect(await computedPadding(page, ".site-header-inner")).toMatchObject({ top: "17.6px", left: "16px", right: "16px" });
  });

  test("drawer header/body pad for the notch", async ({ page }) => {
    await withInsets(page, PORTRAIT_INSETS);
    await page.goto("/");
    await page.locator(".drawer-trigger").click();
    await expect(page.locator(".drawer[open]")).toBeAttached();
    expect(await computedPadding(page, ".drawer-header")).toMatchObject({ top: "59px" });
    // Bottom inset (34px) exceeds the base 1.75rem (28px) -> grows;
    // left/right insets are 0 here -> stays at the base 28px.
    expect(await computedPadding(page, ".drawer-body")).toMatchObject({ bottom: "34px", left: "28px", right: "28px" });
  });

  test("fullscreen viewer chrome pads for the notch", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await withInsets(page, PORTRAIT_INSETS);
    await page.goto(url);
    await page.locator("[data-viewer-open]").click();
    expect(await computedPadding(page, ".viewer-chrome")).toMatchObject({ top: "59px", left: "16px", right: "16px" });
  });
});

test.describe("side insets (landscape-style)", () => {
  test.use({ viewport: { width: 700, height: 400 } });

  test("drawer's edge-to-edge divider stays in sync with the padding under a side inset", async ({ page }) => {
    await withInsets(page, LANDSCAPE_INSETS);
    await page.goto("/");
    await page.locator(".drawer-trigger").click();
    await expect(page.locator(".drawer[open]")).toBeAttached();
    expect(await computedPadding(page, ".drawer-body")).toMatchObject({ left: "47px", right: "47px" });
    // --drawer-inset-start/-end drive BOTH the padding above and this
    // negative margin (the divider-bleeds-to-the-true-edge trick) --
    // they must match exactly, or the divider drifts out of sync with
    // its own row's padding on a wide-inset device.
    const margins = await page.evaluate(() => {
      const li = document.querySelector(".drawer .primary-links li");
      const cs = getComputedStyle(li);
      return { left: cs.marginLeft, right: cs.marginRight };
    });
    expect(margins).toEqual({ left: "-47px", right: "-47px" });
  });
});

test.describe("landscape viewer (side insets)", () => {
  test.use({ viewport: { width: 852, height: 393 } });

  test("prev/next chevrons clear a landscape-side notch/rounded-corner inset", async ({ page }) => {
    // The second piece, not the first -- the newest/first piece never
    // has a ‹ (no NextInSection = no newer neighbor), and this test
    // needs both chevrons present. See helpers.js.
    const url = await secondArtPieceUrl(page);
    await withInsets(page, LANDSCAPE_INSETS);
    await page.goto(url);
    await page.locator("[data-viewer-open]").click();
    const left = await page.evaluate(() => getComputedStyle(document.querySelector(".viewer-prev")).left);
    const right = await page.evaluate(() => getComputedStyle(document.querySelector(".viewer-next")).right);
    expect(left).toBe("47px");
    expect(right).toBe("47px");
  });
});
