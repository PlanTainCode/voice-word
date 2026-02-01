#!/bin/bash
set -e

# Ждем пока БД будет готова
echo "Waiting for database..."
while ! pg_isready -h postgres -U postgres -q; do
    sleep 1
done
echo "Database is ready!"

# Создаем пользователя если его нет
echo "Seeding user..."
python seed_user.py || true

# Запускаем сервер
echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
