"""
screenshot_capture.py — Capture store screenshots using Playwright (headless).
Falls back gracefully if Playwright is unavailable or capture fails.
"""

import os
import logging
import asyncio
from config import PDF_DIR, USER_AGENT

logger = logging.getLogger(__name__)


def sanitize_foldername(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")


async def _capture_async(store_url: str, store_name: str, product_url: str | None) -> list[str]:
    """Async playwright capture — returns list of saved PNG file paths."""
    from playwright.async_api import async_playwright

    store_folder = os.path.join(PDF_DIR, sanitize_foldername(store_name))
    os.makedirs(store_folder, exist_ok=True)

    screenshots = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        # ── Homepage Screenshot ──────────────────────────────────────────────
        try:
            await page.goto(store_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
            path = os.path.join(store_folder, "homepage.png")
            await page.screenshot(path=path, full_page=True)
            screenshots.append(path)
            logger.info(f"Screenshot saved: {path}")
        except Exception as e:
            logger.warning(f"Homepage screenshot failed: {e}")

        # Mobile screenshots disabled per user request (desktop only)
        # ── Mobile Homepage Screenshot (Removed) ──

        # ── Product Page Screenshot ──────────────────────────────────────────
        if product_url:
            try:
                await page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)
                path = os.path.join(store_folder, "product_page.png")
                await page.screenshot(path=path, full_page=True)
                screenshots.append(path)
                logger.info(f"Product page screenshot saved: {path}")
            except Exception as e:
                logger.warning(f"Product page screenshot failed: {e}")

        await browser.close()

    return screenshots


def capture_screenshots(store_url: str, store_name: str, product_url: str | None = None) -> list[str]:
    """
    Synchronous wrapper for async screenshot capture.
    Returns list of screenshot file paths (may be empty if Playwright unavailable).
    """
    try:
        import playwright
    except ImportError:
        logger.warning("Playwright not installed — skipping screenshots. Run: pip install playwright && playwright install chromium")
        return []

    try:
        screenshots = asyncio.run(_capture_async(store_url, store_name, product_url))
        return screenshots
    except Exception as e:
        logger.warning(f"Screenshot capture failed entirely for {store_url}: {e}")
        return []


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://allbirds.com")
    parser.add_argument("--name", default="Allbirds")
    args = parser.parse_args()
    paths = capture_screenshots(args.url, args.name)
    print("Screenshots:", paths)
