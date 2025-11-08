# WhatsApp Bot - Quick Start with Cloudflare (NO DOMAIN NEEDED)
# This uses Cloudflare Quick Tunnel - works immediately without DNS setup

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  WhatsApp Bot - Quick Tunnel Mode" -ForegroundColor Green
Write-Host "  No Domain Required!" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if cloudflared exists
$cloudflaredExists = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflaredExists) {
    Write-Host "❌ cloudflared not found" -ForegroundColor Red
    Write-Host "`n   Install it with:" -ForegroundColor Yellow
    Write-Host "   winget install --id Cloudflare.cloudflared" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "⚠️  Quick Tunnel Mode - URL will change on restart" -ForegroundColor Yellow
Write-Host "   For permanent URL, set up a proper tunnel with DNS" -ForegroundColor Gray
Write-Host "   See: CLOUDFLARE_DNS_SETUP_GUIDE.md`n" -ForegroundColor Gray

# Start Backend
Write-Host "[1/3] Starting Backend (FastAPI)..." -ForegroundColor Yellow
$backendCmd = "cd '$scriptPath\backend'; `$env:DATABASE_URL='sqlite:///./chatbot.db'; & .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Wait for backend to initialize
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "[2/3] Starting Frontend (Vite)..." -ForegroundColor Yellow
$frontendCmd = "cd '$scriptPath\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

# Wait a bit
Start-Sleep -Seconds 2

# Start Cloudflare Quick Tunnel
Write-Host "[3/3] Starting Cloudflare Quick Tunnel..." -ForegroundColor Yellow
Write-Host "   Generating public URL (this takes 5-10 seconds)..." -ForegroundColor Gray

$tunnelCmd = "cloudflared tunnel --url http://localhost:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $tunnelCmd

# Wait for tunnel to start
Start-Sleep -Seconds 8

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local URLs:" -ForegroundColor Cyan
Write-Host "  Backend:      http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Public Tunnel:" -ForegroundColor Yellow
Write-Host "  Check the Cloudflare terminal window for your public URL" -ForegroundColor Cyan
Write-Host "  It will look like: https://random-name.trycloudflare.com" -ForegroundColor Gray
Write-Host ""
Write-Host "For WhatsApp Webhook:" -ForegroundColor Yellow
Write-Host "  1. Copy the URL from Cloudflare terminal" -ForegroundColor Gray
Write-Host "  2. Add /api/v1/webhooks/whatsapp to the end" -ForegroundColor Gray
Write-Host "  3. Use in Meta Dashboard" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  NOTE: This URL changes on each restart!" -ForegroundColor Red
Write-Host "   For permanent URL, see CLOUDFLARE_DNS_SETUP_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
