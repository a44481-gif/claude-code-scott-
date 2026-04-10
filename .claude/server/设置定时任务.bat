@echo off
chcp 65001 >nul
echo ============================================
echo    SCOTT 豆包赚钱 - 定时任务设置
echo ============================================
echo.

cd /d "%~dp0"

:: 创建定时任务 - 每日9点发送日报
echo [1/3] 设置每日运营日报...
schtasks /create /tn "SCOTT_每日日报" /tr "python \"%~dp0daily_report.py\"" /sc daily /st 09:00 /f 2>nul
if errorlevel 1 (
    echo [跳过] 每日日报任务可能已存在
) else (
    echo [成功] 每日日报已设置 (每天09:00)
)

:: 创建定时任务 - 每小时客户跟进检查
echo [2/3] 设置客户跟进检查...
schtasks /create /tn "SCOTT_客户跟进" /tr "python \"%~dp0customer_followup.py\"" /sc hourly /st 10:00 /f 2>nul
if errorlevel 1 (
    echo [跳过] 客户跟进任务可能已存在
) else (
    echo [成功] 客户跟进已设置 (每小时检查)
)

:: 创建定时任务 - 每5分钟同步数据
echo [3/3] 设置数据同步...
schtasks /create /tn "SCOTT_数据同步" /tr "python \"%~dp0cloud_sync.py\"" /sc minute /mo 5 /f 2>nul
if errorlevel 1 (
    echo [跳过] 数据同步任务可能已存在
) else (
    echo [成功] 数据同步已设置 (每5分钟)
)

echo.
echo ============================================
echo    定时任务设置完成！
echo ============================================
echo.
echo  已设置以下自动任务:
echo  ┌────────────────┬──────────────────┐
echo  │ 每日运营日报    │ 每天 09:00       │
echo  ├────────────────┼──────────────────┤
echo  │ 客户跟进检查    │ 每小时 10:00     │
echo  ├────────────────┼──────────────────┤
echo  │ 数据同步        │ 每 5 分钟        │
echo  └────────────────┴──────────────────┘
echo.
echo  查看所有任务: schtasks /query /tn "SCOTT"
echo  删除任务: schtasks /delete /tn "SCOTT_*" /f
echo.
pause
