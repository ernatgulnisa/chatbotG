#!/bin/bash

# Railway startup script
echo "🚂 Starting Railway deployment..."

# Run database migrations
echo "📦 Running database migrations..."
cd backend
alembic upgrade head

# Start backend server
echo "🚀 Starting FastAPI backend on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
