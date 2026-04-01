import asyncio
import random
from datetime import datetime

from playwright.async_api import async_playwright
from playwright_stealth import Stealth


async def parse_avito(
    query: str,
    location: str = "rossiya",
    max_pages: int = 1,
) -> list[dict]:
    items: list[dict] = []
    base_url = f"https://www.avito.ru/{location}?q={query.replace(' ', '+')}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="ru-RU",
            timezone_id="Europe/Moscow",
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        for page_num in range(1, max_pages + 1):
            url = f"{base_url}&p={page_num}" if page_num > 1 else base_url

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(10000)

            for i in range(5):
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(1.5)

            listings = await page.locator('[data-marker="item"]').all()

            for listing in listings:
                try:
                    title = await listing.locator('[data-marker="item-title"]').inner_text(timeout=3000)
                    price = await listing.locator('[data-marker="item-price"]').inner_text(timeout=3000)

                    date_elem = listing.locator('[data-marker="item-date"]')
                    published_at = await date_elem.inner_text(timeout=3000) if await date_elem.count() > 0 else "Не указано"

                    link = "https://www.avito.ru" + (
                        await listing.locator('a[data-marker="item-title"]').get_attribute("href") or ""
                    )

                    items.append({
                        "title": title.strip(),
                        "price": price.strip(),
                        "published_at": published_at.strip(),
                        "link": link,
                        "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                except Exception:
                    continue

        await browser.close()

    return items