@echo off
chcp 65001 >nul
echo ==========================================
echo   GlobalOPS · 统一自动运营平台
echo ==========================================
echo.

cd /d "%~dp0\.."

REM 复制环境变量模板
if not exist "config\.env" (
    copy config\.env.example config\.env
    echo 📝 已创建 config\.env，请填写凭证
    echo.
)

echo 📦 安装 Python 依赖...
cd python_engine
pip install -q -r requirements.txt
cd ..

echo 📦 安装 Node.js 依赖...
cd content_engine
call npm install --silent
cd ..

echo 🔄 数据库迁移...
call docker run --rm -v "%cd%:/data" postgres:15 psql ^
    -h postgres ^
    -U postgres ^
    -d global_ops ^
    -f /data/database/migrations/001_initial_schema.sql

echo 🚀 启动 Docker 服务...
docker compose up -d

echo.
echo ==========================================
echo   ✅ GlobalOPS 启动完成！
echo ==========================================
echo.
echo   🌐 n8n Dashboard:  http://localhost:5678
echo   📊 内容统计:       node content_engine\src\manager.js stats
echo   🎬 生成内容:       node content_engine\src\generator.js --db --count=10
echo   🚀 发布内容:       python python_engine\main.py publish --platform youtube
echo.
pause
