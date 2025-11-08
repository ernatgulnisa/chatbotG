# ⚡ Быстрая настройка Cloudflare Tunnel - Пошаговая инструкция

## Вариант 1: У вас НЕТ домена (Бесплатное решение)

### Используйте бесплатный DNS от Cloudflare

1. **Зарегистрируйте бесплатный домен на:**
   - https://www.freenom.com/ (домены .tk, .ml, .ga, .cf - бесплатно)
   - https://freedns.afraid.org/ (бесплатные поддомены)
   
2. **ИЛИ используйте встроенные возможности Cloudflare:**
   - Cloudflare предоставляет временный домен типа `*.trycloudflare.com`
   - Можно использовать без регистрации домена!

### Самый простой способ - Quick Tunnel (БЕЗ домена):

```powershell
cloudflared tunnel --url http://localhost:8000
```

**Что это делает:**
- Создает временный публичный URL типа `https://random-name.trycloudflare.com`
- Работает сразу без настройки DNS
- URL меняется при каждом запуске (временный URL)

**Для WhatsApp:**
- Скопируйте полученный URL
- Webhook: `https://random-name.trycloudflare.com/api/v1/webhooks/whatsapp`

---

## Вариант 2: У вас ЕСТЬ домен

### Шаг 1: Добавьте домен в Cloudflare

1. Откройте https://dash.cloudflare.com/
2. Нажмите "Add a Site"
3. Введите ваш домен (например: example.com)
4. Выберите план "Free"
5. Cloudflare покажет NS серверы:
   ```
   NS1: emily.ns.cloudflare.com
   NS2: steve.ns.cloudflare.com
   ```
6. Зайдите к вашему регистратору домена (где покупали)
7. Измените NS серверы на те, что показал Cloudflare
8. Подождите 1-24 часа (обычно 15-30 минут)

### Шаг 2: Авторизация cloudflared

```powershell
cloudflared tunnel login
```

- Откроется браузер
- Выберите ваш домен
- Нажмите "Authorize"

### Шаг 3: Создание туннеля

```powershell
cloudflared tunnel create whatsapp-bot
```

**Сохраните TUNNEL_ID из вывода!**

### Шаг 4: Создание config.yml

Создайте файл: `C:\Users\UserHome\.cloudflared\config.yml`

```yaml
tunnel: ВАШ_TUNNEL_ID_ЗДЕСЬ
credentials-file: C:\Users\UserHome\.cloudflared\ВАШ_TUNNEL_ID_ЗДЕСЬ.json

ingress:
  - hostname: bot.ваш-домен.com
    service: http://localhost:8000
  - service: http_status:404
```

### Шаг 5: Настройка DNS

```powershell
cloudflared tunnel route dns whatsapp-bot bot.ваш-домен.com
```

### Шаг 6: Запуск

```powershell
cloudflared tunnel run whatsapp-bot
```

---

## ⚡ РЕКОМЕНДАЦИЯ: Используйте Quick Tunnel для начала

Если вам просто нужно начать работать прямо сейчас:

### 1. Создайте скрипт быстрого запуска

Создам для вас автоматический скрипт...

