import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.database import get_db
from app.schemas import RecordResponse, RecordListResponse, RecordUpdate
from app.auth import get_current_user
from app.models import User, Record
from app.config import get_settings
from app.services.openai_service import transcribe_audio, process_text_with_gpt
from app.services.word_service import generate_word_document

router = APIRouter(prefix="/records", tags=["records"])
settings = get_settings()


def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Получение пользователя по токену из query параметра"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = db.query(User).filter(User.username == username).first()
        return user
    except JWTError:
        return None

ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm'}


async def process_record_task(record_id: int, audio_path: str, db_url: str):
    """Фоновая задача обработки записи"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        record = db.query(Record).filter(Record.id == record_id).first()
        if not record:
            return
        
        record.status = "processing"
        db.commit()
        
        # 1. Транскрибация через Whisper
        original_text = await transcribe_audio(audio_path)
        record.original_text = original_text
        db.commit()
        
        # 2. Обработка через GPT
        processed_text = await process_text_with_gpt(original_text)
        record.processed_text = processed_text
        db.commit()
        
        # 3. Генерация Word документа
        word_dir = os.path.join(settings.upload_dir, "documents")
        word_path = generate_word_document(record.title, processed_text, word_dir)
        record.word_file_path = word_path
        
        record.status = "completed"
        db.commit()
        
    except Exception as e:
        record.status = "error"
        record.error_message = str(e)
        db.commit()
    finally:
        db.close()


@router.get("/", response_model=List[RecordListResponse])
async def get_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка всех записей пользователя"""
    records = db.query(Record).filter(Record.user_id == current_user.id).order_by(Record.created_at.desc()).all()
    return records


@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение конкретной записи"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    return record


@router.post("/", response_model=RecordResponse)
async def create_record(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание новой записи с загрузкой аудио"""
    
    # Проверка расширения файла
    file_ext = os.path.splitext(audio_file.filename)[1].lower()
    if file_ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )
    
    # Сохранение аудио файла
    audio_dir = os.path.join(settings.upload_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    import uuid
    filename = f"{uuid.uuid4()}{file_ext}"
    audio_path = os.path.join(audio_dir, filename)
    
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    
    # Создание записи в БД
    record = Record(
        user_id=current_user.id,
        title=title,
        audio_file_path=audio_path,
        status="pending"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # Запуск фоновой обработки
    background_tasks.add_task(
        process_record_task,
        record.id,
        audio_path,
        settings.database_url
    )
    
    return record


@router.patch("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: int,
    update_data: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление записи (название или текст)"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    if update_data.title is not None:
        record.title = update_data.title
    if update_data.processed_text is not None:
        record.processed_text = update_data.processed_text
    
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/{record_id}")
async def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление записи"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    # Удаление файлов
    if record.audio_file_path and os.path.exists(record.audio_file_path):
        os.remove(record.audio_file_path)
    if record.word_file_path and os.path.exists(record.word_file_path):
        os.remove(record.word_file_path)
    
    db.delete(record)
    db.commit()
    
    return {"message": "Запись удалена"}


@router.get("/{record_id}/download/audio")
async def download_audio(
    record_id: int,
    token: str = Query(..., description="JWT токен авторизации"),
    db: Session = Depends(get_db)
):
    """Скачивание аудио файла"""
    user = get_user_from_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Неавторизован")
    
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    if not record.audio_file_path or not os.path.exists(record.audio_file_path):
        raise HTTPException(status_code=404, detail="Аудио файл не найден")
    
    return FileResponse(
        record.audio_file_path,
        filename=f"{record.title}_audio{os.path.splitext(record.audio_file_path)[1]}",
        media_type="audio/mpeg"
    )


@router.get("/{record_id}/download/word")
async def download_word(
    record_id: int,
    token: str = Query(..., description="JWT токен авторизации"),
    db: Session = Depends(get_db)
):
    """Скачивание Word документа"""
    user = get_user_from_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Неавторизован")
    
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    if not record.word_file_path or not os.path.exists(record.word_file_path):
        raise HTTPException(status_code=404, detail="Word документ не найден")
    
    return FileResponse(
        record.word_file_path,
        filename=f"{record.title}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.post("/{record_id}/regenerate-word", response_model=RecordResponse)
async def regenerate_word(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Перегенерация Word документа (после редактирования текста)"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    if not record.processed_text:
        raise HTTPException(status_code=400, detail="Нет текста для генерации документа")
    
    # Удаляем старый документ
    if record.word_file_path and os.path.exists(record.word_file_path):
        os.remove(record.word_file_path)
    
    # Генерируем новый
    word_dir = os.path.join(settings.upload_dir, "documents")
    word_path = generate_word_document(record.title, record.processed_text, word_dir)
    record.word_file_path = word_path
    
    db.commit()
    db.refresh(record)
    
    return record

