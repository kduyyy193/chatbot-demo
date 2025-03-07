from fastapi import FastAPI
from src.api.v1 import chat, train, telegram
from src.config.settings import settings
from contextlib import asynccontextmanager

app = FastAPI(
    title="Chatbot API",
    description="API for a chatbot using DistilBERT",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(telegram.router, prefix="/api/v1", tags=["Telegram"])
app.include_router(train.router, prefix="/api/v1", tags=["Train"])


@app.post("/api/v1/webhook")
async def webhook(update: dict):
    telegram_service = app.state.telegram_service
    telegram_service.process_update(update)
    return {"status": "ok"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram.setup_webhook()
    yield


@app.get("/")
async def root():
    return {"message": "Chatbot API running!", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info" if settings.ENVIRONMENT == "production" else "debug",
    )
