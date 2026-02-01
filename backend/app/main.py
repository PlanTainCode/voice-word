import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, records
from app.config import get_settings
from app.database import engine, Base

settings = get_settings()

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Создание директории для загрузок
os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(
    title="Voice Word API",
    description="API для конвертации голосовых записей в текстовые документы",
    version="1.0.0"
)

# CORS - разрешаем HTTP подключения
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # Для скачивания файлов
)

# Подключение роутеров
app.include_router(auth.router, prefix="/api")
app.include_router(records.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Voice Word API", "version": "1.0.0"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}

