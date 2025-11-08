# 🚇 Custom Tunnel - Туннель на Python (для продвинутых)

## ⚠️ ВНИМАНИЕ

Этот туннель требует наличия сервера с публичным IP.

**Для начинающих рекомендуем:**
- **LocalTunnel** - см. `start-with-localtunnel.ps1` (работает сразу)
- **Cloudflare Tunnel** - см. `CLOUDFLARE_TUNNEL_SETUP.md` (постоянный URL)

---

## Описание

Если у вас есть сервер с публичным IP, можете использовать этот кастомный туннель:

**Преимущества:**
- ✅ Полный контроль над кодом
- ✅ Можно кастомизировать под свои нужды
- ✅ Нет зависимости от сторонних сервисов

**Недостатки:**
- ⚠️ Требует сервер с публичным IP
- ⚠️ Сложнее в настройке

---

## Архитектура

```
WhatsApp API → [Ваш сервер] → WebSocket → [Ваш ПК] → Backend (localhost:8000)
```

## Файлы

- `tunnel_server.py` - Сервер (запускается на сервере с публичным IP)
- `tunnel_client.py` - Клиент (запускается на вашем ПК)
- `requirements.txt` - Зависимости

---

## Требования

- Сервер с публичным IP (ваш собственный или арендованный)
- Python 3.7+
- Открытый порт 8080 на сервере

---

## Установка

### На сервере:

```bash
# Подключиться к серверу
ssh user@your-server-ip

# Установить Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Создать директорию
mkdir tunnel-server
cd tunnel-server

# Скопировать файлы
# Загрузите tunnel_server.py и requirements.txt

# Установить зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запустить сервер
python tunnel_server.py
```

### На вашем ПК (клиент):

```powershell
# Перейти в папку tunnel
cd tunnel

# Создать виртуальное окружение
python -m venv venv
.\venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить клиент (замените на IP вашего сервера)
python tunnel_client.py ws://YOUR-SERVER-IP:8080/ws 8000
```

## Использование

### 1. Запустить сервер:

```bash
cd tunnel-server
source venv/bin/activate
python tunnel_server.py
```

**Вывод:**
```
INFO:__main__:Tunnel Server started on 0.0.0.0:8080
INFO:__main__:Clients connect to: ws://0.0.0.0:8080/ws
```

### 2. Запустить backend локально:

```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 3. Запустить клиент туннеля:

```powershell
cd tunnel
.\venv\Scripts\activate
python tunnel_client.py ws://123.456.789.0:8080/ws 8000
```

**Вывод:**
```
============================================================
🎉 TUNNEL ACTIVE!
📡 Public URL: http://123.456.789.0:8080/a1b2c3d4
🔗 Webhook URL: http://123.456.789.0:8080/a1b2c3d4/api/v1/webhooks/whatsapp
============================================================
```

### 4. Использовать в WhatsApp:

**Webhook URL:** `http://YOUR-SERVER-IP:8080/TUNNEL-ID/api/v1/webhooks/whatsapp`

## Автоматический запуск

### На сервере (как системный сервис):

Создайте файл `/etc/systemd/system/tunnel-server.service`:

```ini
[Unit]
Description=Custom Tunnel Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/tunnel-server
ExecStart=/home/ubuntu/tunnel-server/venv/bin/python tunnel_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Активируйте:
```bash
sudo systemctl enable tunnel-server
sudo systemctl start tunnel-server
sudo systemctl status tunnel-server
```

### На Windows (создать скрипт):

Создайте `start-tunnel-client.ps1`:

```powershell
# Custom Tunnel Client Startup Script

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$serverUrl = "ws://YOUR-SERVER-IP:8080/ws"

Write-Host "Starting Custom Tunnel Client..." -ForegroundColor Green

cd "$scriptPath\tunnel"
& .\venv\Scripts\Activate.ps1
python tunnel_client.py $serverUrl 8000
```

## Добавить HTTPS (SSL)

### На сервере установить Nginx + Let's Encrypt:

```bash
# 1. Установить nginx
sudo apt install nginx certbot python3-certbot-nginx

# 2. Настроить домен
sudo nano /etc/nginx/sites-available/tunnel

# Добавить:
server {
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 3. Активировать
sudo ln -s /etc/nginx/sites-available/tunnel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 4. Получить SSL сертификат
sudo certbot --nginx -d your-domain.com
```

Теперь используйте: `wss://your-domain.com/ws`

## Преимущества

✅ **Полный контроль** - ваш код, ваш сервер
✅ **Бесплатно** - если есть свой сервер
✅ **Можно кастомизировать** - добавить логирование, аутентификацию и т.д.
✅ **Постоянный URL** - если используете домен
✅ **Без ограничений** - нет лимитов на трафик или время работы

## Недостатки

⚠️ Нужен сервер с публичным IP
⚠️ Требует первоначальной настройки
⚠️ Нужно поддерживать самостоятельно

## Альтернативы (проще в использовании)

**LocalTunnel** - не требует сервера, работает сразу:
```powershell
.\start-with-localtunnel.ps1
```

**Cloudflare Tunnel** - постоянный URL, не требует сервера:
```powershell
.\start-with-cloudflare.ps1
```/

## Улучшения (можно добавить)

- [ ] Аутентификация клиентов (токены)
- [ ] Множественные клиенты на одном сервере
- [ ] Web интерфейс для мониторинга
- [ ] Логирование запросов
- [ ] Кастомные поддомены
- [ ] Rate limiting
- [ ] Metrics и статистика

---

**Для большинства пользователей рекомендуем использовать LocalTunnel или Cloudflare Tunnel - они проще в настройке и не требуют собственного сервера.**

