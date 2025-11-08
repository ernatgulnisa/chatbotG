#!/bin/bash

# Render Startup Script
# Выполняет миграции и запускает FastAPI сервер

set -e  # Остановка при ошибке

echo "🚀 Starting Render deployment..."

# Переход в директорию backend
cd backend

# Запуск миграций Alembic
echo "📦 Running database migrations..."
alembic upgrade head

# Инициализация базы данных (создание начальных данных если нужно)
echo "🗄️ Initializing database..."
python init_db.py || echo "Database already initialized"

# Запуск FastAPI с uvicorn
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
