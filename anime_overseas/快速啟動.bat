@echo off
chcp 65001 >nul
title 動漫出海運營 - 一鍵開始
cd /d "%~dp0"

echo.
echo  ============================================================
echo     動漫出海運營代理人 v1.0
echo     凡人修仙傳 | 英語市場 | YouTube Shorts
echo     聯絡：scott365888@gmail.com / 微信 PTS9800
echo  ============================================================
echo.
echo  请選擇：
echo.
echo   [1] 立即上傳第一個視頻到 YouTube（馬上開始！）
echo   [2] 打開 YouTube Studio（准備上傳）
echo   [3] 打開上傳指南文件（5個視頻完整包）
echo   [4] 打開文件夾（查看所有剪輯和封面）
echo   [5] 設置 YouTube OAuth（全自動上傳，5分鐘）
echo   [6] 批量全流程（下載+剪輯+封面）
echo   [7] 每日報告
echo   [8] 收益報告
echo   [9] 全部做：打開Studio + 上傳指南 + OAuth設置頁
echo.
echo  ============================================================
set /p choice=請輸入選項 (1-9):

if "%choice%"=="1" goto upload_now
if "%choice%"=="2" goto studio
if "%choice%"=="3" goto guide
if "%choice%"=="4" goto folder
if "%choice%"=="5" goto oauth
if "%choice%"=="6" goto batch
if "%choice%"=="7" goto daily
if "%choice%"=="8" goto revenue
if "%choice%"=="9" goto all

:upload_now
start https://studio.youtube.com
echo 已打開 YouTube Studio！請選擇 clip_01_60s.mp4 上傳！
pause
goto end

:studio
start https://studio.youtube.com
echo 已打開 YouTube Studio！
pause
goto end

:guide
start "" "youtube_uploads\YouTube上傳完整包_5個視頻.md"
echo 已打開上傳指南！跟著做即可！
pause
goto end

:folder
start explorer "%~dp0youtube_uploads"
echo 已打開文件夾！
pause
goto end

:oauth
start https://console.cloud.google.com
echo.
echo ============================================================
echo  Google Cloud Console 已打開！
echo  請按照以下步驟：
echo  1. 登入 Google 帳號
echo  2. 新建項目，名稱：anime-ops
echo  3. 啟用 YouTube Data API v3
echo  4. 創建 OAuth 桌面應用憑證
echo  5. 下載 JSON 文件
echo  6. 把文件改名為 client_secrets.json
echo  7. 放到這個文件夾：%~dp0
echo  完成後聯繫我！
echo ============================================================
echo.
echo OAuth 文件需要放到這個位置：
echo %~dp0client_secrets.json
echo.
pause
goto end

:batch
python agent.py batch
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

:all
start https://studio.youtube.com
start https://console.cloud.google.com
start "" "youtube_uploads\YouTube上傳完整包_5個視頻.md"
start explorer "%~dp0youtube_uploads"
echo.
echo 已打開所有窗口！
echo.
echo  左上：YouTube Studio（准備上傳）
echo  右上：Google Cloud Console（設置 OAuth）
echo  另一個：上傳指南（跟著做）
echo.
echo  聯絡：scott365888@gmail.com / 微信 PTS9800
pause
goto end

:end
