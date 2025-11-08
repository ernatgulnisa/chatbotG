# Cloudflare Tunnel Setup - Постоянный URL для WhatsApp Webhook

## Преимущества Cloudflare Tunnel
✅ **Бесплатно навсегда**
✅ **Постоянный URL** (не меняется при перезапусках)
✅ **Безопасно** (без открытия портов)
✅ **Быстро** (CDN Cloudflare)
✅ **Надежно** (99.9% uptime)

## Шаг 1: Установка cloudflared

### Windows (PowerShell):
```powershell
# Скачать cloudflared для Windows
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "$env:USERPROFILE\cloudflared.exe"

# Переместить в Program Files
Move-Item "$env:USERPROFILE\cloudflared.exe" "C:\Program Files\cloudflared.exe" -Force

# Проверить установку
& "C:\Program Files\cloudflared.exe" --version
```

### Альтернативно через winget:
```powershell
winget install --id Cloudflare.cloudflared
```

## Шаг 2: Авторизация в Cloudflare

```powershell
# Запустить авторизацию (откроется браузер)
& "C:\Program Files\cloudflared.exe" tunnel login
```

Это откроет браузер:
1. Войдите в аккаунт Cloudflare (или создайте бесплатный)
2. Выберите домен (или создайте новый на Cloudflare)
3. Разрешите доступ

## Шаг 3: Создание туннеля

```powershell
# Создать туннель с именем (например: whatsapp-bot)
& "C:\Program Files\cloudflared.exe" tunnel create whatsapp-bot
```

Запомните **TUNNEL_ID** из вывода команды!

## Шаг 4: Настройка конфигурации

Создайте файл: `C:\Users\[ВАШ_ПОЛЬЗОВАТЕЛЬ]\.cloudflared\config.yml`

```yaml
tunnel: TUNNEL_ID_ИЗ_ПРЕДЫДУЩЕГО_ШАГА
credentials-file: C:\Users\[ВАШ_ПОЛЬЗОВАТЕЛЬ]\.cloudflared\TUNNEL_ID.json

ingress:
  - hostname: ваш-бот.ваш-домен.com
    service: http://localhost:8000
  - service: http_status:404
```

**Замените:**
- `TUNNEL_ID_ИЗ_ПРЕДЫДУЩЕГО_ШАГА` на ваш ID туннеля
- `[ВАШ_ПОЛЬЗОВАТЕЛЬ]` на ваше имя пользователя Windows
- `ваш-бот.ваш-домен.com` на желаемое имя поддомена

## Шаг 5: Настройка DNS

```powershell
# Создать DNS запись для туннеля
& "C:\Program Files\cloudflared.exe" tunnel route dns whatsapp-bot ваш-бот.ваш-домен.com
```

## Шаг 6: Запуск туннеля

### Тестовый запуск:
```powershell
& "C:\Program Files\cloudflared.exe" tunnel run whatsapp-bot
```

### Установка как Windows Service (запуск при старте системы):
```powershell
# Установить сервис
& "C:\Program Files\cloudflared.exe" service install

# Запустить сервис
& "C:\Program Files\cloudflared.exe" service start
```

## Шаг 7: Обновление .env файла

Обновите `.env` в корне проекта:

```env
# Cloudflare Tunnel URL
CLOUDFLARE_URL=https://ваш-бот.ваш-домен.com
WEBHOOK_URL=https://ваш-бот.ваш-домен.com/api/v1/webhooks/whatsapp

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_VERIFY_TOKEN=my_secure_verify_token_12345
```

## Шаг 8: Настройка WhatsApp Webhook

1. Перейдите в [Meta for Developers](https://developers.facebook.com/)
2. Выберите ваше приложение
3. WhatsApp > Configuration
4. Webhook:
   - **Callback URL**: `https://ваш-бот.ваш-домен.com/api/v1/webhooks/whatsapp`
   - **Verify Token**: `my_secure_verify_token_12345`
5. Нажмите "Verify and Save"

## Полезные команды

```powershell
# Список всех туннелей
& "C:\Program Files\cloudflared.exe" tunnel list

# Информация о туннеле
& "C:\Program Files\cloudflared.exe" tunnel info whatsapp-bot

# Остановить сервис
& "C:\Program Files\cloudflared.exe" service stop

# Удалить туннель (если нужно)
& "C:\Program Files\cloudflared.exe" tunnel delete whatsapp-bot
```

## Автоматический запуск с Cloudflare

Используйте скрипт:
```powershell
.\start-with-cloudflare.ps1
```

## Troubleshooting

### Туннель не запускается
- Проверьте `config.yml` на ошибки
- Убедитесь, что backend работает на порту 8000
- Проверьте логи: `& "C:\Program Files\cloudflared.exe" tunnel run whatsapp-bot`

### DNS не резолвится
- Подождите 5-10 минут (DNS кеширование)
- Проверьте DNS записи на Cloudflare Dashboard

### 502 Bad Gateway
- Backend не запущен или не отвечает
- Проверьте порт в `config.yml` (должен быть 8000)

## Преимущества Cloudflare Tunnel

| Параметр | Cloudflare Tunnel | LocalTunnel |
|----------|-------------------|-------------|
| Цена | Бесплатно | Бесплатно |
| Постоянный URL | ✅ Да | ⚠️ Может меняться |
| Кастомный домен | ✅ Да | ❌ Нет |
| Скорость | ✅ CDN | ⚠️ Обычная |
| Windows Service | ✅ Да | ❌ Нет |

---

**Готово!** Теперь у вас есть постоянный URL, который не меняется при перезапусках.
