# WhatsApp Bot - Start with Custom Tunnel
# Запускает Backend, Frontend и Custom Tunnel Client

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  WhatsApp Bot - Custom Tunnel" -ForegroundColor Green
Write-Host "  Your Own Tunnel Solution" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Настройки - ИЗМЕНИТЕ НА СВОИ!
$tunnelServerUrl = "ws://YOUR-SERVER-IP:8080/ws"  # <-- ЗАМЕНИТЕ на IP вашего сервера
$localPort = 8000

# Проверка настроек
if ($tunnelServerUrl -eq "ws://YOUR-SERVER-IP:8080/ws") {
    Write-Host "⚠️  ВНИМАНИЕ: Настройте tunnel server URL!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Откройте этот файл и измените:" -ForegroundColor Gray
    Write-Host "   `$tunnelServerUrl = `"ws://ВАШ-СЕРВЕР-IP:8080/ws`"" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Инструкция: tunnel\README.md" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Или используйте LocalTunnel (не требует сервера):" -ForegroundColor Yellow
    Write-Host "   .\start-with-localtunnel.ps1" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Проверка tunnel client
$tunnelClientPath = Join-Path $scriptPath "tunnel\tunnel_client.py"
if (-not (Test-Path $tunnelClientPath)) {
    Write-Host "❌ Tunnel client не найден: $tunnelClientPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Убедитесь, что файлы туннеля на месте:" -ForegroundColor Yellow
    Write-Host "   - tunnel\tunnel_client.py" -ForegroundColor Gray
    Write-Host "   - tunnel\requirements.txt" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

# Start Backend
Write-Host "[1/3] Starting Backend (FastAPI)..." -ForegroundColor Yellow
$backendCmd = "cd '$scriptPath\backend'; `$env:DATABASE_URL='sqlite:///./chatbot.db'; & .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $localPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 5

# Start Frontend
Write-Host "[2/3] Starting Frontend (Vite)..." -ForegroundColor Yellow
$frontendCmd = "cd '$scriptPath\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Start-Sleep -Seconds 2

# Start Tunnel Client
Write-Host "[3/3] Starting Custom Tunnel Client..." -ForegroundColor Yellow
Write-Host "   Connecting to: $tunnelServerUrl" -ForegroundColor Gray

$tunnelCmd = "cd '$scriptPath\tunnel'; & .\venv\Scripts\Activate.ps1; python tunnel_client.py $tunnelServerUrl $localPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $tunnelCmd

Start-Sleep -Seconds 3

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local URLs:" -ForegroundColor Cyan
Write-Host "  Backend:      http://localhost:$localPort" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:$localPort/docs" -ForegroundColor White
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Custom Tunnel:" -ForegroundColor Yellow
Write-Host "  Server:       $tunnelServerUrl" -ForegroundColor Cyan
Write-Host "  Check tunnel window for your public URL!" -ForegroundColor Gray
Write-Host ""
Write-Host "For WhatsApp:" -ForegroundColor Yellow
Write-Host "  Copy URL from tunnel window and add:" -ForegroundColor Gray
Write-Host "  /api/v1/webhooks/whatsapp" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
