# Voice Word

Веб-приложение для конвертации голосовых записей в текстовые документы Word.

## Технологии

- **Frontend**: Nuxt 3, Vue 3, Pinia
- **Backend**: Python, FastAPI
- **База данных**: PostgreSQL
- **AI**: OpenAI Whisper (распознавание речи), GPT (обработка текста)

## Требования

- Python 3.10+
- Node.js 18+ / Bun
- PostgreSQL

## Установка

### 1. База данных

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE alb;
```

### 2. Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
# Создайте файл .env на основе .env.example и укажите OPENAI_API_KEY

# Создание пользователя в БД
python seed_user.py

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend

# Установка зависимостей
bun install

# Запуск dev сервера
bun run dev
```

## Конфигурация

### Backend (.env)

```env
DATABASE_URL=postgresql://postgres:3141@localhost/alb
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-your-openai-api-key
GPT_MODEL=gpt-5.2
```

### Frontend

По умолчанию API доступен на `http://localhost:8000/api`. Для изменения:

```env
NUXT_PUBLIC_API_BASE=http://localhost:8000/api
```

## Учетные данные

- **Логин**: albert
- **Пароль**: Albert1940!

## Функционал

1. **Авторизация** - защищенный доступ для одного пользователя
2. **Загрузка аудио** - поддержка MP3, WAV, M4A, OGG, FLAC, WEBM
3. **Распознавание речи** - через OpenAI Whisper API
4. **Обработка текста** - GPT проверяет слова, расставляет пунктуацию и абзацы
5. **Генерация Word** - автоматическое создание форматированного документа
6. **Редактирование** - возможность отредактировать текст и пересоздать документ

## Структура проекта

```
voice-word/
├── backend/
│   ├── app/
│   │   ├── api/           # API роуты
│   │   ├── services/      # Сервисы (OpenAI, Word)
│   │   ├── auth.py        # Авторизация
│   │   ├── config.py      # Конфигурация
│   │   ├── database.py    # Подключение к БД
│   │   ├── main.py        # Точка входа
│   │   ├── models.py      # Модели SQLAlchemy
│   │   └── schemas.py     # Pydantic схемы
│   ├── seed_user.py       # Создание пользователя
│   └── requirements.txt
├── frontend/
│   ├── assets/css/        # Стили
│   ├── composables/       # Композиции Vue
│   ├── layouts/           # Макеты
│   ├── middleware/        # Middleware
│   ├── pages/             # Страницы
│   ├── stores/            # Pinia сторы
│   └── nuxt.config.ts
└── README.md
```

## API Endpoints

- `POST /api/auth/login` - авторизация
- `GET /api/auth/me` - текущий пользователь
- `GET /api/records/` - список записей
- `POST /api/records/` - создание записи
- `GET /api/records/{id}` - получение записи
- `PATCH /api/records/{id}` - обновление записи
- `DELETE /api/records/{id}` - удаление записи
- `GET /api/records/{id}/download/audio` - скачать аудио
- `GET /api/records/{id}/download/word` - скачать Word
- `POST /api/records/{id}/regenerate-word` - пересоздать Word

