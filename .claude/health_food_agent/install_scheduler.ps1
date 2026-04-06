# 健康食品 AI 扩客代理人 - 定时任务安装脚本
# 使用方法: 右键 -> "使用 PowerShell 运行" (需要管理员权限)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  健康食品 AI 扩客代理人 - 定时任务安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检测是否为管理员
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[错误] 请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键菜单 -> 更多 -> 使用管理员运行" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按 Enter 退出"
    exit 1
}

# 配置参数
$ScriptPath = "D:\claude mini max 2.7\.claude\health_food_agent\skill_health_food.py"
$WorkingDir = "D:\claude mini max 2.7\.claude\health_food_agent"
$PythonExe = "python"

# 检查 Python 是否可用
Write-Host "[1/4] 检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = & $PythonExe --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [错误] Python 未找到！" -ForegroundColor Red
    Write-Host "  请确保 Python 已安装并添加到 PATH" -ForegroundColor Yellow
    exit 1
}

# 检查脚本是否存在
Write-Host "[2/4] 检查脚本文件..." -ForegroundColor Yellow
if (Test-Path $ScriptPath) {
    Write-Host "  找到: skill_health_food.py" -ForegroundColor Green
} else {
    Write-Host "  [错误] 脚本文件不存在！" -ForegroundColor Red
    exit 1
}

# 选择执行频率
Write-Host ""
Write-Host "[3/4] 选择定时任务类型：" -ForegroundColor Yellow
Write-Host "  1) 每日执行 (每天 09:00)" -ForegroundColor White
Write-Host "  2) 每周执行 (每周一 09:00)" -ForegroundColor White
Write-Host ""
$choice = Read-Host "请选择 (1/2)"

if ($choice -eq "1") {
    $TaskName = "HealthFoodAgent_Daily"
    $TaskDesc = "健康食品 AI 扩客代理人 - 每日自动分析报告"
    $Trigger = New-ScheduledTaskTrigger -Daily -At "09:00"
    $Schedule = "每日"
} elseif ($choice -eq "2") {
    $TaskName = "HealthFoodAgent_Weekly"
    $TaskDesc = "健康食品 AI 扩客代理人 - 每周自动分析报告"
    $Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "09:00"
    $Schedule = "每周一"
} else {
    Write-Host "  [错误] 无效选择！" -ForegroundColor Red
    exit 1
}

# 创建任务动作
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "--mode full" -WorkingDirectory $WorkingDir

# 检查任务是否已存在
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host ""
    Write-Host "  任务 [$TaskName] 已存在，是否覆盖？" -ForegroundColor Yellow
    $overwrite = Read-Host "  输入 Y 覆盖，N 退出 (Y/N)"
    if ($overwrite -ne "Y") {
        Write-Host "  已取消安装" -ForegroundColor Yellow
        exit 0
    }
    # 移除旧任务
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "  已移除旧任务" -ForegroundColor Yellow
}

# 注册新任务
Write-Host ""
Write-Host "[4/4] 创建定时任务..." -ForegroundColor Yellow

try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Description $TaskDesc -RunLevel Highest -Force | Out-Null

    # 立即执行一次测试
    Write-Host ""
    Write-Host "  定时任务创建成功！" -ForegroundColor Green
    Write-Host "  任务名称: $TaskName" -ForegroundColor Cyan
    Write-Host "  执行频率: $Schedule 09:00" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  是否立即执行一次测试？" -ForegroundColor Yellow
    $testRun = Read-Host "  输入 Y 执行测试，N 跳过 (Y/N)"

    if ($testRun -eq "Y") {
        Write-Host ""
        Write-Host "  正在执行测试..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $TaskName
        Start-Sleep -Seconds 3

        $taskInfo = Get-ScheduledTask -TaskName $TaskName
        Write-Host ""
        Write-Host "  任务状态: $($taskInfo.State)" -ForegroundColor Cyan
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  安装完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "后续管理命令：" -ForegroundColor White
    Write-Host "  查看状态: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "  立即执行: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "  删除任务: Unregister-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "  [错误] 任务创建失败: $_" -ForegroundColor Red
    exit 1
}
