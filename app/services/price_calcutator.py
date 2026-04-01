from typing import List, Tuple


def calculate_price_stats(
    items: List[dict], exclude_anomalies: bool = False
) -> Tuple[List[dict], float, int]:
    """Расчёт средней цены + фильтрация аномалий (±60%)"""
    prices = []
    for item in items:
        try:
            price_str = (
                item["price"]
                .replace(" ", "")
                .replace("₽", "")
                .replace("руб.", "")
                .strip()
            )
            prices.append(int(price_str))
        except:
            continue

    if not prices:
        return items, 0.0, len(items)

    avg_price = sum(prices) / len(prices)

    if exclude_anomalies:
        filtered_items = []
        for item in items:
            try:
                p = int(
                    item["price"]
                    .replace(" ", "")
                    .replace("₽", "")
                    .replace("руб.", "")
                    .strip()
                )
                deviation = abs(p - avg_price) / avg_price
                if deviation <= 0.6:  # ±60%
                    filtered_items.append(item)
            except:
                filtered_items.append(item)
        return filtered_items, avg_price, len(filtered_items)

    return items, avg_price, len(items)
