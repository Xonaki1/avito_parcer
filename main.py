from fastapi import FastAPI

from app.routes import router

app = FastAPI(title="Avito Async Parser")
app.include_router(router)

