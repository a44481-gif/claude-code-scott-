$html = Get-Content "d:/claude mini max 2.7/.claude/psu_daily_report_20260402.html" -Raw -Encoding UTF8
$subject = "Daily PSU Sales Report - 2026-04-02"
$to = "h13751019800@163.com"
$from = "h13751019800@163.com"
$smtp = "smtp.163.com"
$port = 465
$creds = ConvertTo-SecureString "FZQAXDZUHDWQHUIO" -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($from, $creds)

try {
    Send-MailMessage -From $from -To $to -Subject $subject -Body $html -BodyAsHtml -SmtpServer $smtp -Port $port -UseSsl -Credential $credential -Encoding UTF8
    Write-Host "EMAIL SENT SUCCESSFULLY to h13751019800@163.com"
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
}