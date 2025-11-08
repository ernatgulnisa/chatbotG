# Quick Test - Webhook Auto-Configuration
# Demonstrates auto-fetching LocalTunnel URL

Write-Host "`n🧪 Testing Webhook Auto-Configuration`n" -ForegroundColor Cyan

$envFilePath = ".env"

Write-Host "Checking LocalTunnel configuration..." -ForegroundColor Yellow

# Read .env file to get webhook URL
if (Test-Path $envFilePath) {
    $envContent = Get-Content $envFilePath -Raw
    
    if ($envContent -match "WEBHOOK_URL=(.+)") {
        $webhookUrl = $matches[1].Trim()
        
        Write-Host "✅ Webhook configuration found!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Webhook URL:   $webhookUrl" -ForegroundColor Cyan
        Write-Host "Verify Token:  my_secure_verify_token_12345" -ForegroundColor Cyan
        Write-Host ""
        
        # Copy to clipboard
        Set-Clipboard -Value $webhookUrl
        Write-Host "✅ Webhook URL copied to clipboard!" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now paste it directly into Meta Dashboard!" -ForegroundColor Yellow
    }
    else {
        Write-Host "⚠️  No WEBHOOK_URL found in .env file" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To start with LocalTunnel, run:" -ForegroundColor Yellow
        Write-Host "   .\start-with-localtunnel.ps1" -ForegroundColor Cyan
    }
}
else {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start with LocalTunnel, run:" -ForegroundColor Yellow
    Write-Host "   .\start-with-localtunnel.ps1" -ForegroundColor Cyan
}

Write-Host ""
