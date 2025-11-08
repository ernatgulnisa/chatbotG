# Руководство по установке и запуску

## 📋 Предварительные требования

- **Node.js** 18+ и npm
- **Python** 3.11+
- **PostgreSQL** 15+
- **Redis** 7+
- **Docker и Docker Compose** (опционально, но рекомендуется)

## 🚀 Способ 1: Запуск с Docker (Рекомендуется)

### 1. Клонируйте репозиторий и настройте переменные окружения

```bash
cd chatbotG
cp .env.example .env
```

Отредактируйте файл `.env` и укажите ваши настройки.

### 2. Запустите все сервисы с Docker Compose

```bash
docker-compose up -d
```

Это запустит:

- PostgreSQL на порту 5432
- Redis на порту 6379
- Backend (FastAPI) на порту 8000
- Frontend (React) на порту 3000
- Celery Worker для фоновых задач
- Celery Beat для планирования задач

### 3. Доступ к приложению

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Остановка сервисов

```bash
docker-compose down
```

Для полного удаления (включая данные):

```bash
docker-compose down -v
```

## 🛠 Способ 2: Локальная установка

### Backend

#### 1. Установите PostgreSQL и Redis

**Windows:**

```powershell
# Скачайте и установите PostgreSQL с https://www.postgresql.org/download/windows/
# Скачайте и установите Redis с https://github.com/microsoftarchive/redis/releases
```

#### 2. Создайте базу данных

```powershell
# Откройте psql и выполните:
CREATE DATABASE chatbot_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO postgres;
```

#### 3. Настройте Python окружение

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. Настройте переменные окружения

Создайте файл `.env` в корне проекта на основе `.env.example`

#### 5. Выполните миграции базы данных

```powershell
# Инициализируйте Alembic (только первый раз)
alembic init alembic

# Создайте первую миграцию
alembic revision --autogenerate -m "Initial migration"

# Примените миграции
alembic upgrade head
```

#### 6. Запустите Backend

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 7. Запустите Celery Worker (в отдельном терминале)

```powershell
cd backend
.\venv\Scripts\activate
celery -A app.celery_worker worker --loglevel=info --pool=solo
```

### Frontend

#### 1. Установите зависимости

```powershell
cd frontend
npm install
```

#### 2. Настройте переменные окружения

Создайте файл `.env.local`:

```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

#### 3. Запустите Frontend

```powershell
npm run dev
```

Frontend будет доступен на http://localhost:3000

## 🔧 Разработка

### Структура проекта

```
chatbotG/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── core/           # Core config
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── store/         # Zustand stores
│   │   ├── services/      # API services
│   │   ├── layouts/       # Layout components
│   │   └── main.jsx       # Entry point
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml      # Docker orchestration
├── .env.example           # Environment variables template
└── README.md              # Documentation
```

### Backend команды

```powershell
# Создать новую миграцию
alembic revision --autogenerate -m "Description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1

# Запустить тесты
pytest

# Форматирование кода
black app/
```

### Frontend команды

```powershell
# Разработка
npm run dev

# Сборка
npm run build

# Просмотр продакшн сборки
npm run preview

# Линтинг
npm run lint
```

## 🔐 Настройка WhatsApp Business API

### 1. Meta (Facebook) WhatsApp Cloud API

1. Перейдите на https://developers.facebook.com/
2. Создайте новое приложение
3. Добавьте продукт "WhatsApp"
4. Получите:
   - Phone Number ID
   - WhatsApp Business Account ID (WABA ID)
   - Access Token
5. Настройте Webhook:

   - URL: `https://your-domain.com/api/v1/webhooks/whatsapp`
   - Verify Token: укажите свой токен из `.env`
   - Подпишитесь на события: `messages`

6. Обновите `.env`:

```
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_VERIFY_TOKEN=your-verify-token
WHATSAPP_APP_SECRET=your-app-secret
```

## 📊 Мониторинг

### Логи Docker

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Проверка здоровья сервисов

```bash
# Backend health check
curl http://localhost:8000/health

# PostgreSQL
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping
```

## 🐛 Устранение неполадок

### Backend не запускается

1. Проверьте, что PostgreSQL и Redis запущены
2. Проверьте переменные окружения в `.env`
3. Проверьте логи: `docker-compose logs backend`

### Frontend не подключается к Backend

1. Проверьте `VITE_API_URL` в `.env.local`
2. Убедитесь, что Backend запущен на порту 8000
3. Проверьте CORS настройки в Backend

### Ошибки миграции БД

```powershell
# Сбросить все миграции
alembic downgrade base

# Удалить БД и создать заново
dropdb chatbot_db
createdb chatbot_db

# Применить миграции заново
alembic upgrade head
```

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи сервисов
2. Убедитесь, что все порты свободны (3000, 8000, 5432, 6379)
3. Проверьте файрвол и антивирус

## 🚀 Деплой на продакшн

См. документацию по деплою для:

- AWS / Azure / Google Cloud
- Render / Railway / Vercel
- VPS с Nginx

## 📝 Лицензия

MIT
