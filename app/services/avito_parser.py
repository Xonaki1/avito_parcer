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
    """Асинхронный парсер Avito (обновлённая версия 2026)"""
    items: list[dict] = []
    base_url = f"https://www.avito.ru/{location}?q={query.replace(' ', '+')}"

    print(f"🚀 Начинаем парсинг: {query} | страниц: {max_pages}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/134.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        for page_num in range(1, max_pages + 1):
            url = f"{base_url}&p={page_num}" if page_num > 1 else base_url
            print(f"📄 Загружаем страницу {page_num}: {url}")

            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=15000)  # ← главное улучшение
            await asyncio.sleep(random.uniform(3, 6))

            # Более надёжный селектор + ожидание
            await page.wait_for_selector('[data-marker="item"]', timeout=10000)
            listings = await page.locator('[data-marker="item"]').all()

            print(f"   Найдено карточек на странице: {len(listings)}")

            for listing in listings:
                try:
                    title = await listing.locator('[data-marker="item-title"]').inner_text(timeout=2000)
                    price = await listing.locator('[data-marker="item-price"]').inner_text(timeout=2000)
                    link = "https://www.avito.ru" + (
                        await listing.locator("a[data-marker='item-title']").get_attribute("href") or ""
                    )

                    items.append({
                        "title": title.strip(),
                        "price": price.strip(),
                        "link": link,
                        "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                except Exception:
                    continue

            # Пауза между страницами
            if page_num < max_pages:
                await asyncio.sleep(random.uniform(8, 15))

        await browser.close()

    print(f"✅ Парсинг завершён. Всего найдено: {len(items)} объявлений")
    return items