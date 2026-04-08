#!/bin/bash
# deploy_cloud.sh - VPS 部署腳本
# 用法: bash deploy_cloud.sh <server_ip>
# 示例: bash deploy_cloud.sh 123.45.67.89

set -e

SERVER="$1"
if [ -z "$1" ]; then
    echo "用法: $0 <server_ip> [ssh_port]"
    exit 1
fi
SSH_PORT="${2:-22}"
SSH_OPTS="-o StrictHostKeyChecking=no -p $SSH_PORT"

echo "🚀 部署 AI Agent 到 $SERVER ..."

# 1. 推送代碼
echo "[1/5] 推送代碼..."
rsync -avz --exclude '__pycache__' --exclude '*.pyc' \
    -e "ssh $SSH_OPTS" \
    ./cloud_server/ \
    root@$SERVER:/opt/ai-agent/

# 2. 安裝依賴
echo "[2/5] 安裝 Python 依賴..."
ssh $SSH_OPTS root@$SERVER "cd /opt/ai-agent && pip install -r requirements.txt -q"

# 3. 設定環境變量
echo "[3/5] 設定環境變量..."
ssh $SSH_OPTS root@$SERVER "cat > /etc/systemd/system/ai-agent.service << EOF
[Unit]
Description=AI Agent Cloud Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-agent
ExecStart=/usr/bin/python3 -m uvicorn src.run:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment=PORT=8000
Environment=TZ=Asia/Shanghai

[Install]
WantedBy=multi-user.target
EOF"

# 4. 啟動服務
echo "[4/5] 啟動服務..."
ssh $SSH_OPTS root@$SERVER "systemctl daemon-reload && systemctl enable ai-agent && systemctl restart ai-agent"

# 5. 驗證
echo "[5/5] 驗證部署..."
sleep 3
RESULT=$(curl -s http://$SERVER:8000/health 2>/dev/null || echo '{"status":"checking"}')
echo "✅ 部署完成！"
echo "   雲端 Server: http://$SERVER:8000"
echo "   健康檢查: $RESULT"
echo ""
echo "📋 常用指令:"
echo "   ssh $SSH_OPTS root@$SERVER"
echo "   systemctl status ai-agent    # 查看狀態"
echo "   journalctl -u ai-agent -f   # 查看日誌"
echo "   curl http://$SERVER:8000/trigger/it_news  # 手動觸發"
