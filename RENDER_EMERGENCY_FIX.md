# 🚨 Render Emergency Fix - WhatsApp Number Not Found

## Problem
```
❌ WhatsApp number not found: 819213961283826
```

## Quick Fix (2 ways)

### Option 1: Wait for Auto-Deploy (Recommended)
Render автоматически задеплоит новый код с GitHub. Обычно это занимает 2-5 минут.

**Проверить статус:**
1. Открыть Render Dashboard
2. Перейти в ваш сервис
3. Проверить раздел "Events" или "Logs"
4. Искать коммит `74ed6ec` или сообщение "Deployment successful"

**Что ждать в логах:**
```
🚀 Starting Render deployment...
📦 Creating database tables...
🔄 Running database migrations...
🗄️ Initializing database...
📱 Checking WhatsApp configuration...
✅ All data exists, nothing to create
🌐 Starting FastAPI server on port 10000...
```

### Option 2: Manual Fix via Render Shell (Immediate)

Если не можете ждать, используйте Render Shell для немедленного создания данных.

**Шаги:**

1. **Открыть Shell в Render Dashboard:**
   - Откройте ваш сервис на render.com
   - Нажмите "Shell" в верхнем меню
   - Дождитесь загрузки терминала

2. **Запустить проверку и инициализацию:**
```bash
cd backend
python check_and_init_whatsapp.py
```

3. **Проверить результат:**
```
========================================================
  Checking Database
========================================================

📱 WhatsApp Numbers: 1
   • +1234567890 (ID: demo_phone_id)
     Status: connected, Active: True

🏢 Businesses: 1
   • Demo Business (ID: 1)

👤 Users: 1
   • admin@chatbot.com - owner

========================================================
✅ All data exists, nothing to create
========================================================
```

4. **Если нужно создать с реальными данными из переменных окружения:**
```bash
# Проверить переменные окружения
echo $WHATSAPP_PHONE_NUMBER
echo $WHATSAPP_PHONE_NUMBER_ID

# Если они пустые, установить временно
export WHATSAPP_PHONE_NUMBER="+ваш_номер"
export WHATSAPP_PHONE_NUMBER_ID="819213961283826"

# Запустить снова
python check_and_init_whatsapp.py
```

5. **Перезапустить сервис (если нужно):**
   - В Render Dashboard нажмите "Manual Deploy" → "Clear build cache & deploy"
   - Или просто подождите несколько секунд - изменения в БД подхватятся сразу

---

## Verification

После применения исправления, отправьте тестовое сообщение на WhatsApp.

**Ожидаемые логи на Render:**
```
🔄 Processing webhook message...
📱 From: 77051858321
📝 Type: text
🆔 Message ID: wamid...
👤 Creating new customer for 77051858321
✅ Customer created: 77051858321
📞 Creating conversation...
✅ Conversation created
💬 Processing text message...
✅ Message processed successfully
```

**Если всё еще не работает:**
```
🔄 Processing webhook message...
📝 WhatsApp number not found in database, creating: 819213961283826
✅ WhatsApp number auto-created
👤 Creating new customer for 77051858321
...
```

---

## Root Cause

Проблема возникла потому что:
1. Render PostgreSQL база была пустая (новая)
2. `init_bot_templates.py` запускался но не создавал данные (возможно ошибка)
3. Webhook пришёл раньше чем данные были созданы

## Permanent Solution

Новый код содержит:
- ✅ `check_and_init_whatsapp.py` - проверяет и создаёт данные перед стартом
- ✅ Обновлённый `start-render.sh` - запускает проверку при каждом деплое
- ✅ Auto-creation в `whatsapp.py` - создаёт WhatsApp number если не найден

Это гарантирует что данные будут созданы автоматически.

---

## Environment Variables (Optional)

Если хотите использовать реальные данные вместо demo данных:

**Добавить в Render Environment:**
```bash
WHATSAPP_PHONE_NUMBER=+ваш_номер_телефона
WHATSAPP_PHONE_NUMBER_ID=819213961283826
```

**Где взять значения:**
- `WHATSAPP_PHONE_NUMBER`: Ваш номер WhatsApp Business (формат: +77051858321)
- `WHATSAPP_PHONE_NUMBER_ID`: ID из Meta Business (819213961283826 из логов)

**Как добавить:**
1. Render Dashboard → ваш сервис
2. Environment → Add Environment Variable
3. Добавить обе переменные
4. Save Changes
5. Render автоматически передеплоит

---

## Manual WhatsApp Number Creation (Advanced)

Если автоматическое создание не работает, можно создать вручную через Python:

```python
# В Render Shell:
cd backend
python

# В Python интерпретаторе:
from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.models.business import Business

db = SessionLocal()

# Найти business
business = db.query(Business).first()
print(f"Business: {business.name if business else 'NOT FOUND'}")

# Создать WhatsApp number
if business:
    whatsapp = WhatsAppNumber(
        business_id=business.id,
        phone_number='+77051858321',  # ваш номер
        phone_number_id='819213961283826',  # из логов
        display_name='My WhatsApp',
        provider='meta',
        status='connected',
        is_active=True
    )
    db.add(whatsapp)
    db.commit()
    print(f"✅ WhatsApp created: {whatsapp.phone_number}")
else:
    print("❌ No business found - run check_and_init_whatsapp.py first")

db.close()
exit()
```

---

## Check Current Status

Запросить текущее состояние БД:

```python
# В Render Shell:
cd backend
python -c "
from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.models.business import Business
from app.models.user import User

db = SessionLocal()

print('👤 Users:', db.query(User).count())
print('🏢 Businesses:', db.query(Business).count())
print('📱 WhatsApp Numbers:', db.query(WhatsAppNumber).count())

numbers = db.query(WhatsAppNumber).all()
for num in numbers:
    print(f'   • {num.phone_number} (ID: {num.phone_number_id})')

db.close()
"
```

---

## Next Steps After Fix

1. ✅ Убедиться что webhook работает (отправить тестовое сообщение)
2. ✅ Проверить что бот отвечает
3. ✅ Логин в web интерфейс (admin@chatbot.com / admin123)
4. ✅ Добавить реальные данные через UI если нужно
5. ✅ Изменить пароль админа в production

---

## Support

Если проблема не решена:
1. Проверьте логи на Render (последние 100 строк)
2. Убедитесь что DATABASE_URL установлен правильно
3. Проверьте что Render использует PostgreSQL (не SQLite)
4. Убедитесь что деплой завершился успешно

**Полезные команды для диагностики:**
```bash
# В Render Shell:
echo $DATABASE_URL
echo $WHATSAPP_PHONE_NUMBER_ID
cd backend && python check_and_init_whatsapp.py
```
