# Работа без удаленного сервера

## Зачем нужен удаленный сервер?

Удаленный сервер нужен потому что у него **публичный IP адрес**, доступный из интернета.

**Проблема:**
```
WhatsApp → ??? → Ваш ПК (за роутером, нет публичного IP)
           ❌ Не может подключиться
```

**С туннелем:**
```
WhatsApp → Туннель → Ваш ПК
          ✅ Работает
```

---

## Рекомендуемые решения:

### 1. LocalTunnel (РЕКОМЕНДУЮ)

**Самый простой способ:**

```powershell
# Установить
npm install -g localtunnel

# Запустить backend
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# В другом терминале - туннель
lt --port 8000 --subdomain mywhatsappbot
```

**Получите:** `https://mywhatsappbot.loca.lt/api/v1/webhooks/whatsapp`

✅ Бесплатно
✅ Работает сразу
✅ Можно выбрать subdomain
⚠️ Иногда нестабильно

---

### 2. Cloudflare Quick Tunnel

```powershell
cloudflared tunnel --url http://localhost:8000
```

✅ Бесплатно
✅ Быстро
⚠️ URL меняется при перезапуске

---

### 3. Ваш ПК как сервер (если есть белый IP)

**Проверить IP:**
```powershell
Invoke-RestMethod -Uri "https://api.ipify.org"
```

Если показало НЕ 192.168.x.x - у вас может быть белый IP!

**Настройка:**

1. **Port Forwarding на роутере:**
   - Зайти в роутер (192.168.1.1)
   - Port Forwarding: 8080 → IP вашего ПК

2. **Firewall:**
   ```powershell
   New-NetFirewallRule -DisplayName "Tunnel" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
   ```

3. **Запустить сервер:**
   ```powershell
   cd tunnel
   python tunnel_server.py
   ```

4. **Использовать:**
   `http://ВАШ_IP:8080/TUNNEL_ID/api/v1/webhooks/whatsapp`

⚠️ Требует белый IP от провайдера
⚠️ ПК должен быть включен 24/7

---

## Быстрый старт с LocalTunnel:

```powershell
npm install -g localtunnel
```

Готово! Используйте скрипт `start-with-localtunnel.ps1` для запуска.
