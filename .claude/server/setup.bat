@echo off
chcp 65001 >nul
echo ========================================
echo    豆包运营代理人 - 环境安装脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python已安装

echo.
echo [2/3] 安装依赖包...
pip install flask flask-cors qrcode Pillow python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [3/3] 创建配置文件夹...
if not exist "data" mkdir data
if not exist ".env" (
    copy .env.example .env
    echo [提示] 已创建.env配置文件，请编辑配置后启动
)

echo.
echo ========================================
echo    安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 编辑 .env 文件配置支付宝和邮件
echo 2. 运行 python app.py 启动服务
echo 3. 访问 http://localhost:5000
echo.
pause
