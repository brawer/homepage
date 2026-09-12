// Covers the ?view=full address-bar syncing added for issue #104/#113
// (assets/js/nav.js's "Fullscreen art viewer" block). Three ways the
// viewer can end up open each get different history handling there —
// see that block's own comment for the full reasoning; this suite is
// what actually exercises it, since none of it is visible from reading
// the source (it's a small state machine over pushState/replaceState/
// popstate that's easy to get subtly wrong in one branch without
// breaking the others).
const { test, expect } = require("@playwright/test");
const { firstArtPieceUrl } = require("./helpers");

const isOpen = (page) => expect(page.locator("#viewer[open]")).toBeAttached();
const isClosed = (page) => expect(page.locator("#viewer[open]")).not.toBeAttached();

test.describe("opening via the zoom button", () => {
  test("pushes ?view=full and opens the dialog", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url);
    await page.locator("[data-viewer-open]").click();
    await expect(page).toHaveURL(/\?view=full$/);
    await isOpen(page);
  });

  test("Back closes it, strips the URL, and stays on the same page", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url);
    await page.locator("[data-viewer-open]").click();
    await page.goBack();
    await expect(page).not.toHaveURL(/view=full/);
    await expect(page).toHaveURL(new RegExp(url.replace(/\/$/, "") + "/?$"));
    await isClosed(page);
  });

  test("Forward reopens it", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url);
    await page.locator("[data-viewer-open]").click();
    await page.goBack();
    await page.goForward();
    await expect(page).toHaveURL(/\?view=full$/);
    await isOpen(page);
  });

  test("the X button closes it, strips the URL, and stays put", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url);
    await page.locator("[data-viewer-open]").click();
    await page.locator("[data-viewer-close]").click();
    await expect(page).not.toHaveURL(/view=full/);
    await expect(page).toHaveURL(new RegExp(url.replace(/\/$/, "") + "/?$"));
    await isClosed(page);
  });

  test("Escape closes it and strips the URL", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url);
    await page.locator("[data-viewer-open]").click();
    await page.keyboard.press("Escape");
    await expect(page).not.toHaveURL(/view=full/);
    await isClosed(page);
  });
});

test.describe("arriving with ?view=full already in the URL", () => {
  test("a direct link opens the dialog on load and keeps the param", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    await isOpen(page);
    await expect(page).toHaveURL(/\?view=full$/);
  });

  test("closing it strips the URL without navigating away", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    await page.locator("[data-viewer-close]").click();
    await expect(page).not.toHaveURL(/view=full/);
    await expect(page).toHaveURL(new RegExp(url.replace(/\/$/, "") + "/?$"));
    await isClosed(page);
  });

  test("a plain URL with no ?view=full never auto-opens", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url);
    await isClosed(page);
  });
});

test.describe("Prev/Next hops inside the viewer (real navigations)", () => {
  test("a hop lands on the next piece with ?view=full intact", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    const nextHref = await page.locator(".viewer-next").getAttribute("href");
    test.skip(!nextHref, "First art piece has no next sibling to hop to.");
    await page.locator(".viewer-next").click();
    expect(page.url()).not.toContain(url);
    await expect(page).toHaveURL(/\?view=full$/);
    await isOpen(page);
  });

  test("Back from a hop returns to the previous piece, still open", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    const nextHref = await page.locator(".viewer-next").getAttribute("href");
    test.skip(!nextHref, "First art piece has no next sibling to hop to.");
    await page.locator(".viewer-next").click();
    await page.goBack();
    await expect(page).toHaveURL(new RegExp(url.replace(/\/$/, "") + "/\\?view=full$"));
    await isOpen(page);
  });

  test("open -> hop -> hop -> Back x3 fully unwinds to the plain original page", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url);
    await page.locator("[data-viewer-open]").click();
    let hopped = 0;
    for (let i = 0; i < 2; i++) {
      const nextHref = await page.locator(".viewer-next").getAttribute("href");
      if (!nextHref) break;
      await page.locator(".viewer-next").click();
      hopped++;
    }
    test.skip(hopped < 2, "Not enough sibling pieces after the first to hop through twice.");
    for (let i = 0; i < hopped + 1; i++) {
      await page.goBack();
    }
    await expect(page).not.toHaveURL(/view=full/);
    await expect(page).toHaveURL(new RegExp(url.replace(/\/$/, "") + "/?$"));
    await isClosed(page);
  });
});
