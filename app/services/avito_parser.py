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
    """УЛУЧШЕННАЯ анти-капча версия 2026 (российский fingerprint)"""
    items: list[dict] = []
    base_url = f"https://www.avito.ru/{location}?q={query.replace(' ', '+')}"

    print(f"🚀 Начинаем парсинг: {query} | страниц: {max_pages} (российский fingerprint)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,   # окно видно — можешь вручную решить капчу, если появится
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-extensions",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1366, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            locale="ru-RU",                    # ← важно!
            timezone_id="Europe/Moscow",       # ← важно!
            extra_http_headers={
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
                "sec-ch-ua": '"Chromium";v="134", "Not;A=Brand";v="99"',
            },
        )

        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        for page_num in range(1, max_pages + 1):
            url = f"{base_url}&p={page_num}" if page_num > 1 else base_url
            print(f"📄 Открываем: {url}")

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=30000)

            # === ЕЩЁ БОЛЕЕ ЧЕЛОВЕЧЕСКОЕ ПОВЕДЕНИЕ ===
            print("🖱️ Имитируем движения мыши...")
            for _ in range(4):
                await page.mouse.move(random.randint(100, 1200), random.randint(100, 700))
                await asyncio.sleep(random.uniform(0.3, 0.8))

            print("📜 Скроллим как человек...")
            for i in range(7):
                try:
                    await page.evaluate("window.scrollBy(0, window.innerHeight * 0.75)")
                    await asyncio.sleep(random.uniform(1.8, 3.2))
                    print(f"   Скролл {i+1}/7...")
                except Exception:
                    print("⚠️ Страница сменилась (капча/редирект) — останавливаемся")
                    break

            # Проверяем наличие карточек
            selectors = [
                '[data-marker="item"]',
                '[data-marker="catalog-serp"] [data-marker="item"]',
                '.items-root > div',
                '[data-marker="catalog-main"]',
            ]

            listings = []
            for sel in selectors:
                try:
                    await page.wait_for_selector(sel, timeout=12000)
                    listings = await page.locator(sel).all()
                    if listings:
                        print(f"✅ Нашёл карточки: {len(listings)} шт.")
                        break
                except Exception:
                    continue

            if not listings:
                print("❌ Карточки не найдены — скорее всего капча")
                await page.screenshot(path="avito_captcha_debug.png")
                print("📸 Скриншот сохранён: avito_captcha_debug.png")
                print("📋 Открой его и опиши, что видишь (капча reCAPTCHA, Cloudflare и т.д.)")
                break

            # Парсим
            for listing in listings:
                try:
                    title = await listing.locator('[data-marker="item-title"]').inner_text(timeout=4000)
                    price = await listing.locator('[data-marker="item-price"]').inner_text(timeout=4000)
                    link = "https://www.avito.ru" + (
                        await listing.locator('a[data-marker="item-title"]').get_attribute("href") or ""
                    )
                    items.append({
                        "title": title.strip(),
                        "price": price.strip(),
                        "link": link,
                        "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                except Exception:
                    continue

            if page_num < max_pages:
                await asyncio.sleep(random.uniform(10, 15))

        await browser.close()

    print(f"✅ Парсинг завершён. Найдено объявлений: {len(items)}")
    return items