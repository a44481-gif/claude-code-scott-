#!/bin/bash
# CoBM Cloud Agent - 一鍵部署腳本

set -e

echo "=============================================="
echo "CoBM Cloud Agent 一鍵部署腳本"
echo "=============================================="

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 參數
DEPLOY_METHOD=${1:-"docker"}  # docker | vps | local

# 函數
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 檢查依賴
check_dependencies() {
    log_info "檢查系統依賴..."

    if command -v docker &> /dev/null; then
        log_info "Docker: ✅"
    else
        log_warn "Docker: ❌ 未安裝"
        if [ "$DEPLOY_METHOD" == "docker" ]; then
            log_error "Docker 是必需的，請先安裝"
            exit 1
        fi
    fi

    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose: ✅"
    else
        log_warn "Docker Compose: ❌ 未安裝"
    fi
}

# 生成 API Key
generate_api_key() {
    echo $(openssl rand -hex 16)
}

# 部署 Docker
deploy_docker() {
    log_info "使用 Docker 部署..."

    # 創建目錄
    mkdir -p reports
    mkdir -p cloud_results

    # 複製配置文件
    if [ ! -f .env ]; then
        log_info "創建環境配置文件..."
        cat > .env << EOF
# Claude API Key (必填)
CLAUDE_API_KEY=your-claude-api-key-here

# SMTP 認證碼 (必填)
SMTP_AUTH_CODE=JWxaQXzrCQCWtPu3

# API 密鑰 (自動生成)
API_SECRET_KEY=$(generate_api_key)
EOF
        log_warn "請編輯 .env 文件填入您的 API Key"
    fi

    # 構建和啟動
    log_info "構建 Docker 鏡像..."
    docker-compose build

    log_info "啟動服務..."
    docker-compose up -d

    # 等待啟動
    sleep 5

    # 健康檢查
    if curl -s http://localhost:8000/health > /dev/null; then
        log_info "服務已啟動: http://localhost:8000"
        log_info "API 文檔: http://localhost:8000/docs"
    else
        log_error "服務啟動失敗，請檢查日誌"
        docker-compose logs
    fi
}

# 部署 VPS
deploy_vps() {
    log_info "使用 VPS 部署..."

    echo "請提供 VPS 信息:"
    read -p "VPS IP/域名: " VPS_HOST
    read -p "SSH 用戶名: " VPS_USER
    read -p "SSH 密碼: " -s VPS_PASS
    echo ""

    log_info "連接到 VPS..."
    # 這裡需要 sshpass 或 expect 工具
    # 簡化版本：輸出部署命令

    cat << 'EOF'
請在 VPS 上執行以下命令：

# 1. 安裝 Docker
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker

# 2. 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 上傳代碼
scp -r ./cloud_agent user@vps:/opt/cobm-agent/
cd /opt/cobm-agent

# 4. 配置環境變量
cat > .env << 'ENVEOF'
CLAUDE_API_KEY=your-key
SMTP_AUTH_CODE=your-smtp-code
API_SECRET_KEY=your-secret-key
ENVEOF

# 5. 啟動
docker-compose up -d

# 6. 配置 Nginx 反向代理 (可選)
# 配置 HTTPS
EOF
}

# 本地運行
deploy_local() {
    log_info "本地運行模式..."

    # 創建虛擬環境
    if [ ! -d "venv" ]; then
        log_info "創建 Python 虛擬環境..."
        python3 -m venv venv
    fi

    log_info "激活虛擬環境..."
    source venv/bin/activate

    log_info "安裝依賴..."
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

    log_info "啟動服務..."
    export CLAUDE_API_KEY=${CLAUDE_API_KEY:-"demo"}
    export SMTP_AUTH_CODE=${SMTP_AUTH_CODE:-""}
    export API_SECRET_KEY=${API_SECRET_KEY:-"cobm-secret-key-2026"}

    python app.py
}

# 主流程
main() {
    check_dependencies

    case $DEPLOY_METHOD in
        docker)
            deploy_docker
            ;;
        vps)
            deploy_vps
            ;;
        local)
            deploy_local
            ;;
        *)
            echo "未知部署方式: $DEPLOY_METHOD"
            echo "用法: ./deploy.sh [docker|vps|local]"
            exit 1
            ;;
    esac

    echo ""
    echo "=============================================="
    echo "部署完成！"
    echo "=============================================="
}

main
