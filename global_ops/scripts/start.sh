#!/bin/bash
# GlobalOPS · 快速启动脚本
# 用法: ./scripts/start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BASE_DIR"

echo "=========================================="
echo "  GlobalOPS · 统一自动运营平台"
echo "=========================================="
echo ""

# 复制环境变量模板
if [ ! -f "config/.env" ]; then
  echo "📝 首次运行：创建 .env 配置文件..."
  cp config/.env.example config/.env
  echo "⚠️  请编辑 config/.env 填写实际凭证"
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
  echo "❌ Docker 未安装"
  exit 1
fi

if ! docker info &> /dev/null; then
  echo "❌ Docker 未运行，请先启动 Docker Desktop"
  exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
  echo "❌ Node.js 未安装"
  exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Python 未安装"
  exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 安装 Python 依赖
echo "📦 安装 Python 依赖..."
cd python_engine
pip install -q -r requirements.txt 2>/dev/null || pip3 install -q -r requirements.txt
cd ..

# 安装 Node.js 依赖
echo "📦 安装 Node.js 依赖..."
cd content_engine
npm install --silent 2>/dev/null
cd ..

# 数据库迁移
echo "🔄 数据库迁移..."
chmod +x scripts/migrate_db.sh
bash scripts/migrate_db.sh

# 启动 Docker
echo "🚀 启动 Docker 服务..."
docker compose up -d

echo ""
echo "=========================================="
echo "  ✅ GlobalOPS 启动完成！"
echo "=========================================="
echo ""
echo "  🌐 n8n Dashboard:  http://localhost:5678"
echo "  📊 内容管理:       node content_engine/src/manager.js stats"
echo "  🎬 生成内容:       node content_engine/src/generator.js --db --count=10"
echo "  🚀 发布内容:       python python_engine/main.py publish --platform youtube"
echo ""
