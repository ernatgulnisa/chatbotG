# 🔧 Настройка переменных окружения на Render

## Шаг 1: Откройте настройки

1. Перейдите на https://dashboard.render.com
2. Откройте ваш сервис **chatbotg-web**
3. Нажмите **Environment** в левом меню

## Шаг 2: Добавьте переменные

Нажмите **Add Environment Variable** и добавьте:

### Переменная 1: WhatsApp Phone Number ID
```
Key:   WHATSAPP_PHONE_NUMBER_ID
Value: 819213961283826
```

### Переменная 2: WhatsApp Phone Number (опционально)
```
Key:   WHATSAPP_PHONE_NUMBER
Value: +77051858321
```

> **Где взять эти значения?**
> - `WHATSAPP_PHONE_NUMBER_ID`: из логов Render (`819213961283826`)
> - `WHATSAPP_PHONE_NUMBER`: ваш номер WhatsApp Business

## Шаг 3: Сохраните

1. Нажмите **Save Changes**
2. Render автоматически передеплоит сервис (2-3 минуты)

## Шаг 4: Проверьте результат

После передеплоя в логах должно появиться:

```
📱 Checking WhatsApp configuration...
============================================================
  Checking Database
============================================================
📱 WhatsApp Numbers: 1

🔄 Updating WhatsApp number with environment variables...
   Old ID: demo_phone_id
   New ID: 819213961283826
   New Phone: +77051858321
✅ WhatsApp number updated successfully!
============================================================
```

## Шаг 5: Тест

Отправьте сообщение на WhatsApp. Логи должны показать:

```
🔄 Processing webhook message...
📱 From: 77051858321
👤 Creating new customer for 77051858321
✅ Customer created
✅ Message processed successfully
```

Без ошибки ❌ WhatsApp number not found!

---

## Альтернатива: Ручное обновление через Shell

Если не хотите ждать передеплоя, обновите через Shell:

```bash
cd backend
python -c "
from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber

db = SessionLocal()
whatsapp = db.query(WhatsAppNumber).first()

if whatsapp:
    whatsapp.phone_number_id = '819213961283826'
    whatsapp.phone_number = '+77051858321'
    whatsapp.display_name = 'My WhatsApp Business'
    db.commit()
    print('✅ Updated successfully!')

db.close()
"
```

Это сработает сразу, но при следующем деплое переменные окружения всё равно лучше добавить.
