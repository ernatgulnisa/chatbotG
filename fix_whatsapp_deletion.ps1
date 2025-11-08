# Fix WhatsApp Number Deletion Script
# This script applies CASCADE DELETE migration to allow WhatsApp number deletion

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Fix WhatsApp Number Deletion Issue" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if PostgreSQL is running
Write-Host "🔍 Checking PostgreSQL status..." -ForegroundColor Yellow
$pgProcess = Get-Process -Name "postgres" -ErrorAction SilentlyContinue

if (-not $pgProcess) {
    Write-Host "❌ PostgreSQL is not running!" -ForegroundColor Red
    Write-Host "   Please start PostgreSQL first." -ForegroundColor Yellow
    Write-Host "   You can start it using Docker:" -ForegroundColor Yellow
    Write-Host "   docker-compose up -d db" -ForegroundColor Cyan
    exit 1
}

Write-Host "✓ PostgreSQL is running" -ForegroundColor Green

# Navigate to backend directory
Set-Location -Path "backend"

Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
pip install -q sqlalchemy psycopg2-binary alembic 2>$null

Write-Host "`n🔧 Applying CASCADE DELETE migration..." -ForegroundColor Yellow
python apply_cascade_migration.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Migration applied successfully!" -ForegroundColor Green
    Write-Host "`n🎉 WhatsApp numbers can now be deleted!" -ForegroundColor Green
    Write-Host "   All related data (bots, conversations, broadcasts) will be automatically removed." -ForegroundColor Gray
    
    Write-Host "`n💡 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Restart the backend server" -ForegroundColor Gray
    Write-Host "   2. Try deleting a WhatsApp number from the UI" -ForegroundColor Gray
}
else {
    Write-Host "`n❌ Migration failed!" -ForegroundColor Red
    Write-Host "   Please check the error messages above." -ForegroundColor Yellow
}

# Return to root directory
Set-Location -Path ".."

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
