# WhatsApp Bot - Start with LocalTunnel
# Запускает Backend, Frontend и LocalTunnel (БЕЗ VPS!)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  WhatsApp Bot & CRM Platform" -ForegroundColor Green
Write-Host "  LocalTunnel Edition (No VPS)" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Настройки
$localPort = 8000
$subdomain = "whatsappbot-$(Get-Random -Minimum 1000 -Maximum 9999)"  # Случайный subdomain

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Local Port:    $localPort" -ForegroundColor Gray
Write-Host "  Subdomain:     $subdomain" -ForegroundColor Gray
Write-Host ""

# Проверка LocalTunnel
$ltInstalled = Get-Command lt -ErrorAction SilentlyContinue
if (-not $ltInstalled) {
    Write-Host "❌ LocalTunnel not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Installing LocalTunnel..." -ForegroundColor Yellow
    npm install -g localtunnel
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "   Failed to install. Please run manually:" -ForegroundColor Red
        Write-Host "   npm install -g localtunnel" -ForegroundColor Gray
        Write-Host ""
        exit 1
    }
    Write-Host "   ✅ LocalTunnel installed!" -ForegroundColor Green
    Write-Host ""
}

# Start Backend
Write-Host "[1/3] Starting Backend (FastAPI)..." -ForegroundColor Yellow
$backendCmd = "cd '$scriptPath\backend'; `$env:DATABASE_URL='sqlite:///./chatbot.db'; & .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $localPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Wait for backend to initialize
Write-Host "   Waiting for backend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "[2/3] Starting Frontend (Vite)..." -ForegroundColor Yellow
$frontendCmd = "cd '$scriptPath\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

# Wait a bit
Start-Sleep -Seconds 2

# Start LocalTunnel
Write-Host "[3/3] Starting LocalTunnel..." -ForegroundColor Yellow
Write-Host "   Creating tunnel to port $localPort..." -ForegroundColor Gray

$tunnelCmd = "lt --port $localPort --subdomain $subdomain"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $tunnelCmd

# Wait for tunnel to establish
Write-Host "   Waiting for tunnel to connect..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Calculate URLs
$publicUrl = "https://$subdomain.loca.lt"
$webhookUrl = "$publicUrl/api/v1/webhooks/whatsapp"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  All Services Running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local URLs:" -ForegroundColor Cyan
Write-Host "  Backend:      http://localhost:$localPort" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:$localPort/docs" -ForegroundColor White
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Public Tunnel (LocalTunnel):" -ForegroundColor Yellow
Write-Host "  Public URL:    $publicUrl" -ForegroundColor Cyan
Write-Host "  Webhook URL:   $webhookUrl" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  First Visit Warning:" -ForegroundColor Yellow
Write-Host "   LocalTunnel may show a warning page on first visit" -ForegroundColor Gray
Write-Host "   Click 'Continue' to proceed" -ForegroundColor Gray
Write-Host ""
Write-Host "WhatsApp Configuration:" -ForegroundColor Yellow
Write-Host "  1. Go to Meta for Developers" -ForegroundColor Gray
Write-Host "  2. WhatsApp → Configuration → Webhook" -ForegroundColor Gray
Write-Host "  3. Callback URL:  $webhookUrl" -ForegroundColor Cyan
Write-Host "  4. Verify Token:  (from your .env file)" -ForegroundColor Gray
Write-Host "  5. Click 'Verify and Save'" -ForegroundColor Gray
Write-Host ""

# Copy webhook URL to clipboard
try {
    Set-Clipboard -Value $webhookUrl
    Write-Host "✅ Webhook URL copied to clipboard!" -ForegroundColor Green
}
catch {
    # Clipboard might not be available
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   - Tunnel URL is valid while this script runs" -ForegroundColor Gray
Write-Host "   - Subdomain may change if taken by someone else" -ForegroundColor Gray
Write-Host "   - For permanent URL, see CLOUDFLARE_TUNNEL_SETUP.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to close this window (services will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
