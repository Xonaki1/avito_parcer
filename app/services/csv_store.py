import csv
from datetime import datetime
from pathlib import Path

from app.core.paths import RESULTS_DIR


def save_items_to_csv(items: list[dict], query: str) -> Path:
    """
    Save parsed items to a timestamped CSV file and return its full path.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = RESULTS_DIR / f"avito_{query}_{timestamp}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["title", "price", "link", "parsed_at"],
        )
        writer.writeheader()
        writer.writerows(items)

    return filename

