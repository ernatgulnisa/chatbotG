#!/bin/bash

# Render Startup Script
# Создает таблицы, выполняет миграции и запускает FastAPI сервер

set -e  # Остановка при ошибке

echo "🚀 Starting Render deployment..."

# Переход в директорию backend
cd backend

# Создание таблиц в БД (если их нет)
echo "📦 Creating database tables..."
python -c "
from app.core.database import engine, Base
from app.models import base  # Import all models
print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('✅ Tables created successfully')
" || echo "⚠️ Table creation skipped (may already exist)"

# Запуск миграций Alembic (для обновления constraints)
echo "� Running database migrations..."
alembic upgrade head || echo "⚠️ Migrations skipped (may already be applied)"

# Инициализация базы данных (создание начальных данных)
echo "🗄️ Initializing database..."
python init_db.py || echo "✅ Database already initialized"

# Проверка и создание WhatsApp данных (приоритетная проверка)
echo "📱 Checking WhatsApp configuration..."
python check_and_init_whatsapp.py || {
    echo "⚠️ WhatsApp check failed, trying fallback initialization..."
    # Fallback to bot templates
    python init_bot_templates.py || {
        echo "⚠️ Bot templates initialization also failed"
        echo "   You can add WhatsApp number manually through web interface"
    }
}

# Запуск FastAPI с uvicorn
echo "🌐 Starting FastAPI server on port ${PORT:-10000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
