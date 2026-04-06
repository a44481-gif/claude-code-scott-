# PSU 每日報告 - Windows 工作排程器設定腳本
# 使用方式：以系統管理員身份執行 PowerShell
#   Set-ExecutionPolicy -Scope RemoteSigned -Force
#   .\scheduler_setup.ps1
#
# 移除排程任務：
#   Unregister-ScheduledTask -TaskName "PSU_DailyReport" -Confirm:$false

param(
    [string]$PythonPath = "python",
    [string]$ScriptPath = "$PSScriptRoot\run_daily.py",
    [string]$RunTime = "09:00",
    [switch]$DryRun  # 測試模式，不實際建立任務
)

$ErrorActionPreference = "Stop"
$TaskName = "PSU_DailyReport"
$Description = "PSU電源供應器每日市場報告自動化 - 收集京東/天貓/Amazon數據並寄送AI分析報告"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PSU 每日報告 - Windows 任務排程器設定" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 驗證腳本存在
if (-not (Test-Path $ScriptPath)) {
    Write-Host "[錯誤] 找不到主腳本: $ScriptPath" -ForegroundColor Red
    Write-Host "請確認 run_daily.py 在正確位置" -ForegroundColor Yellow
    exit 1
}

Write-Host "[資訊] 工作名稱: $TaskName" -ForegroundColor White
Write-Host "[資訊] 執行時間: 每天 $RunTime" -ForegroundColor White
Write-Host "[資訊] 腳本路徑: $ScriptPath" -ForegroundColor White
Write-Host ""

# 檢查 Python 是否可用
Write-Host "[檢查] 驗證 Python 環境..." -ForegroundColor Yellow
try {
    $pyVersion = & $PythonPath --version 2>&1
    Write-Host "  ✅ Python: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python 找不到，請確認已安裝並加入 PATH" -ForegroundColor Red
    Write-Host "  或修改 PythonPath 參數指定 Python 路徑" -ForegroundColor Yellow
    exit 1
}

# 檢查必要套件
Write-Host "[檢查] 驗證必要套件..." -ForegroundColor Yellow
$requiredPkgs = @("httpx", "pyyaml", "beautifulsoup4", "lxml")
$missingPkgs = @()
foreach ($pkg in $requiredPkgs) {
    $installed = & $PythonPath -m pip show $pkg 2>$null
    if (-not $installed) {
        $missingPkgs += $pkg
        Write-Host "  ⚠️  缺少: $pkg" -ForegroundColor Red
    } else {
        Write-Host "  ✅ $pkg" -ForegroundColor Green
    }
}

if ($missingPkgs.Count -gt 0) {
    Write-Host ""
    Write-Host "[安裝] 正在安裝缺少的套件..." -ForegroundColor Yellow
    & $PythonPath -m pip install $missingPkgs --quiet
    Write-Host "  ✅ 套件安裝完成" -ForegroundColor Green
}

Write-Host ""

if ($DryRun) {
    Write-Host "[測試模式] 跳過任務建立" -ForegroundColor Cyan
    exit 0
}

# 移除舊任務（如果存在）
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[移除] 刪除既有任務: $TaskName" -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 建立動作
$action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory (Split-Path $ScriptPath)

# 觸發器：每天指定時間
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At $RunTime

# 原則：以最高權限執行，使用登入的使用者身份
$principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Highest

# 設定
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -RunOnlyIfNetworkAvailable:$false

# 註冊任務
Write-Host "[建立] 建立排程任務: $TaskName" -ForegroundColor Cyan
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $Description `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 排程任務建立成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "任務名稱: $TaskName" -ForegroundColor White
Write-Host "執行時間: 每天 $RunTime" -ForegroundColor White
Write-Host ""
Write-Host "可用指令：" -ForegroundColor Yellow
Write-Host "  查看任務:  Get-ScheduledTask -TaskName `"$TaskName`" | Get-ScheduledTaskInfo" -ForegroundColor Gray
Write-Host "  立即執行:  Start-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor Gray
Write-Host "  查看日誌:  Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'} | Where-Object { `$_.Message -like '*PSU*' } | Select-Object -First 10" -ForegroundColor Gray
Write-Host "  刪除任務:  Unregister-ScheduledTask -TaskName `"$TaskName`" -Confirm:`$false" -ForegroundColor Gray
Write-Host ""
Write-Host "首次執行前，請先填寫 config.yaml 中的：" -ForegroundColor Yellow
Write-Host "  1. minimax.api_key   - MiniMax API Key" -ForegroundColor White
Write-Host "  2. email.password    - 163.com 授權碼（SMTP）" -ForegroundColor White
Write-Host ""
