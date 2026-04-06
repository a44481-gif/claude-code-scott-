@echo off
chcp 65001 > nul
title AI数字人直播 - 自动配置向导
color 0A

:start
cls
echo.
echo  ============================================================
echo.
echo              AI 数字人直播 - 自动配置向导
echo.
echo  ============================================================
echo.
echo  [1] 配置抖音推流地址
echo  [2] 下载安装OBS Studio
echo  [3] 生成直播视频
echo  [4] 启动Webhook服务
echo  [5] 打开配置指南
echo  [6] 打开抖音创作平台
echo  [0] 退出
echo.
echo  ============================================================
echo.

set /p choice=请选择 (0-6):

if "%choice%"=="1" goto config_stream
if "%choice%"=="2" goto download_obs
if "%choice%"=="3" goto generate_videos
if "%choice%"=="4" goto start_webhook
if "%choice%"=="5" goto open_guide
if "%choice%"=="6" goto open_douyin
if "%choice%"=="0" goto end

goto start

:config_stream
cls
echo.
echo  ============================================================
echo               配置抖音推流地址
echo  ============================================================
echo.
echo  请到抖音创作服务平台获取推流地址:
echo  https://creator.douyin.com/
echo.
echo  格式: rtmp://push.toutiao.com/live/xxxx-xxxx
echo.
set /p stream_url=请粘贴推流地址:

python config_douyin.py "%stream_url%"
echo.
pause
goto start

:download_obs
cls
echo.
echo 正在打开OBS下载页面...
start https://obsproject.com/downloads
echo.
echo 下载完成后请运行OBS安装向导
pause
goto start

:generate_videos
cls
echo.
echo  ============================================================
echo               生成直播视频
echo  ============================================================
echo.
python generate_live_videos.py -c 5
echo.
pause
goto start

:start_webhook
cls
echo.
echo  ============================================================
echo               启动 Webhook 服务
echo  ============================================================
echo.
echo  按 Ctrl+C 停止服务
echo.
python n8n_webhook.py
goto start

:open_guide
cls
echo.
echo 正在打开配置指南...
start OBS_SETUP_GUIDE.md
goto start

:open_douyin
start https://creator.douyin.com/
goto start

:end
cls
echo.
echo  ============================================================
echo               感谢使用！
echo  ============================================================
echo.
timeout /t 3
exit
