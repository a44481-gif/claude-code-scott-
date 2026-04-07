#!/bin/bash
# ==========================================
# n8n AI Agent 快速啟動腳本
# ==========================================

set -e

echo "=========================================="
echo "  n8n PC電源營銷系統 啟動腳本"
echo "=========================================="

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝"
    exit 1
fi

# 檢查 .env 文件
if [ ! -f .env ]; then
    echo "📝 創建 .env 文件..."
    cp .env.example .env
    echo "⚠️  請編輯 .env 文件填入實際配置"
    echo "   特別是："
    echo "   - N8N_PASSWORD"
    echo "   - POSTGRES_PASSWORD"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - LARK_WEBHOOK"
    exit 1
fi

# 創建必要目錄
echo "📁 創建數據目錄..."
mkdir -p data workflows db nginx/ssl

# 拉取最新鏡像
echo "📦 拉取最新鏡像..."
docker-compose pull

# 啟動服務
echo "🚀 啟動服務..."
docker-compose up -d

# 等待服務就緒
echo "⏳ 等待服務啟動..."
sleep 10

# 檢查狀態
echo ""
echo "=========================================="
echo "  服務狀態"
echo "=========================================="
docker-compose ps

echo ""
echo "✅ n8n 系統已啟動！"
echo ""
echo "📍 訪問地址："
echo "   - n8n UI: http://localhost:5678"
echo "   - Webhook: http://localhost:5678/webhook/"
echo ""
echo "📚 API 文檔："
echo "   - http://localhost:5678/restricted/docs"
echo ""
echo "💡 首次使用："
echo "   1. 訪問 http://localhost:5678"
echo "   2. 使用管理員帳號登入"
echo "   3. 導入工作流：Settings > Import from File"
echo ""
echo "🔧 常用命令："
echo "   - 查看日誌: docker-compose logs -f n8n"
echo "   - 重啟服務: docker-compose restart"
echo "   - 停止服務: docker-compose down"
echo "   - 更新系統: docker-compose pull && docker-compose up -d"
echo ""
