@echo off
chcp 65001 >nul
echo ============================================
echo    SCOTT 豆包赚钱 - 一键启动自动运营
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装
    pause
    exit /b 1
)

cd /d "%~dp0"

echo [1/4] 检查环境...
python -c "import flask, requests" 2>nul
if errorlevel 1 (
    echo [安装] 安装依赖包...
    pip install flask flask-cors requests python-dotenv qrcode Pillow gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo [2/4] 启动收款服务...
start "SCOTT-收款服务" python app.py

echo [3/4] 等待服务启动...
timeout /t 5 /nobreak >nul

echo [4/4] 检查状态...
curl -s http://127.0.0.1:5000/api/products >nul 2>&1
if errorlevel 1 (
    echo [警告] 服务可能未正常启动，请检查
) else (
    echo [成功] 服务已启动！
)

echo.
echo ============================================
echo    SCOTT 豆包赚钱 - 启动完成
echo ============================================
echo.
echo   收款页面: http://127.0.0.1:5000
echo   管理后台: http://127.0.0.1:5000/admin
echo.
echo 按任意键打开浏览器...
pause >nul
start http://127.0.0.1:5000
