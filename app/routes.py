from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio

from app.core.paths import RESULTS_DIR
from app.services.avito_parser import parse_avito
from app.services.csv_store import save_items_to_csv

router = APIRouter()
templates = Jinja2Templates(directory="templates")
PARSE_SEMAPHORE = asyncio.Semaphore(3)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.post("/parse")
async def start_parse(
    request: Request,
    query: str = Form(...),
    location: str = Form("rossiya"),
    max_pages: int = Form(1),
):
    items = await parse_avito(query, location, max_pages)
    csv_path = save_items_to_csv(items, query)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "items": items[:50],
            "total": len(items),
            "filename": csv_path.name,
            "query": query,
        },
    )


@router.get("/download/{filename}")
async def download(filename: str):
    file_path = RESULTS_DIR / filename
    if not file_path.exists():
        return {"error": "Файл не найден"}
    return FileResponse(file_path, media_type="text/csv", filename=filename)
