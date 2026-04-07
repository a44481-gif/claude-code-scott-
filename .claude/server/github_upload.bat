@echo off
chcp 65001 >nul
echo ========================================
echo    SCOTT豆包赚钱 - GitHub 上传脚本
echo ========================================
echo.

cd /d "%~dp0"

:: 检查 Git 是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Git，请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

:: 检查远程仓库是否已配置
git remote -v >nul 2>&1
if errorlevel 1 (
    echo.
    echo [提示] 请先在 GitHub 创建仓库
    echo 1. 打开 https://github.com/new
    echo 2. Repository name: scott-payment-system
    echo 3. 选择 Private
    echo 4. 点击 Create repository
    echo.
    set /p REPO_URL="请粘贴仓库地址 (https://github.com/用户名/scott-payment-system.git): "

    git init
    git add .
    git commit -m "Initial commit: SCOTT豆包赚钱收款系统"
    git remote add origin %REPO_URL%
) else (
    echo [OK] Git 仓库已初始化
)

echo.
echo ========================================
echo    准备上传到 GitHub
echo ========================================
echo.

:: 检查是否有文件
git status --porcelain >nul 2>&1
if errorlevel 1 (
    echo [提示] 没有新文件需要上传
) else (
    echo [OK] 有新文件，准备上传...
)

:: 推送到 GitHub
echo.
echo 按任意键开始上传到 GitHub...
pause >nul

git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 上传失败，请检查:
    echo 1. GitHub 仓库是否存在
    echo 2. 网络连接是否正常
    echo 3. 仓库地址是否正确
) else (
    echo.
    echo ========================================
    echo    上传成功！
    echo ========================================
    echo.
    echo 下一步:
    echo 1. 打开 https://railway.app
    echo 2. 部署 scott-payment-system
    echo 3. 配置环境变量
)

echo.
pause
