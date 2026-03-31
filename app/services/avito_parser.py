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
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/134.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        # Apply stealth evasions to the created page.
        await Stealth().apply_stealth_async(page)

        for page_num in range(1, max_pages + 1):
            url = f"{base_url}&p={page_num}" if page_num > 1 else base_url

            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(3000, 6000))

            listings = await page.locator('[data-marker="item"]').all()

            for listing in listings:
                try:
                    title_elem = listing.locator('[data-marker="item-title"]')
                    price_elem = listing.locator('[data-marker="item-price"]')
                    link_elem = title_elem.locator("a")

                    title = (
                        await title_elem.inner_text()
                        if await title_elem.count() > 0
                        else "Нет названия"
                    )
                    price = (
                        await price_elem.inner_text()
                        if await price_elem.count() > 0
                        else "Цена не указана"
                    )
                    link = (
                        "https://www.avito.ru" + await link_elem.get_attribute("href")
                        if await link_elem.count() > 0
                        else ""
                    )

                    items.append(
                        {
                            "title": title.strip(),
                            "price": price.strip(),
                            "link": link,
                            "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )
                except:
                    continue

            if page_num < max_pages:
                await page.wait_for_timeout(random.randint(8000, 15000))

        await browser.close()

    return items

