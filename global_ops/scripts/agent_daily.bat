@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set BASE_DIR=%SCRIPT_DIR%..
set LOG_FILE=%BASE_DIR%\logs\agent_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=!LOG_FILE: =0!

echo ==========================================
echo   🤖 GlobalOPS 代理自动运营
echo ==========================================

if not exist "%BASE_DIR%\logs" mkdir "%BASE_DIR%\logs"

echo [%date% %time%] 开始运营 >> "!LOG_FILE!" 2>nul

echo.
echo 📊 检查内容库...
node "%BASE_DIR%\content_engine\src\manager.js" stats >> "!LOG_FILE!" 2>nul
echo.

echo 🎬 生成今日新内容...
node "%BASE_DIR%\content_engine\src\generator.js" --db --count=10 >> "!LOG_FILE!" 2>nul
echo.

echo 🚀 触发 YouTube 发布...
python "%BASE_DIR%\python_engine\main.py" publish --platform youtube --limit=3 >> "!LOG_FILE!" 2>nul
echo.

echo 📈 采集运营数据...
python "%BASE_DIR%\python_engine\main.py" analytics --days=1 >> "!LOG_FILE!" 2>nul
echo.

echo 💰 检查收益...
python "%BASE_DIR%\python_engine\main.py" revenue --days=7 >> "!LOG_FILE!" 2>nul
echo.

echo [%date% %time%] 运营完成 >> "!LOG_FILE!" 2>nul
echo ==========================================
echo   ✅ 代理运营完成！查看日志: logs\
echo ==========================================
pause
