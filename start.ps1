# WhatsApp Bot & CRM Platform - Start Script
# This script starts both Backend and Frontend services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WhatsApp Bot & CRM Platform" -ForegroundColor Green
Write-Host "  Starting Frontend and Backend..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend
Write-Host "[1/2] Starting Backend (FastAPI)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; .\venv\Scripts\activate; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait for backend to initialize
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/2] Starting Frontend (Vite)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ Both services are starting!" -ForegroundColor Green
Write-Host "  🔧 Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  📖 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
