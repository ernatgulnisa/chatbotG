# WhatsApp Bot & CRM Platform - Cloudflare Tunnel Startup
# This script starts Backend, Frontend with Cloudflare Tunnel (permanent URL)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  WhatsApp Bot & CRM Platform" -ForegroundColor Green
Write-Host "  Cloudflare Tunnel Edition" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$cloudflaredPath = "C:\Program Files\cloudflared.exe"
$envFilePath = Join-Path $scriptPath ".env"

# Check if cloudflared exists
if (-not (Test-Path $cloudflaredPath)) {
    Write-Host "❌ cloudflared not found at: $cloudflaredPath" -ForegroundColor Red
    Write-Host "`n   Please install cloudflared first:" -ForegroundColor Yellow
    Write-Host "   1. Run: winget install --id Cloudflare.cloudflared" -ForegroundColor Gray
    Write-Host "   OR" -ForegroundColor Gray
    Write-Host "   2. See CLOUDFLARE_TUNNEL_SETUP.md for manual installation" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

# Check if tunnel is configured
$configPath = "$env:USERPROFILE\.cloudflared\config.yml"
if (-not (Test-Path $configPath)) {
    Write-Host "❌ Cloudflare Tunnel not configured" -ForegroundColor Red
    Write-Host "`n   Please follow setup instructions:" -ForegroundColor Yellow
    Write-Host "   1. Open CLOUDFLARE_TUNNEL_SETUP.md" -ForegroundColor Gray
    Write-Host "   2. Complete Steps 2-5 (tunnel creation and configuration)" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

# Read config to get hostname
$configContent = Get-Content $configPath -Raw
if ($configContent -match "hostname:\s*(\S+)") {
    $hostname = $matches[1]
    $cloudflareUrl = "https://$hostname"
    $webhookUrl = "$cloudflareUrl/api/v1/webhooks/whatsapp"
}
else {
    Write-Host "⚠️  Could not read hostname from config.yml" -ForegroundColor Yellow
    Write-Host "   Using default from .env file" -ForegroundColor Gray
    
    # Try to read from .env
    if (Test-Path $envFilePath) {
        $envContent = Get-Content $envFilePath -Raw
        if ($envContent -match "CLOUDFLARE_URL=(.+)") {
            $cloudflareUrl = $matches[1].Trim()
            $webhookUrl = "$cloudflareUrl/api/v1/webhooks/whatsapp"
        }
    }
}

# Function to update .env file
function Update-EnvVariable {
    param (
        [string]$Key,
        [string]$Value
    )
    
    if (-not (Test-Path $envFilePath)) {
        Write-Host "⚠️  .env file not found, creating..." -ForegroundColor Yellow
        New-Item -Path $envFilePath -ItemType File -Force | Out-Null
    }
    
    $envContent = Get-Content $envFilePath -Raw -ErrorAction SilentlyContinue
    
    if ($null -eq $envContent) {
        $envContent = ""
    }
    
    # Check if key exists
    if ($envContent -match "(?m)^$Key=.*$") {
        # Update existing key
        $envContent = $envContent -replace "(?m)^$Key=.*$", "$Key=$Value"
    }
    else {
        # Add new key
        if ($envContent -and -not $envContent.EndsWith("`n")) {
            $envContent += "`n"
        }
        $envContent += "$Key=$Value`n"
    }
    
    Set-Content -Path $envFilePath -Value $envContent -NoNewline
}

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

# Check if cloudflared is already running as service
$serviceRunning = $false
try {
    $service = Get-Service -Name "cloudflared" -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq "Running") {
        $serviceRunning = $true
        Write-Host "[3/3] Cloudflare Tunnel already running as service ✅" -ForegroundColor Green
    }
}
catch {
    $serviceRunning = $false
}

# Start Cloudflare Tunnel if not running as service
if (-not $serviceRunning) {
    Write-Host "[3/3] Starting Cloudflare Tunnel..." -ForegroundColor Yellow
    
    # Get tunnel name from config
    $tunnelName = "whatsapp-bot"
    if ($configContent -match "tunnel:\s*(\S+)") {
        $tunnelId = $matches[1]
        
        # Try to get tunnel name from list
        try {
            $tunnelList = & $cloudflaredPath tunnel list 2>$null
            if ($tunnelList -match "(\S+)\s+$tunnelId") {
                $tunnelName = $matches[1]
            }
        }
        catch {
            # Use default name
        }
    }
    
    $cloudflareCmd = "& '$cloudflaredPath' tunnel run $tunnelName"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cloudflareCmd
    
    Write-Host "   Waiting for tunnel to initialize..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

# Update .env file if we have URLs
if ($cloudflareUrl) {
    Update-EnvVariable -Key "CLOUDFLARE_URL" -Value $cloudflareUrl
    Update-EnvVariable -Key "WEBHOOK_URL" -Value $webhookUrl
    Write-Host "✅ .env file updated with Cloudflare URLs" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  All services are running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Backend:      http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

if ($cloudflareUrl) {
    Write-Host "Cloudflare Tunnel (PERMANENT URL):" -ForegroundColor Yellow
    Write-Host "  Public URL:    $cloudflareUrl" -ForegroundColor Cyan
    Write-Host "  Webhook URL:   $webhookUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "WhatsApp Configuration:" -ForegroundColor Yellow
    Write-Host "  Webhook URL:   $webhookUrl" -ForegroundColor Green
    Write-Host "  Verify Token:  my_secure_verify_token_12345" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ This URL is PERMANENT and won't change!" -ForegroundColor Green
    
    # Copy webhook URL to clipboard
    try {
        Set-Clipboard -Value $webhookUrl
        Write-Host "✅ Webhook URL copied to clipboard!" -ForegroundColor Green
    }
    catch {
        # Clipboard might not be available
    }
}
else {
    Write-Host "⚠️  Cloudflare URL not found in config" -ForegroundColor Yellow
    Write-Host "   Please check your config.yml file" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Next Steps (if not done yet):" -ForegroundColor Yellow
Write-Host "  1. Go to Meta for Developers Dashboard" -ForegroundColor Gray
Write-Host "  2. WhatsApp > Configuration > Webhook" -ForegroundColor Gray
Write-Host "  3. Paste the Webhook URL and Verify Token" -ForegroundColor Gray
Write-Host "  4. Click 'Verify and Save'" -ForegroundColor Gray
Write-Host "  5. You only need to do this ONCE!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window (services will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
