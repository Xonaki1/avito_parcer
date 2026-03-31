import sys
import asyncio



if sys.platform.startswith("win"):
    # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Avito Async Parser")
app.include_router(router)

