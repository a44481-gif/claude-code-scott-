@echo off
chcp 65001 >nul
title 漫剧出海AI - 自动视频生成器

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   漫剧出海AI - 全自动视频生成            ║
echo  ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0.."

:menu
cls
echo.
echo  ╭─────────────────────────────────────╮
echo  │       漫剧出海AI - 代理人运营       │
echo  ╰─────────────────────────────────────╯
echo.
echo  [1] 生成今日内容 + 图片
echo  [2] 生成视频 (需要剪映)
echo  [3] 批量生成5套内容
echo  [4] 查看今日待发布
echo  [5] 设置每日自动生成
echo  [0] 退出
echo.
set /p choice=请选择操作 [0-5]:

if "%choice%"=="1" goto generate
if "%choice%"=="2" goto make_video
if "%choice%"=="3" goto batch
if "%choice%"=="4" goto view
if "%choice%"=="5" goto schedule
if "%choice%"=="0" exit

:generate
echo.
echo  📝 正在生成内容...
python scripts/auto_video_generator.py
echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:make_video
echo.
echo  🎬 视频制作说明:
echo.
echo  由于TikTok限制，需要使用剪映制作视频:
echo.
echo  1. 打开 剪映 APP
echo  2. 选择 "图文成片"
echo  3. 复制 output\*.md 里的内容
echo  4. 选择配音主播
echo  5. 生成视频
echo  6. 发布到TikTok
echo.
echo  或者使用本地剪映电脑版批量制作
echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:batch
echo.
echo  📚 批量生成5套内容...
python scripts/auto_video_generator.py
python scripts/auto_video_generator.py
python scripts/auto_video_generator.py
python scripts/auto_video_generator.py
python scripts/auto_video_generator.py
echo.
echo  ✅ 已生成5套内容！
echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:view
echo.
echo  📋 今日待发布内容:
echo.
if exist "output\publish_*.md" (
    dir /b /o:-d output\publish_*.md | findstr /n "." | findstr "^1:"
    set "firstfile="
    for /f "delims=" %%a in ('dir /b /o:-d output\publish_*.md') do (
        if not defined firstfile set "firstfile=%%a" & goto found
    )
    :found
    if defined firstfile type output\%firstfile%
) else (
    echo  暂无内容，请先生成！
)
echo.
echo  按任意键返回菜单...
pause >nul
goto menu

:schedule
echo.
echo  ⏰ 设置每日自动生成...
echo.
echo  将创建Windows定时任务:
echo   - 每天 08:00 自动生成内容
echo.
set /p email=请输入通知邮箱 [%email%]:
if "%email%"=="" set "email=a44481@gmail.com"
echo.
echo  邮箱: %email%
echo.
echo  正在创建定时任务...
schtasks /create /tn "ManhuaContentGen" /tr "python \"%cd%\scripts\auto_video_generator.py\"" /sc daily /st 08:00 /f >nul 2>&1
if %errorlevel%==0 (
    echo  ✅ 定时任务创建成功！
) else (
    echo  ⚠️ 定时任务可能已存在
)
echo.
echo  按任意键返回菜单...
pause >nul
goto menu
