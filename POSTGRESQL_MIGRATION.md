# 🔄 Переход с SQLite на PostgreSQL

## ✅ Что было сделано

1. **Обновлён `.env`**: DATABASE_URL теперь указывает на PostgreSQL
2. **Обновлён `config.py`**: PostgreSQL установлен по умолчанию
3. **Готов `docker-compose.yml`**: PostgreSQL уже настроен

---

## 🚀 Варианты запуска PostgreSQL

### Вариант 1: Docker (Рекомендуется) ⭐

**Требования:** Docker Desktop установлен

```powershell
# 1. Запустить только PostgreSQL
docker-compose up -d postgres

# 2. Проверить, что БД запустилась
docker ps

# 3. Применить миграции
cd backend
& "C:/Program Files/Python311/python.exe" -m alembic upgrade head

# 4. Запустить приложение
& "C:/Program Files/Python311/python.exe" -m uvicorn app.main:app --reload
```

**Преимущества:**
- ✅ Быстрый старт (1 команда)
- ✅ Не нужно устанавливать PostgreSQL
- ✅ Легко удалить: `docker-compose down -v`

---

### Вариант 2: Локальная установка PostgreSQL

**Требования:** PostgreSQL 15+ установлен на компьютере

#### Установка PostgreSQL:

1. Скачать: https://www.postgresql.org/download/windows/
2. Запустить installer
3. Выбрать пароль: `postgres`
4. Порт: `5432`

#### Создание БД:

```powershell
# Открыть psql
psql -U postgres

# В psql выполнить:
CREATE DATABASE chatbot_db;
\q
```

#### Запуск приложения:

```powershell
cd backend

# Применить миграции
& "C:/Program Files/Python311/python.exe" -m alembic upgrade head

# Запустить
& "C:/Program Files/Python311/python.exe" -m uvicorn app.main:app --reload
```

---

### Вариант 3: Облачная БД (Бесплатно)

#### A. Render.com (Рекомендуется)

1. Зайти на https://dashboard.render.com/
2. New → PostgreSQL
3. Выбрать Free план
4. Database Name: `chatbot_db`
5. Скопировать **External Database URL**
6. Вставить в `.env`:

```env
DATABASE_URL=postgresql://user:password@hostname:5432/database
```

#### B. Supabase (Альтернатива)

1. https://supabase.com/
2. New Project
3. Скопировать Connection String
4. Вставить в `.env`

#### C. Railway.app (Альтернатива)

1. https://railway.app/
2. New Project → PostgreSQL
3. Variables → Copy DATABASE_URL
4. Вставить в `.env`

---

## 📋 Миграция данных из SQLite

Если у вас есть данные в `chatbot.db`:

```powershell
# 1. Установить pgloader
# Скачать: https://github.com/dimitri/pgloader/releases

# 2. Создать файл migration.load:
```

**migration.load:**
```
LOAD DATABASE
     FROM sqlite://chatbot.db
     INTO postgresql://postgres:postgres@localhost:5432/chatbot_db

WITH include drop, create tables, create indexes, reset sequences

SET work_mem to '16MB', maintenance_work_mem to '512 MB';
```

```powershell
# 3. Запустить миграцию
pgloader migration.load
```

**Альтернатива (вручную):**

```powershell
# Экспорт из SQLite
sqlite3 chatbot.db .dump > backup.sql

# Импорт в PostgreSQL (с корректировками)
# SQLite и PostgreSQL имеют разный синтаксис, потребуется редактирование
```

---

## ✅ Проверка подключения

```powershell
# Тест подключения к PostgreSQL
& "C:/Program Files/Python311/python.exe" -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:postgres@localhost:5432/chatbot_db')
conn = engine.connect()
print('✅ PostgreSQL подключён успешно!')
conn.close()
"
```

---

## 🔧 Применение миграций Alembic

```powershell
cd backend

# Просмотр текущей версии
& "C:/Program Files/Python311/python.exe" -m alembic current

# Применить все миграции
& "C:/Program Files/Python311/python.exe" -m alembic upgrade head

# Создать начальные данные (если нужно)
& "C:/Program Files/Python311/python.exe" init_db.py
```

---

## 📊 Проверка таблиц

```powershell
# Подключиться к БД
psql -U postgres -d chatbot_db

# Список таблиц
\dt

# Структура таблицы
\d users

# Выход
\q
```

---

## 🐛 Troubleshooting

### Ошибка: "could not connect to server"

```powershell
# Проверить, запущен ли PostgreSQL
Get-Service postgresql*

# Или для Docker
docker ps | Select-String postgres
```

### Ошибка: "password authentication failed"

Проверьте пароль в `.env`:
```env
POSTGRES_PASSWORD=postgres
```

### Ошибка: "database does not exist"

```powershell
# Создать БД
createdb -U postgres chatbot_db

# Или в psql
psql -U postgres
CREATE DATABASE chatbot_db;
```

### Ошибка: "relation does not exist"

```powershell
# Применить миграции
cd backend
& "C:/Program Files/Python311/python.exe" -m alembic upgrade head
```

---

## 🎯 Быстрый старт (рекомендуемый путь)

```powershell
# 1. Запустить PostgreSQL в Docker
docker-compose up -d postgres

# Подождать 10 секунд, пока БД инициализируется
Start-Sleep -Seconds 10

# 2. Применить миграции
cd backend
$env:PYTHONPATH = "$PWD"
& "C:/Program Files/Python311/python.exe" -m alembic upgrade head

# 3. Создать тестовые данные (опционально)
& "C:/Program Files/Python311/python.exe" init_db.py

# 4. Запустить backend
& "C:/Program Files/Python311/python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# В другом терминале:
cd ../frontend
npm run dev
```

---

## 📝 Обновлённые файлы

1. **backend/.env** ✅
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatbot_db
   ```

2. **backend/app/core/config.py** ✅
   ```python
   DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/chatbot_db"
   ```

3. **docker-compose.yml** ✅ (уже был настроен)

---

## 🎉 Результат

После перехода на PostgreSQL:

- ✅ **Production-ready**: PostgreSQL поддерживается всеми хостингами
- ✅ **Concurrency**: Несколько пользователей одновременно
- ✅ **Advanced features**: Full-text search, JSON columns, triggers
- ✅ **Scalability**: Миллионы записей без проблем
- ✅ **Backups**: Автоматические бэкапы на облачных БД
- ✅ **Alembic migrations**: Версионирование схемы БД

---

## 📚 Дополнительные ресурсы

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy with PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Docker Compose Guide](https://docs.docker.com/compose/)

---

**Статус:** ✅ Конфигурация готова! Выберите вариант запуска PostgreSQL.
