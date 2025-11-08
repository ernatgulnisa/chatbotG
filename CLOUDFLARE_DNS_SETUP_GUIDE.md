# 🌐 Пошаговая настройка Cloudflare Tunnel и DNS

## Шаг 1: Авторизация в Cloudflare

```powershell
cloudflared tunnel login
```

**Что произойдет:**
1. Откроется браузер с страницей Cloudflare
2. Войдите в аккаунт Cloudflare (или создайте новый бесплатный аккаунт)
3. Выберите домен для туннеля (или добавьте новый)
4. Нажмите "Authorize"

**Если браузер не открылся:**
- Скопируйте URL из терминала
- Вставьте в браузер вручную

**Результат:**
```
You have successfully logged in.
If you wish to copy your credentials to a server, they have been saved to:
C:\Users\UserHome\.cloudflared\cert.pem
```

---

## Шаг 2: Создание туннеля

```powershell
cloudflared tunnel create whatsapp-bot
```

**Что произойдет:**
- Создастся туннель с именем `whatsapp-bot`
- Будет сгенерирован уникальный TUNNEL_ID

**Результат:**
```
Created tunnel whatsapp-bot with id 12345678-1234-1234-1234-123456789abc
```

**⚠️ ВАЖНО: Сохраните этот TUNNEL_ID!**

---

## Шаг 3: Создание конфигурационного файла

Создайте файл: `C:\Users\UserHome\.cloudflared\config.yml`

```yaml
tunnel: 12345678-1234-1234-1234-123456789abc
credentials-file: C:\Users\UserHome\.cloudflared\12345678-1234-1234-1234-123456789abc.json

ingress:
  - hostname: whatsapp-bot.ваш-домен.com
    service: http://localhost:8000
  - service: http_status:404
```

**Замените:**
- `12345678-1234-1234-1234-123456789abc` → ваш TUNNEL_ID из Шага 2
- `ваш-домен.com` → ваш домен в Cloudflare
- `whatsapp-bot` → желаемое имя поддомена

**Примеры доменов:**
- `whatsapp-bot.example.com`
- `bot.mycompany.com`
- `api.mydomain.com`

---

## Шаг 4: Настройка DNS записи

**Автоматический способ (РЕКОМЕНДУЕТСЯ):**

```powershell
cloudflared tunnel route dns whatsapp-bot whatsapp-bot.ваш-домен.com
```

Замените `whatsapp-bot.ваш-домен.com` на ваш реальный домен.

**Результат:**
```
2025-11-08 Created CNAME whatsapp-bot.ваш-домен.com
which will route to this tunnel tunnelID
```

**Что это делает:**
- Автоматически создает CNAME запись в Cloudflare DNS
- Указывает на ваш туннель
- DNS начнет работать через 1-5 минут

**Ручной способ (если автоматический не работает):**

1. Откройте [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Выберите ваш домен
3. Перейдите в DNS → Records
4. Нажмите "Add record"
5. Заполните:
   - **Type:** CNAME
   - **Name:** whatsapp-bot (или другое имя поддомена)
   - **Target:** `TUNNEL_ID.cfargotunnel.com`
   - **Proxy status:** Proxied (оранжевое облако)
6. Сохраните

---

## Шаг 5: Тестирование туннеля

```powershell
cloudflared tunnel run whatsapp-bot
```

**Должно появиться:**
```
INF Connection registered connIndex=0
INF Connection registered connIndex=1
INF Connection registered connIndex=2
INF Connection registered connIndex=3
```

**Проверьте в браузере:**
```
https://whatsapp-bot.ваш-домен.com
```

Если backend запущен, увидите ответ или Swagger UI на `/docs`.

**Остановите тест:** `Ctrl+C`

---

## Шаг 6: Обновление .env файла

Откройте `.env` в корне проекта и добавьте/обновите:

```env
# Cloudflare Tunnel URL
CLOUDFLARE_URL=https://whatsapp-bot.ваш-домен.com
WEBHOOK_URL=https://whatsapp-bot.ваш-домен.com/api/v1/webhooks/whatsapp

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_VERIFY_TOKEN=my_secure_verify_token_12345
```

---

## Шаг 7: Запуск с проектом

Теперь можно использовать скрипт:

```powershell
.\start-with-cloudflare.ps1
```

Или запустить вручную:

**Терминал 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Терминал 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

**Терминал 3 - Cloudflare Tunnel:**
```powershell
cloudflared tunnel run whatsapp-bot
```

---

## Шаг 8: Настройка WhatsApp Webhook (ОДИН РАЗ)

1. Перейдите на [Meta for Developers](https://developers.facebook.com/)
2. Выберите приложение → WhatsApp → Configuration
3. Webhook:
   - **Callback URL:** `https://whatsapp-bot.ваш-домен.com/api/v1/webhooks/whatsapp`
   - **Verify Token:** (из `.env` файла)
4. Нажмите "Verify and Save"
5. Подпишитесь на: `messages`, `message_status`

**✅ ГОТОВО! URL больше не нужно обновлять!**

---

## Бонус: Установка как Windows Service

Чтобы туннель запускался автоматически при старте Windows:

```powershell
# Установить как сервис
cloudflared service install

# Запустить сервис
cloudflared service start

# Проверить статус
Get-Service cloudflared
```

**После этого:**
- Туннель будет работать всегда в фоне
- Не нужно запускать вручную
- Автозапуск при перезагрузке Windows

**Управление сервисом:**
```powershell
# Остановить
cloudflared service stop

# Удалить сервис
cloudflared service uninstall
```

---

## 🔍 Проверка работы

### 1. Проверка DNS

```powershell
nslookup whatsapp-bot.ваш-домен.com
```

Должен вернуть IP адреса Cloudflare.

### 2. Проверка HTTPS

Откройте в браузере:
```
https://whatsapp-bot.ваш-домен.com/docs
```

Должна открыться Swagger документация API.

### 3. Проверка webhook

Отправьте тестовое сообщение на ваш WhatsApp номер.
Проверьте логи backend - должен прийти webhook.

---

## ❓ FAQ

### У меня нет домена в Cloudflare

**Вариант 1: Бесплатные домены**

1. **DuckDNS** (https://www.duckdns.org/)
   - Бесплатные поддомены типа `yourname.duckdns.org`
   - Не требует кредитной карты
   - Работает навсегда

2. **Afraid.org FreeDNS** (https://freedns.afraid.org/)
   - Бесплатные поддомены
   - Много доменов на выбор
   - Бесплатная регистрация

3. **No-IP** (https://www.noip.com/free)
   - Бесплатные hostname
   - До 3 hostname бесплатно
   - Требует подтверждение раз в 30 дней

**Вариант 2: Дешевые домены (.com, .net, .xyz)**
- **Namecheap** (https://www.namecheap.com/) - от $0.99/год
- **Porkbun** (https://porkbun.com/) - от $1/год (.xyz)
- **Cloudflare Registrar** (https://www.cloudflare.com/products/registrar/) - по себестоимости

**Вариант 3: Использовать LocalTunnel (БЕЗ домена)**
- Не требует вообще никакого домена
- Работает сразу из коробки:
  ```powershell
  .\start-with-localtunnel.ps1
  ```

### DNS не резолвится

- Подождите 5-10 минут (DNS кеширование)
- Очистите DNS кеш: `ipconfig /flushdns`
- Проверьте в Cloudflare Dashboard → DNS

### 502 Bad Gateway

- Backend не запущен или не отвечает
- Проверьте: `http://localhost:8000/docs`
- Убедитесь, что в `config.yml` указан правильный порт (8000)

### Туннель не подключается

- Проверьте TUNNEL_ID в `config.yml`
- Убедитесь, что файл `.json` существует в `.cloudflared`
- Переавторизуйтесь: `cloudflared tunnel login`

---

## 📚 Полезные команды

```powershell
# Список всех туннелей
cloudflared tunnel list

# Информация о туннеле
cloudflared tunnel info whatsapp-bot

# Удалить туннель (если нужно переделать)
cloudflared tunnel delete whatsapp-bot

# Удалить DNS запись
cloudflared tunnel route dns whatsapp-bot whatsapp-bot.ваш-домен.com --delete
```

---

**Готово! Теперь у вас есть постоянный URL для WhatsApp бота!** 🎉
