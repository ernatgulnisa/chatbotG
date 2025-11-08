# Stop all services (Backend, Frontend, LocalTunnel)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Stopping All Services" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "🛑 Stopping processes..." -ForegroundColor Yellow

# Stop Backend (uvicorn/python)
Write-Host "  - Stopping Backend (Python/uvicorn)..." -ForegroundColor Gray
Stop-Process -Name "python", "uvicorn" -Force -ErrorAction SilentlyContinue

# Stop Frontend (Node/Vite)
Write-Host "  - Stopping Frontend (Node)..." -ForegroundColor Gray
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue

# Stop LocalTunnel (Node process)
Write-Host "  - Stopping LocalTunnel..." -ForegroundColor Gray
Get-Process | Where-Object { $_.ProcessName -eq "node" -and $_.CommandLine -like "*localtunnel*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "`n✅ All services stopped!" -ForegroundColor Green
Write-Host ""
