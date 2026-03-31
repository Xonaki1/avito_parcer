import asyncio
import sys

from fastapi import FastAPI

from app.routes import router


if sys.platform.startswith("win"):
    # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = FastAPI(title="Avito Async Parser")
app.include_router(router)

