# Cloud PostgreSQL Database Setup
# No Docker or local PostgreSQL installation required

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cloud PostgreSQL (Free)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Choose cloud database provider:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Supabase (Recommended)" -ForegroundColor Green
Write-Host "   - Free forever" -ForegroundColor Gray
Write-Host "   - 500MB storage" -ForegroundColor Gray
Write-Host "   - Automatic backups" -ForegroundColor Gray
Write-Host "   - https://supabase.com/" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. Render.com" -ForegroundColor Green
Write-Host "   - Free for 90 days" -ForegroundColor Gray
Write-Host "   - 1GB storage" -ForegroundColor Gray
Write-Host "   - https://render.com/" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Railway.app" -ForegroundColor Green
Write-Host "   - $5 free/month" -ForegroundColor Gray
Write-Host "   - Auto-scaling" -ForegroundColor Gray
Write-Host "   - https://railway.app/" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter number (1-3) or press Enter to skip"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Supabase Setup:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Open: https://supabase.com/" -ForegroundColor White
        Write-Host "2. Sign Up (via GitHub)" -ForegroundColor White
        Write-Host "3. New Project - Name: chatbot" -ForegroundColor White
        Write-Host "4. Choose region: Europe (Frankfurt)" -ForegroundColor White
        Write-Host "5. Create password (save it!)" -ForegroundColor White
        Write-Host "6. Click Create Project" -ForegroundColor White
        Write-Host ""
        Write-Host "7. After creation: Settings -> Database" -ForegroundColor Yellow
        Write-Host "8. Copy Connection String (URI)" -ForegroundColor Yellow
        Write-Host "9. Format: postgresql://postgres:[YOUR-PASSWORD]@..." -ForegroundColor Gray
        Write-Host ""
        Start-Process "https://supabase.com/dashboard"
    }
    "2" {
        Write-Host ""
        Write-Host "Render.com Setup:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Open: https://dashboard.render.com/" -ForegroundColor White
        Write-Host "2. Sign Up (via GitHub)" -ForegroundColor White
        Write-Host "3. New -> PostgreSQL" -ForegroundColor White
        Write-Host "4. Name: chatbot-db" -ForegroundColor White
        Write-Host "5. Database: chatbot_db" -ForegroundColor White
        Write-Host "6. User: chatbot_user" -ForegroundColor White
        Write-Host "7. Region: Frankfurt" -ForegroundColor White
        Write-Host "8. Plan: Free" -ForegroundColor White
        Write-Host "9. Create Database" -ForegroundColor White
        Write-Host ""
        Write-Host "10. Copy External Database URL" -ForegroundColor Yellow
        Write-Host "11. Format: postgresql://user:pass@hostname:5432/db" -ForegroundColor Gray
        Write-Host ""
        Start-Process "https://dashboard.render.com/select-repo?type=pserv"
    }
    "3" {
        Write-Host ""
        Write-Host "Railway.app Setup:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Open: https://railway.app/" -ForegroundColor White
        Write-Host "2. Login with GitHub" -ForegroundColor White
        Write-Host "3. New Project -> Deploy PostgreSQL" -ForegroundColor White
        Write-Host "4. After creation: Variables -> DATABASE_URL" -ForegroundColor White
        Write-Host "5. Copy the value" -ForegroundColor White
        Write-Host ""
        Start-Process "https://railway.app/new"
    }
    default {
        Write-Host ""
        Write-Host "Instructions available in POSTGRESQL_MIGRATION.md" -ForegroundColor Cyan
        exit 0
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "After getting DATABASE_URL:" -ForegroundColor Yellow
Write-Host ""

$dbUrl = Read-Host "Paste DATABASE_URL (or press Enter to skip)"

if ($dbUrl) {
    Write-Host ""
    Write-Host "Updating .env file..." -ForegroundColor Cyan
    
    $envPath = ".\backend\.env"
    
    if (Test-Path $envPath) {
        $envContent = Get-Content $envPath -Raw
        
        # Update DATABASE_URL
        if ($envContent -match "DATABASE_URL=.*") {
            $envContent = $envContent -replace "DATABASE_URL=.*", "DATABASE_URL=$dbUrl"
        } else {
            $envContent += "`nDATABASE_URL=$dbUrl`n"
        }
        
        Set-Content $envPath -Value $envContent
        
        Write-Host "Done! .env updated" -ForegroundColor Green
    } else {
        Write-Host "Warning: .env file not found" -ForegroundColor Yellow
        Write-Host "Create backend/.env with:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "DATABASE_URL=$dbUrl" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Testing connection..." -ForegroundColor Cyan
    
    $testScript = @"
import sys
try:
    from sqlalchemy import create_engine
    engine = create_engine('$dbUrl')
    conn = engine.connect()
    print('SUCCESS: Connected to PostgreSQL!')
    conn.close()
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"@
    
    $testScript | & "C:/Program Files/Python311/python.exe" -
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  Next Steps:" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Apply migrations:" -ForegroundColor Yellow
        Write-Host "   cd backend" -ForegroundColor White
        Write-Host "   python -m alembic upgrade head" -ForegroundColor White
        Write-Host ""
        Write-Host "2. Create initial data:" -ForegroundColor Yellow
        Write-Host "   python init_db.py" -ForegroundColor White
        Write-Host ""
        Write-Host "3. Start application:" -ForegroundColor Yellow
        Write-Host "   python -m uvicorn app.main:app --reload" -ForegroundColor White
        Write-Host ""
    }
} else {
    Write-Host ""
    Write-Host "After getting DATABASE_URL:" -ForegroundColor Cyan
    Write-Host "1. Update backend/.env" -ForegroundColor White
    Write-Host "2. Apply migrations: python -m alembic upgrade head" -ForegroundColor White
    Write-Host "3. Start app: python -m uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host ""
}

Write-Host "Full documentation: POSTGRESQL_MIGRATION.md" -ForegroundColor Cyan
Write-Host ""
