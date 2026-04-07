@echo off
chcp 65001 >nul
title 动漫出海运营代理人
cd /d "%~dp0"
echo ========================================================
echo          动漫出海运营代理人 v1.0
echo          IP: 凡人修仙传 | 市场: 全球
echo          联系人: scott365888@gmail.com / 微信 PTS9800
echo ========================================================
echo.
echo 请选择操作:
echo.
echo  [1] 批量全流程（下载→剪辑→封面→准备上传）
echo  [2] 下载素材
echo  [3] 剪辑视频
echo  [4] 生成封面
echo  [5] 上传 YouTube（需要先设置 OAuth）
echo  [6] 每日报告
echo  [7] 收益报告
echo  [8] 交互模式
echo  [9] 打开输出文件夹
echo.
echo ========================================================
set /p choice=请输入选项 (1-9):
echo.

if "%choice%"=="1" goto batch
if "%choice%"=="2" goto download
if "%choice%"=="3" goto clip
if "%choice%"=="4" goto thumb
if "%choice%"=="5" goto upload
if "%choice%"=="6" goto daily
if "%choice%"=="7" goto revenue
if "%choice%"=="8" goto interactive
if "%choice%"=="9" goto openfolder

:batch
python agent.py batch
pause
goto end

:download
python agent.py download
pause
goto end

:clip
python agent.py clip
pause
goto end

:thumb
python agent.py thumb
pause
goto end

:upload
echo.
echo ========================================================
echo  上传 YouTube 需要先设置 OAuth:
echo  1. 打开浏览器访问: https://console.cloud.google.com
echo  2. 创建项目 -> 启用 YouTube Data API v3
echo  3. 创建 OAuth 凭据 -> 下载 JSON
echo  4. 把文件改名为 client_secrets.json
echo  5. 放到这个文件夹: %~dp0
echo ========================================================
set /p video_path=请输入视频路径（或直接回车使用第一个剪辑）:
if "%video_path%"=="" (
    python agent.py upload
) else (
    python agent.py upload "%video_path%"
)
pause
goto end

:daily
python agent.py daily
pause
goto end

:revenue
python agent.py revenue
pause
goto end

:interactive
python agent.py
pause
goto end

:openfolder
start explorer "%~dp0youtube_uploads"
pause
goto end

:end
