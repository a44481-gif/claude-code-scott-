@echo off
chcp 65001 >nul
echo ======================================
echo AI 短视频每日内容推送 - 任务设置
echo ======================================
echo.

set SCRIPT_PATH=%~dp0daily_push.bat
set TASK_NAME=AI_ShortVideo_DailyPush

:: 删除已存在的任务
schtasks /delete /tn "%TASK_NAME%" /f 2>nul

:: 创建计划任务 - 每天早上9点
schtasks /create /tn "%TASK_NAME%" /tr "cmd /c \"%SCRIPT_PATH%\"" /sc DAILY /st 09:00 /f

if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo ✅ 任务设置成功！
    echo ======================================
    echo.
    echo 📅 每天早上 9:00 会自动：
    echo    1. 生成当日内容
    echo    2. 发送到邮箱 h13751019800@163.com
    echo.
    echo 📧 你只需要：
    echo    1. 打开邮箱查看内容
    echo    2. 复制文案去抖音发布
    echo.
) else (
    echo.
    echo ❌ 任务设置失败
    echo.
)

pause
