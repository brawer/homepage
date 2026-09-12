// Covers clicking the empty letterbox/pillarbox margin around the
// photo to close the fullscreen viewer (a follow-up to #104/#113 —
// the real dialog ::backdrop is unreachable, see assets/js/nav.js's
// own comment on this). The margin math is coordinate-based (the <img>
// element's own box is stretched to fill its container regardless of
// the photo's aspect ratio — see main.css's .viewer-image img comment
// — so a plain e.target check can't tell "on the photo" from "in the
// dead space" apart), which is exactly the kind of logic worth a real
// pixel-level test rather than eyeballing a screenshot.
//
// Deliberately picks whichever art piece sorts first (see helpers.js)
// rather than a hardcoded slug, and deliberately exercises BOTH a wide/
// short viewport (pillarboxes left/right for any normal painting) and
// a tall/narrow one (letterboxes top/bottom) rather than assuming a
// particular aspect ratio.
const { test, expect } = require("@playwright/test");
const { firstArtPieceUrl } = require("./helpers");

async function renderedImageRect(page) {
  return page.evaluate(() => {
    const img = document.querySelector(".viewer-image img");
    const box = img.getBoundingClientRect();
    const iw = img.naturalWidth;
    const ih = img.naturalHeight;
    const scale = Math.min(box.width / iw, box.height / ih);
    const renderedW = iw * scale;
    const renderedH = ih * scale;
    return {
      left: box.left + (box.width - renderedW) / 2,
      right: box.left + (box.width + renderedW) / 2,
      top: box.top + (box.height - renderedH) / 2,
      bottom: box.top + (box.height + renderedH) / 2,
      boxTop: box.top,
      boxBottom: box.bottom,
    };
  });
}

const isOpen = (page) => expect(page.locator("#viewer[open]")).toBeAttached();
const isClosed = (page) => expect(page.locator("#viewer[open]")).not.toBeAttached();

test.describe("wide viewport (pillarboxes left/right)", () => {
  test.use({ viewport: { width: 1200, height: 500 } });

  test("clicking deep in the left margin closes the viewer and cleans the URL", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    const rect = await renderedImageRect(page);
    // y=100: below the chrome bar, well clear of the prev/next chevrons
    // (vertically centered), so this isolates the margin itself.
    await page.mouse.click(Math.max(20, rect.left / 2), 100);
    await isClosed(page);
    await expect(page).not.toHaveURL(/view=full/);
  });

  test("clicking deep in the right margin closes the viewer", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    const rect = await renderedImageRect(page);
    await page.mouse.click((rect.right + 1200) / 2, 100);
    await isClosed(page);
  });

  test("clicking the photo itself does not close the viewer", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    const rect = await renderedImageRect(page);
    await page.mouse.click((rect.left + rect.right) / 2, 100);
    await isOpen(page);
  });

  test("a click just inside the rendered edge stays open; just outside closes", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    let rect = await renderedImageRect(page);
    // Skip if this piece's letterbox math leaves no usable margin at
    // this viewport (an unusually wide-aspect source) -- the boundary
    // itself is what's under test, not this specific piece.
    test.skip(rect.left < 5, "Rendered image has no measurable left margin at this viewport.");

    await page.mouse.click(Math.ceil(rect.left) + 3, 100);
    await isOpen(page);

    await page.goto(url + "?view=full");
    rect = await renderedImageRect(page);
    await page.mouse.click(Math.floor(rect.left) - 3, 100);
    await isClosed(page);
  });

  test("the chrome-bar gap (out of scope) does not close the viewer", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    await page.mouse.click(600, 28);
    await isOpen(page);
  });

  test("the prev/next chevrons still navigate (not swallowed by the margin listener)", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    const nextHref = await page.locator(".viewer-next").getAttribute("href");
    test.skip(!nextHref, "First art piece has no next sibling.");
    await page.locator(".viewer-next").click();
    await expect(page).toHaveURL(/\?view=full$/);
    expect(page.url()).not.toContain(url);
  });
});

test.describe("tall viewport (letterboxes top/bottom)", () => {
  test.use({ viewport: { width: 420, height: 1400 } });

  test("clicking deep in the top or bottom margin closes the viewer", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    const rect = await renderedImageRect(page);
    test.skip(rect.top - rect.boxTop < 5, "Rendered image has no measurable top margin at this viewport.");

    await page.mouse.click(210, Math.round((rect.boxTop + rect.top) / 2));
    await isClosed(page);

    await page.goto(url + "?view=full");
    await page.mouse.click(210, Math.round((rect.bottom + rect.boxBottom) / 2));
    await isClosed(page);
  });

  test("clicking the photo itself does not close the viewer", async ({ page }) => {
    const url = await firstArtPieceUrl(page);
    await page.goto(url + "?view=full");
    const rect = await renderedImageRect(page);
    await page.mouse.click(210, Math.round((rect.top + rect.bottom) / 2));
    await isOpen(page);
  });
});
