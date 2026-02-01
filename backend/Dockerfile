FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директорию для загрузок
RUN mkdir -p uploads/audio uploads/documents

# Делаем entrypoint исполняемым
RUN chmod +x docker-entrypoint.sh

# Порт
EXPOSE 8000

# Запуск через entrypoint
CMD ["./docker-entrypoint.sh"]
