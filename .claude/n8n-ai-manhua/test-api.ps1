$apiKey = "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"
$headers = @{
    "x-api-key" = $apiKey
    "anthropic-version" = "2023-06-01"
    "content-type" = "application/json"
}
$body = @{
    model = "claude-sonnet-4-6"
    max_tokens = 100
    messages = @(
        @{
            role = "user"
            content = "Say 'OK' in exactly that word"
        }
    )
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "https://api.anthropic.com/v1/messages" -Method Post -Headers $headers -Body $body
    Write-Host "SUCCESS!"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "ERROR: $_"
    $_.Exception.Response
}
