# ⚡ Railway Quick Start - 5 минут до деплоя

## Шаг 1: Подготовка (30 сек)

```powershell
# Убедитесь что код на GitHub
git init
git add .
git commit -m "Ready for Railway deployment"
git remote add origin https://github.com/your-username/chatbotG.git
git push -u origin main
```

## Шаг 2: Railway Setup (2 мин)

1. Откройте https://railway.app/
2. **Login with GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. Выберите репозиторий `chatbotG`
5. Railway начнет автодеплой

## Шаг 3: Добавить PostgreSQL (30 сек)

1. В проекте нажмите **+ New**
2. **Database** → **Add PostgreSQL**
3. Railway автоматически создаст `DATABASE_URL`

## Шаг 4: Переменные окружения (1 мин)

В разделе **Variables** добавьте:

```bash
# Сгенерировать ключи:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Скопируйте результат в:
- `SECRET_KEY`
- `ENCRYPTION_KEY`

Добавьте остальные:
```env
ENVIRONMENT=production
WHATSAPP_VERIFY_TOKEN=your-token
WHATSAPP_APP_SECRET=your-meta-secret
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
```

## Шаг 5: Получить URL (30 сек)

1. **Settings** → **Domains** → **Generate Domain**
2. Скопируйте: `https://your-project.up.railway.app`
3. Добавьте в Variables:
   ```
   WEBHOOK_URL=https://your-project.up.railway.app/api/v1/webhooks/whatsapp
   ALLOWED_ORIGINS=https://your-project.up.railway.app
   ```

## Шаг 6: Настроить Meta Webhook (30 сек)

1. https://developers.facebook.com/apps/
2. WhatsApp → Configuration → Webhook
3. **Callback URL:** `https://your-project.up.railway.app/api/v1/webhooks/whatsapp`
4. **Verify Token:** (ваш `WHATSAPP_VERIFY_TOKEN`)
5. Subscribe: `messages`, `message_status`

## ✅ Готово!

Проверьте:
```bash
# Тест API
curl https://your-project.up.railway.app/health

# Отправьте сообщение на WhatsApp
# Бот должен ответить автоматически
```

## 📊 Мониторинг

- **Логи:** Railway Dashboard → Deployments → View Logs
- **Метрики:** Railway Dashboard → Metrics
- **БД:** Railway Dashboard → PostgreSQL → Connect

## 🔄 Автодеплой

После настройки каждый `git push` автоматически деплоит:

```bash
git add .
git commit -m "Update bot"
git push
# Railway автоматически задеплоит за 1-2 минуты
```

## 💰 Лимиты

- **500 часов/месяц** бесплатно (~20 дней)
- Для 24/7: **Starter Plan $5/мес**

## 📚 Полная документация

[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
