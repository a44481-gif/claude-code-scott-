@echo off
chcp 65001 > nul
REM AI数字人新闻系统启动脚本 (Windows)
REM Digital Human News System Startup Script

setlocal enabledelayedexpansion

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 创建必要的目录
if not exist "data\raw" mkdir "data\raw"
if not exist "data\processed" mkdir "data\processed"
if not exist "data\output" mkdir "data\output"
if not exist "logs" mkdir "logs"

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 显示帮助信息
goto :main

:show_help
echo AI数字人新闻系统
echo.
echo 用法: run.bat [选项]
echo.
echo 选项:
echo   full        运行完整流程 ^(默认^)
echo   fetch       仅抓取新闻
echo   filter      仅内容筛选
echo   create      仅AI二创
echo   generate    仅视频生成
echo   publish     仅平台发布
echo   scheduler   运行定时任务
echo   test        测试模式
echo   help        显示帮助信息
echo.
goto :end

:main
set "MODE=%~1"
if "%MODE%"=="" set "MODE=full"

if /i "%MODE%"=="help" goto :show_help
if /i "%MODE%"=="--help" goto :show_help
if /i "%MODE%"=="-h" goto :show_help

echo.
echo ================================================
echo     AI数字人新闻内容生产与全球分发系统
echo ================================================
echo.

if /i "%MODE%"=="full" (
    echo 开始运行完整流程...
    python main.py --mode full
    goto :end
)

if /i "%MODE%"=="fetch" (
    echo 运行 抓取新闻 模块...
    python main.py --mode fetch
    goto :end
)

if /i "%MODE%"=="filter" (
    echo 运行 内容筛选 模块...
    python main.py --mode filter
    goto :end
)

if /i "%MODE%"=="create" (
    echo 运行 AI二创 模块...
    python main.py --mode create
    goto :end
)

if /i "%MODE%"=="generate" (
    echo 运行 视频生成 模块...
    python main.py --mode generate
    goto :end
)

if /i "%MODE%"=="publish" (
    echo 运行 平台发布 模块...
    python main.py --mode publish
    goto :end
)

if /i "%MODE%"=="scheduler" (
    echo 启动定时任务调度器...
    python main.py --mode scheduler
    goto :end
)

if /i "%MODE%"=="test" (
    echo 测试模式运行...
    python main.py --mode full --test
    goto :end
)

echo 未知选项: %MODE%
echo.
goto :show_help

:end
echo.
echo 按任意键退出...
pause >nul
