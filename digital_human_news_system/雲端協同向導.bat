@echo off
chcp 65001 > nul
title AI數字人直播系統 - 雲端協同

:menu
cls
echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║         AI數字人直播系統 - 雲端協同                      ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.
echo  [1] 啟動本地接收服務器 (端口 8081)
echo  [2] 啟動Webhook服務 (端口 8080)
echo  [3] 啟動全部服務
echo  [4] 顯示運行狀態
echo  [5] 查看今日統計
echo  [6] 查看待發布內容
echo  [7] 打開雲端協同指南
echo  [0] 退出
echo.
echo  ════════════════════════════════════════════════════════════
echo.

set /p choice=請選擇 (0-7):

if "%choice%"=="1" goto start_local
if "%choice%"=="2" goto start_webhook
if "%choice%"=="3" goto start_all
if "%choice%"=="4" goto show_status
if "%choice%"=="5" goto show_stats
if "%choice%"=="6" goto show_pending
if "%choice%"=="7" goto open_guide
if "%choice%"=="0" goto end

goto menu

:start_local
cls
echo.
echo  ════════════════════════════════════════════════════════════
echo               啟動本地接收服務器
echo  ════════════════════════════════════════════════════════════
echo.
echo  服務地址: http://localhost:8081
echo  功能: 接收雲端推送的結果
echo.
python cloud_sync_server.py --port 8081
goto menu

:start_webhook
cls
echo.
echo  ════════════════════════════════════════════════════════════
echo               啟動Webhook服務
echo  ════════════════════════════════════════════════════════════
echo.
echo  服務地址: http://localhost:8080
echo  功能: 供n8n調用的API
echo.
python n8n_webhook.py --port 8080
goto menu

:start_all
cls
echo.
echo  ════════════════════════════════════════════════════════════
echo               啟動全部服務
echo  ════════════════════════════════════════════════════════════
echo.
echo  將打開兩個終端窗口:
echo  [窗口1] 本地接收服務器 - http://localhost:8081
echo  [窗口2] Webhook服務     - http://localhost:8080
echo.
echo  按 Ctrl+C 可停止對應服務
echo.
start "本地接收服務器" cmd /k "python cloud_sync_server.py --port 8081"
timeout /t 2 /nobreak > nul
start "Webhook服務" cmd /k "python n8n_webhook.py --port 8080"
echo.
echo  服務已啟動！
timeout /t 3 /nobreak > nul
goto menu

:show_status
cls
echo.
echo  ════════════════════════════════════════════════════════════
echo               服務運行狀態
echo  ════════════════════════════════════════════════════════════
echo.

curl -s http://localhost:8081/health 2>nul
if %errorlevel% neq 0 (
    echo  [X] 本地接收服務器: 未運行
) else (
    echo  [OK] 本地接收服務器: 運行中
)

curl -s http://localhost:8080/health 2>nul
if %errorlevel% neq 0 (
    echo  [X] Webhook服務: 未運行
) else (
    echo  [OK] Webhook服務: 運行中
)

echo.
pause
goto menu

:show_stats
cls
echo.
echo  ════════════════════════════════════════════════════════════
echo               今日統計
echo  ════════════════════════════════════════════════════════════
echo.
curl -s http://localhost:8081/stats 2>nul || echo  請先啟動本地接收服務器
echo.
pause
goto menu

:show_pending
cls
echo.
echo  ════════════════════════════════════════════════════════════
echo               待發布內容
echo  ════════════════════════════════════════════════════════════
echo.
curl -s http://localhost:8081/pending 2>nul || echo  請先啟動本地接收服務器
echo.
pause
goto menu

:open_guide
start CLOUD_SYNC_GUIDE.md
goto menu

:end
cls
echo.
echo  ════════════════════════════════════════════════════════════
echo               感謝使用！
echo  ════════════════════════════════════════════════════════════
echo.
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak > nul
exit
