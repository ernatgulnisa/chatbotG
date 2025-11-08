# Apply WhatsApp Number Deletion Fix
# This script recreates the database with CASCADE DELETE constraints

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Fix WhatsApp Number Deletion" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "🔍 Проверка базы данных..." -ForegroundColor Yellow

# Check if PostgreSQL is available
$pgAvailable = $false
try {
    $pgProcess = Get-Process -Name "postgres" -ErrorAction SilentlyContinue
    if ($pgProcess) {
        $pgAvailable = $true
        Write-Host "✓ PostgreSQL найден" -ForegroundColor Green
    }
}
catch {}

if (-not $pgAvailable) {
    Write-Host "⚠️  PostgreSQL не найден" -ForegroundColor Yellow
    Write-Host "   Используем SQLite вместо PostgreSQL" -ForegroundColor Cyan
    
    # Use SQLite
    $env:DATABASE_URL = "sqlite:///./chatbot.db"
    
    Write-Host "`n📌 Выбрана база данных: SQLite" -ForegroundColor Green
    Write-Host "   Файл: backend/chatbot.db" -ForegroundColor Gray
}

# Navigate to backend
Set-Location -Path "backend" -ErrorAction Stop

Write-Host "`n⚠️  ВНИМАНИЕ!" -ForegroundColor Red
Write-Host "   Это пересоздаст базу данных." -ForegroundColor Yellow
Write-Host "   Все текущие данные будут удалены!" -ForegroundColor Yellow

$continue = Read-Host "`nПродолжить? (yes/no)"

if ($continue -ne "yes") {
    Write-Host "`n❌ Отменено пользователем" -ForegroundColor Red
    Set-Location -Path ".."
    exit 1
}

Write-Host "`n🔧 Пересоздание базы данных..." -ForegroundColor Yellow

# Create a temporary input file for automatic confirmation
$inputFile = "temp_input.txt"
"yes" | Out-File -FilePath $inputFile -Encoding ASCII

# Run init_db.py with automatic confirmation
Get-Content $inputFile | python init_db.py --force

Remove-Item $inputFile -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ База данных успешно пересоздана!" -ForegroundColor Green
    
    Write-Host "`n🎯 Что изменилось:" -ForegroundColor Cyan
    Write-Host "   • Добавлено каскадное удаление (CASCADE DELETE)" -ForegroundColor Gray
    Write-Host "   • Теперь можно удалять номера WhatsApp" -ForegroundColor Gray
    Write-Host "   • При удалении номера автоматически удалятся:" -ForegroundColor Gray
    Write-Host "     - Все боты этого номера" -ForegroundColor DarkGray
    Write-Host "     - Все разговоры через этот номер" -ForegroundColor DarkGray
    Write-Host "     - Все рассылки с этого номера" -ForegroundColor DarkGray
    
    Write-Host "`n💡 Следующие шаги:" -ForegroundColor Cyan
    Write-Host "   1. Запустите сервер: cd .. && .\start.ps1" -ForegroundColor Gray
    Write-Host "   2. Откройте http://localhost:3001/whatsapp" -ForegroundColor Gray
    Write-Host "   3. Добавьте номера WhatsApp" -ForegroundColor Gray
    Write-Host "   4. Попробуйте удалить номер - теперь это работает!" -ForegroundColor Gray
    
}
else {
    Write-Host "`n❌ Ошибка при пересоздании базы данных!" -ForegroundColor Red
    Write-Host "   Проверьте сообщения об ошибках выше" -ForegroundColor Yellow
}

# Return to root
Set-Location -Path ".."

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
