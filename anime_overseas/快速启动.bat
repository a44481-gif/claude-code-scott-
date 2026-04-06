@echo off
chcp 65001 >nul
title 动漫出海运营代理人 · 快速启动

echo ============================================================
echo         动漫出海运营代理人 · 快速启动
echo ============================================================
echo.

cd /d "%~dp0anime_overseas"

:menu
echo.
echo 请选择操作：
echo.
echo  [1] 每日摘要         - 查看今日运营状态
echo  [2] 批量运营         - 做10条凡人修仙传视频
echo  [3] 生成封面         - 生成YouTube缩略图
echo  [4] 下载素材         - 下载凡人修仙传片段
echo  [5] 手动上传指引     - 生成上传步骤说明
echo  [6] 收益报告         - 查看本月收益
echo  [7] 数据分析         - 查看账号数据
echo  [8] 交互模式         - 进入对话式操作界面
echo.
echo  [0] 退出
echo.
set /p choice=请输入选项 [1-8, 0退出]:

if "%choice%"=="1" goto daily
if "%choice%"=="2" goto batch
if "%choice%"=="3" goto thumbnail
if "%choice%"=="4" goto download
if "%choice%"=="5" goto guide
if "%choice%"=="6" goto revenue
if "%choice%"=="7" goto analytics
if "%choice%"=="8" goto interactive
if "%choice%"=="0" goto end
goto menu

:daily
echo.
python anime_ops.py daily
echo.
pause
goto menu

:batch
echo.
echo 开始批量运营：凡人修仙传 英语版 10条...
echo.
set /p count_input=输入数量（默认10）:
if "%count_input%"=="" set count_input=10
python anime_ops.py batch %count_input% --ip 凡人修仙传 --lang en
echo.
pause
goto menu

:thumbnail
echo.
set /p thumb_title=输入封面标题（英文，如：HE WAITED 1000 YEARS）:
if "%thumb_title%"=="" set thumb_title=HE WAITED 1000 YEARS - Fanren Xiuxian Zhuan
python anime_ops.py thumb "%thumb_title%"
echo.
echo 封面已生成到: youtube_uploads/thumbnails\
echo.
pause
goto menu

:download
echo.
set /p ep_num=输入集数（如：5，不输入则下载预告片）:
if "%ep_num%"=="" (
    python anime_ops.py download 凡人修仙传
) else (
    python anime_ops.py download 凡人修仙传 %ep_num%
)
echo.
pause
goto menu

:guide
echo.
python -c "
from pathlib import Path
from anime_ops import cmd_manual_upload_guide
print(cmd_manual_upload_guide('youtube_uploads/output/video.mp4', '凡人修仙传精彩片段'))
"
echo.
pause
goto menu

:revenue
echo.
python -c "
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import os; os.chdir(r'%~dp0anime_overseas')
from payment_agent import PaymentAgent
agent = PaymentAgent()
print(agent.generate_payment_report())
"
echo.
pause
goto menu

:analytics
echo.
python anime_ops.py analytics
echo.
pause
goto menu

:interactive
echo.
python anime_ops.py
goto menu

:end
echo.
echo 再见！祝运营顺利！
timeout /t 2 >nul
exit /b 0
