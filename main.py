import sys
from pathlib import Path

# ←←← Это исправляет импорт app.services.* в uvicorn + reload
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
import os

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from fastapi import FastAPI
from app.routes import router


app = FastAPI(title="Avito Parser")
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )