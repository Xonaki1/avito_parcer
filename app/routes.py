from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.services.avito_parser import parse_avito
from app.services.price_calculator import calculate_price_stats

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/parse", response_class=HTMLResponse)
async def start_parse(
    request: Request,
    query: str = Form(...),
    location: str = Form("rossiya"),
    max_pages: int = Form(1),
    exclude_anomalies: bool = Form(False),
):
    items = await parse_avito(query, location, max_pages)

    filtered_items, avg_price, filtered_count = calculate_price_stats(
        items, exclude_anomalies
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": filtered_items,
            "avg_price": round(avg_price) if avg_price else 0,
            "total_items": len(items),
            "filtered_items_count": filtered_count,
            "exclude_anomalies": exclude_anomalies,
            "query": query,
        },
    )
