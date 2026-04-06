# ============================================================
# Windows 任務排程器設定腳本
# 功能：建立「每天早上 9:00」自動執行全球 PSU 報告的計劃任務
# 使用方式：以系統管理員身份執行 PowerShell，運行：
#   .\scheduler_setup.ps1
# ============================================================

param(
    [string]$ScriptPath = ".\run_daily.py",
    [string]$TaskName = "Global_PSU_DailyReport",
    [string]$Hour = "09",
    [string]$Minute = "00"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  全球 PSU 每日報告 — Windows 任務排程設定" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. 確認 Python 路徑
Write-Host "[1/5] 確認 Python 環境..." -ForegroundColor Yellow
$pythonCmd = "python"
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "  ✅ 找到 Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 未找到 python，請先安裝 Python 並加入 PATH" -ForegroundColor Red
    exit 1
}

# 確認腳本存在
$ScriptFullPath = Resolve-Path $ScriptPath -ErrorAction SilentlyContinue
if (-not $ScriptFullPath) {
    Write-Host "  ❌ 找不到腳本: $ScriptPath" -ForegroundColor Red
    Write-Host "  請確認 run_daily.py 位於當前目錄" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ 腳本路徑: $($ScriptFullPath.Path)" -ForegroundColor Green

# 2. 確認依賴套件
Write-Host "[2/5] 確認依賴套件..." -ForegroundColor Yellow
$required = @("httpx", "beautifulsoup4", "lxml", "pyyaml", "python-pptx", "playwright")
$missing = @()
foreach ($pkg in $required) {
    $installed = & $pythonCmd -m pip show $pkg 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missing += $pkg
        Write-Host "  ⚠️  缺少: $pkg" -ForegroundColor Red
    } else {
        Write-Host "  ✅ $pkg" -ForegroundColor Green
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "  正在自動安裝缺少的套件..." -ForegroundColor Yellow
    & $pythonCmd -m pip install $missing
}

# 3. 創建每日觸發器
Write-Host "[3/5] 創建任務排程..." -ForegroundColor Yellow

$action = New-ScheduledTaskAction `
    -Execute "$pythonCmd" `
    -Argument "`"$($ScriptFullPath.Path)`" --mode full" `
    -WorkingDirectory (Split-Path $ScriptFullPath.Path)

$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "$Hour`:$Minute"

# 任務Principal：使用當前用戶
$principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Highest

# 任務設定
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit ([TimeSpan]::FromHours(2))

# 4. 註冊任務
Write-Host "[4/5] 註冊計劃任務 `$TaskName..." -ForegroundColor Yellow

try {
    # 先刪除舊任務（如果存在）
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "全球電商平台 PSU 每日自動化報告 | 每日 ${Hour}:${Minute} 自動執行" `
        -Force

    Write-Host "  ✅ 任務已創建: $TaskName" -ForegroundColor Green

    # 立即觸發一次（可選）
    Write-Host ""
    Write-Host "  是否立即測試執行一次？(Y/N): " -ForegroundColor Cyan
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host "  正在執行測試運行..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $TaskName
        Start-Sleep 5
        $status = Get-ScheduledTask -TaskName $TaskName
        Write-Host "  任務狀態: $($status.State)" -ForegroundColor Green
    }

} catch {
    Write-Host "  ❌ 任務創建失敗: $_" -ForegroundColor Red
    Write-Host "  提示：以系統管理員身份執行此腳本" -ForegroundColor Yellow
    exit 1
}

# 5. 顯示任務狀態
Write-Host "[5/5] 任務狀態確認..." -ForegroundColor Yellow
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "  ✅ 任務已就緒！" -ForegroundColor Green
    Write-Host ""
    Write-Host "  📋 任務詳情：" -ForegroundColor Cyan
    Write-Host "    名稱:   $($task.TaskName)"
    Write-Host "    狀態:   $($task.State)"
    Write-Host "    觸發:   每日 ${Hour}:${Minute}"
    Write-Host "    腳本:   $($ScriptFullPath.Path)"
    Write-Host ""
    Write-Host "  📌 管理命令：" -ForegroundColor Cyan
    Write-Host "    查看狀態: Get-ScheduledTask -TaskName '$TaskName'"
    Write-Host "    立即執行: Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host "    停止任務: Stop-ScheduledTask -TaskName '$TaskName'"
    Write-Host "    刪除任務: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
} else {
    Write-Host "  ❌ 任務狀態獲取失敗" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  設定完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
