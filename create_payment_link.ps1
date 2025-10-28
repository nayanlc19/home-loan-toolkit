# Quick script to create payment links manually for Windows
# Usage: .\create_payment_link.ps1 user@email.com

param(
    [Parameter(Mandatory=$true)]
    [string]$UserEmail
)

$body = @{
    amount = 9900
    currency = "INR"
    description = "Home Loan Toolkit - Full Access Payment"
    customer = @{
        name = "Customer"
        email = $UserEmail
    }
    notify = @{
        sms = $false
        email = $true
    }
    reminder_enable = $true
    notes = @{
        product = "Home Loan Toolkit"
        user_email = $UserEmail
    }
} | ConvertTo-Json

$credentials = "rzp_live_RYmXpTJIWI1cMg:Oy7e2KsXnLvqRzABm43puF85"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($credentials)
$base64 = [Convert]::ToBase64String($bytes)

$headers = @{
    "Authorization" = "Basic $base64"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.razorpay.com/v1/payment_links" `
        -Method Post `
        -Headers $headers `
        -Body $body

    Write-Host "`nPayment link created successfully!" -ForegroundColor Green
    Write-Host "Email: $UserEmail" -ForegroundColor Cyan
    Write-Host "Payment Link: $($response.short_url)" -ForegroundColor Yellow
    Write-Host "Payment ID: $($response.id)" -ForegroundColor Gray
} catch {
    Write-Host "`nError creating payment link:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
