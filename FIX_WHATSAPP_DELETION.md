# Решение проблемы удаления номера WhatsApp

## Проблема

При попытке удалить номер WhatsApp из системы возникает ошибка из-за того, что к номеру привязаны другие данные (боты, разговоры, рассылки).

## Причина

База данных не была настроена на каскадное удаление (CASCADE DELETE). Это означает, что при попытке удалить родительскую запись (номер WhatsApp), база данных блокирует операцию, если существуют связанные дочерние записи.

## Решение

### Автоматическое решение (рекомендуется)

Запустите PowerShell скрипт:

```powershell
.\fix_whatsapp_deletion.ps1
```

Этот скрипт:

1. Проверит, что PostgreSQL запущен
2. Применит миграцию базы данных
3. Добавит каскадное удаление для всех связей

### Ручное решение

Если автоматический скрипт не работает:

1. **Убедитесь, что PostgreSQL запущен:**

   ```powershell
   docker-compose up -d db
   ```

2. **Перейдите в директорию backend:**

   ```powershell
   cd backend
   ```

3. **Запустите миграцию:**

   ```powershell
   python apply_cascade_migration.py
   ```

4. **Перезапустите сервер:**
   ```powershell
   cd ..
   .\start.ps1
   ```

## Что изменилось

После применения миграции:

### 1. **Модель WhatsAppNumber** (`backend/app/models/whatsapp_number.py`)

- Добавлено `cascade="all, delete-orphan"` для связей:
  - `bots`
  - `conversations`
  - (broadcasts уже удаляются через свою связь)

### 2. **База данных**

- Обновлены Foreign Key constraints:
  - `bots.whatsapp_number_id` → ON DELETE CASCADE
  - `conversations.whatsapp_number_id` → ON DELETE CASCADE
  - `broadcasts.whatsapp_number_id` → ON DELETE CASCADE

### 3. **API Endpoint** (`backend/app/api/v1/endpoints/whatsapp.py`)

- Улучшена обработка ошибок
- Добавлен try-catch блок
- Более информативные сообщения об ошибках

### 4. **Фронтенд** (`frontend/src/pages/WhatsAppSettings.jsx`)

- Улучшено предупреждение перед удалением
- Показывает, какие данные будут удалены:
  - Все боты
  - Все разговоры
  - Все рассылки
- Лучшие сообщения об ошибках

## Поведение после исправления

При удалении номера WhatsApp:

1. **Автоматически удалятся:**

   - ✅ Все боты, привязанные к этому номеру
   - ✅ Все сценарии ботов
   - ✅ Все разговоры через этот номер
   - ✅ Все сообщения в этих разговорах
   - ✅ Все рассылки с этого номера
   - ✅ Все сообщения в рассылках

2. **Пользователь увидит:**
   - Предупреждение о том, что будет удалено
   - Подтверждение успешного удаления
   - Или понятное сообщение об ошибке (если что-то пошло не так)

## Безопасность

⚠️ **ВНИМАНИЕ:** Удаление номера WhatsApp является необратимой операцией!

Все связанные данные будут безвозвратно удалены. Убедитесь, что вы:

- Сделали резервную копию важных данных
- Понимаете последствия удаления
- Действительно хотите удалить номер

## Проверка работы

После применения миграции:

1. Откройте `http://localhost:3001/whatsapp`
2. Попробуйте удалить номер WhatsApp
3. Вы увидите предупреждение о том, что будет удалено
4. После подтверждения номер и все связанные данные будут удалены

## Откат изменений

Если вам нужно откатить изменения (вернуть запрет на удаление):

```sql
-- Выполните в PostgreSQL
ALTER TABLE bots
DROP CONSTRAINT bots_whatsapp_number_id_fkey,
ADD CONSTRAINT bots_whatsapp_number_id_fkey
FOREIGN KEY (whatsapp_number_id)
REFERENCES whatsapp_numbers(id);

ALTER TABLE conversations
DROP CONSTRAINT conversations_whatsapp_number_id_fkey,
ADD CONSTRAINT conversations_whatsapp_number_id_fkey
FOREIGN KEY (whatsapp_number_id)
REFERENCES whatsapp_numbers(id);

ALTER TABLE broadcasts
DROP CONSTRAINT broadcasts_whatsapp_number_id_fkey,
ADD CONSTRAINT broadcasts_whatsapp_number_id_fkey
FOREIGN KEY (whatsapp_number_id)
REFERENCES whatsapp_numbers(id);
```

## Техническая документация

### Каскадное удаление (CASCADE DELETE)

**Что это?**

- Автоматическое удаление связанных записей при удалении родительской записи

**Как работает?**

```
WhatsApp Number (ID=1)
  ├── Bot 1 → удалится автоматически
  │   └── Scenario 1 → удалится автоматически
  ├── Bot 2 → удалится автоматически
  ├── Conversation 1 → удалится автоматически
  │   └── Messages → удалятся автоматически
  └── Broadcast 1 → удалится автоматически
      └── Messages → удалятся автоматически
```

**Альтернативные стратегии:**

- `SET NULL` - установить NULL вместо удаления
- `RESTRICT` - запретить удаление (текущее поведение)
- `SET DEFAULT` - установить значение по умолчанию
- `NO ACTION` - ничего не делать (поведение по умолчанию)

### SQL-запросы миграции

```sql
-- Боты
ALTER TABLE bots
DROP CONSTRAINT IF EXISTS bots_whatsapp_number_id_fkey,
ADD CONSTRAINT bots_whatsapp_number_id_fkey
FOREIGN KEY (whatsapp_number_id)
REFERENCES whatsapp_numbers(id)
ON DELETE CASCADE;

-- Разговоры
ALTER TABLE conversations
DROP CONSTRAINT IF EXISTS conversations_whatsapp_number_id_fkey,
ADD CONSTRAINT conversations_whatsapp_number_id_fkey
FOREIGN KEY (whatsapp_number_id)
REFERENCES whatsapp_numbers(id)
ON DELETE CASCADE;

-- Рассылки
ALTER TABLE broadcasts
DROP CONSTRAINT IF EXISTS broadcasts_whatsapp_number_id_fkey,
ADD CONSTRAINT broadcasts_whatsapp_number_id_fkey
FOREIGN KEY (whatsapp_number_id)
REFERENCES whatsapp_numbers(id)
ON DELETE CASCADE;
```

## Поддержка

Если у вас остались проблемы:

1. Проверьте логи сервера
2. Убедитесь, что PostgreSQL запущен
3. Проверьте версию PostgreSQL (должна быть >= 12)
4. Убедитесь, что у пользователя БД есть права на изменение таблиц

## История изменений

- **2025-11-06**: Исправление проблемы удаления номеров WhatsApp
  - Добавлено каскадное удаление
  - Улучшены предупреждения в UI
  - Добавлена обработка ошибок
