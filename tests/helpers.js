// Shared helpers for the nav.js test suite. Deliberately does not
// hardcode a specific art-piece slug: /art/ always has real pieces
// (see CLAUDE.md — 20+ as of writing), and picking whichever sorts
// first keeps these tests working across content changes (a piece
// being renamed, reordered, or retired) without any updates here.

/**
 * Navigates to the art grid and returns the first piece's own URL
 * (its plain detail-page path, e.g. "/art/some-piece/" — no
 * ?view=full). Whatever it is, it's real content with a real image,
 * which is all the fullscreen-viewer/letterbox tests need.
 * @param {import('@playwright/test').Page} page
 */
async function firstArtPieceUrl(page) {
  await page.goto("/art/");
  const href = await page.locator("a.gallery-item").first().getAttribute("href");
  if (!href) throw new Error("No art pieces found on /art/ — can't pick a test fixture.");
  return href;
}

/**
 * Like firstArtPieceUrl, but the SECOND piece — guaranteed (with more
 * than one piece in the section, true for /art/ today and for the
 * foreseeable future) to have both a newer and an older neighbor, so
 * both the viewer's ‹ and › chevrons render. The very first/newest
 * piece only ever has an older neighbor (no ‹), which is exactly right
 * for content but wrong for a test that needs both chevrons present.
 * @param {import('@playwright/test').Page} page
 */
async function secondArtPieceUrl(page) {
  await page.goto("/art/");
  const href = await page.locator("a.gallery-item").nth(1).getAttribute("href");
  if (!href) throw new Error("Fewer than two art pieces on /art/ — can't pick this test fixture.");
  return href;
}

module.exports = { firstArtPieceUrl, secondArtPieceUrl };
