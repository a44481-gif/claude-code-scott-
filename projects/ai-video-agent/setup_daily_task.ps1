# 设置每日自动任务
# 运行此脚本设置每天早上9点自动发送内容到邮箱

$scriptPath = "D:\claude mini max 2.7\projects\ai-video-agent\daily_push.bat"
$taskName = "AI_ShortVideo_DailyPush"

Write-Host "="*60
Write-Host "设置每日自动内容推送"
Write-Host "="*60
Write-Host ""

# 检查是否已存在任务
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "任务已存在，正在删除..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 创建触发器 - 每天早上9点
$trigger = New-ScheduledTaskTrigger -Daily -At "09:00"

# 创建操作
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`""

# 创建设置
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 注册任务
Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Settings $settings -Description "AI短视频每日内容推送" | Out-Null

Write-Host ""
Write-Host "✅ 任务设置成功！" -ForegroundColor Green
Write-Host ""
Write-Host "📅 每天早上 9:00 会自动：" -ForegroundColor Cyan
Write-Host "   1. 生成当日内容" -ForegroundColor White
Write-Host "   2. 发送到邮箱 h13751019800@163.com" -ForegroundColor White
Write-Host ""
Write-Host "📧 你只需要：" -ForegroundColor Cyan
Write-Host "   1. 打开邮箱查看内容" -ForegroundColor White
Write-Host "   2. 复制文案去抖音发布" -ForegroundColor White
Write-Host ""
Write-Host "="*60

# 立即执行一次测试
Write-Host ""
Write-Host "是否立即执行一次测试？(Y/N)"
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "正在执行测试..." -ForegroundColor Yellow
    & $scriptPath
}
