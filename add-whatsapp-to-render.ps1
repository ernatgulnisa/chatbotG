# Скрипт для добавления WhatsApp номера на Render через API

# 1. Сначала зарегистрируйтесь (если еще нет аккаунта)
$registerBody = @{
    email = "your@email.com"
    password = "your_password_min8chars"
    full_name = "Your Name"
    business_name = "Your Business"
} | ConvertTo-Json

# Раскомментируйте если нужно создать аккаунт:
# $registerResult = Invoke-RestMethod -Uri 'https://chatbotg-web.onrender.com/api/v1/auth/register' -Method Post -Body $registerBody -ContentType 'application/json'

# 2. Войдите в систему
$loginBody = @{
    username = "your@email.com"
    password = "your_password_min8chars"
} | ConvertTo-Json

$loginResult = Invoke-RestMethod -Uri 'https://chatbotg-web.onrender.com/api/v1/auth/login' -Method Post -Body $loginBody -ContentType 'application/json'

$token = $loginResult.access_token
Write-Host "Token получен: $token"

# 3. Добавьте WhatsApp номер
$whatsappBody = @{
    display_name = "Мой WhatsApp"
    phone_number = "+77711919140"
    phone_number_id = "819213961283826"
    waba_id = "25435060679483721"
    api_token = "YOUR_ACCESS_TOKEN_FROM_META"  # Замените на реальный токен!
    is_active = $true
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$whatsappResult = Invoke-RestMethod -Uri 'https://chatbotg-web.onrender.com/api/v1/whatsapp/numbers' -Method Post -Body $whatsappBody -Headers $headers -ContentType 'application/json'

Write-Host "WhatsApp номер добавлен!"
$whatsappResult
