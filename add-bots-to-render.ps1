# Script to add bot templates to Render database
# Usage: Run this in Render shell or via curl to API

$RENDER_URL = "https://chatbotg-web.onrender.com"

# 1. Login (replace with your credentials)
$loginData = @{
    email = "21ernat@mail.ru"
    password = "YOUR_PASSWORD_HERE"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$RENDER_URL/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = $loginResponse.access_token

Write-Host "[OK] Logged in successfully"

# 2. Create bot via Python script (alternative approach)
# This should be run directly on Render
Write-Host ""
Write-Host "=== To initialize bots on Render, run this command in Render Shell ==="
Write-Host ""
Write-Host "cd /opt/render/project/src/backend && python init_bot_templates.py"
Write-Host ""
Write-Host "Or add this to your start-render.sh script:"
Write-Host "python /opt/render/project/src/backend/init_bot_templates.py || true"
