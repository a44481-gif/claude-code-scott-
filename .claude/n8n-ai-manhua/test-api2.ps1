$apiKey = "YOUR_API_KEY_HERE"
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
    $response = Invoke-WebRequest -Uri "https://api.anthropic.com/v1/messages" -Method Post -Headers $headers -Body $body
    Write-Host "SUCCESS! Status: $($response.StatusCode)"
    $response.Content
} catch {
    Write-Host "ERROR Status: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "ERROR: $($_.Exception.Message)"
    try {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        $reader.Close()
        Write-Host "Response Body: $responseBody"
    } catch {
        Write-Host "Could not read response body"
    }
}
