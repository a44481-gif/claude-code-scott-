@echo off
chcp 65001 >nul
title 漫剧出海AI - 全自动运营

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   漫剧出海AI变现系统 - 全自动运营模式    ║
echo  ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0.."

:menu
cls
echo.
echo  ╭─────────────────────────────────────╮
echo  │       漫剧出海AI - 全自动运营       │
echo  ╰─────────────────────────────────────╯
echo.
echo  [1] 立即生成今日内容
echo  [2] 查看今日待发布内容
echo  [3] 设置每日自动提醒
echo  [4] 查看内容库统计
echo  [5] 导出发布清单
echo  [6] 打开输出目录
echo  [7] 测试云端同步
echo  [0] 退出
echo.
set /p choice=请选择操作 [0-7]:

if "%choice%"=="1" goto generate
if "%choice%"=="2" goto view
if "%choice%"=="3" goto schedule
if "%choice%"=="4" goto stats
if "%choice%"=="5" goto export
if "%choice%"=="6" goto open
if "%choice%"=="7" goto sync
if "%choice%"=="0" exit

:generate
echo.
echo  📝 正在生成内容...
node scripts/cloud-generator.js
echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:view
echo.
echo  📋 今日待发布内容:
echo.
if exist "output\daily_publish.md" (
    type output\daily_publish.md
) else (
    echo  暂无内容，请先生成!
)
echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:schedule
echo.
echo  ⏰ 设置每日自动提醒...
echo.
echo  将创建Windows定时任务:
echo   - 每天 08:00 提醒发布
echo   - 每天 12:00 提醒午间发布
echo   - 每天 20:00 提醒晚间发布
echo.
schtasks /create /tn "漫剧出海每日提醒" /tr "msg * /time:30 漫剧出海:该发布内容了! 打开 output\daily_publish.md 查看" /sc daily /st 08:00 /f >nul 2>&1
if %errorlevel%==0 (
    echo  ✅ 08:00 提醒已设置
) else (
    echo  ⚠️ 08:00 提醒设置失败(可能已存在)
)

schtasks /create /tn "漫剧出海午间提醒" /tr "msg * /time:30 漫剧出海:午间发布! 查看 output\daily_publish.md" /sc daily /st 12:00 /f >nul 2>&1
if %errorlevel%==0 (
    echo  ✅ 12:00 提醒已设置
) else (
    echo  ⚠️ 12:00 提醒设置失败
)

schtasks /create /tn "漫剧出海晚间提醒" /tr "msg * /time:30 漫剧出海:晚间发布! 现在是黄金时间!" /sc daily /st 20:00 /f >nul 2>&1
if %errorlevel%==0 (
    echo  ✅ 20:00 提醒已设置
) else (
    echo  ⚠️ 20:00 提醒设置失败
)

echo.
echo  📋 当前定时任务:
schtasks /query /tn "漫剧出海" 2>nul | findstr "漫剧" && echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:stats
echo.
echo  📊 内容库统计:
node scripts/manager.js stats
echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:export
echo.
echo  📤 导出发布清单...
node scripts/exporter.js md
if exist "output\daily_publish.md" (
    echo.
    echo  ✅ 已导出到 output\daily_publish.md
)
echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:open
echo.
explorer output
goto menu

:sync
echo.
echo  ☁️ 测试云端同步...
echo.
echo  GitHub Actions 状态检查:
echo  访问 https://github.com/YOUR_USERNAME/manhua-system/actions
echo.
echo  或手动触发:
echo  1. 打开 GitHub 仓库
echo  2. 点击 Actions
echo  3. 选择 "漫剧出海 - 每日内容生成"
echo  4. 点击 "Run workflow"
echo.
echo  按任意键返回菜单...
pause >nul
goto menu
