# CoBM Cloud Agent 雲端 AI 自動化系統

將本地工作搬到雲端，自動執行數據分析、報告生成、郵件發送。

## 🚀 快速開始

### 方式一：Docker 一鍵部署

```bash
cd cloud_agent

# 編輯環境配置
cp .env.example .env
nano .env  # 填入 CLAUDE_API_KEY

# 啟動服務
docker-compose up -d

# 測試
curl http://localhost:8000/health
```

### 方式二：本地運行

```bash
cd cloud_agent

# 安裝依賴
pip install -r requirements.txt

# 設置環境變量
export CLAUDE_API_KEY="your-key"
export SMTP_AUTH_CODE="your-code"
export API_SECRET_KEY="your-secret"

# 啟動
python app.py
```

## 📡 API 使用

### 創建任務

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "X-API-Key: cobm-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "full_pipeline",
    "params": {},
    "email_to": "scott365888@gmail.com"
  }'
```

### 響應

```json
{
  "task_id": "a1b2c3d4",
  "status": "pending",
  "message": "任務已創建，ID: a1b2c3d4",
  "check_url": "/api/v1/tasks/a1b2c3d4"
}
```

### 查詢狀態

```bash
curl http://localhost:8000/api/v1/tasks/a1b2c3d4 \
  -H "X-API-Key: cobm-secret-key-2026"
```

## 💻 本地觸發器

```bash
# 執行全流程（爬蟲→分析→報告→郵件）
python local_trigger.py --type full_pipeline

# 僅生成報告
python local_trigger.py --type report

# 僅爬取數據
python local_trigger.py --type crawl
```

## 🔄 工作流程

```
本地觸發 ──▶ 雲端 API ──▶ 任務佇列 ──▶ Claude AI
                                    │
                                    ▼
                            ┌───────────────┐
                            │   數據爬取    │
                            └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │   AI 分析    │
                            └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  報告生成    │
                            │  (PPT/文檔)  │
                            └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  郵件發送    │
                            │  163.com     │
                            └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  結果回傳    │
                            │  本地存儲    │
                            └───────────────┘
```

## 📊 支持的任務類型

| 類型 | 功能 | 說明 |
|------|------|------|
| `full_pipeline` | 全流程自動化 | 爬蟲→分析→報告→郵件 |
| `report` | 僅生成報告 | 根據參數生成 PPT |
| `crawl` | 僅爬取數據 | 采集市場數據 |
| `analyze` | 僅分析 | 調用 AI 分析數據 |

## 🌐 部署到雲端

### 騰訊雲函數 (SCF)

1. 打包代碼：`zip -r cloud_agent.zip app.py requirements.txt`
2. 上傳到騰訊雲 SCF
3. 配置環境變量
4. 設置定時觸發器

### 阿里雲函數計算

1. 使用 Serverless Devs 工具
2. 配置 s.yaml
3. 部署：`s deploy`

### VPS (DigitalOcean/AWS)

```bash
# 安裝 Docker
curl -fsSL https://get.docker.com | sh

# 上傳代碼
scp -r cloud_agent user@server:/opt/

# 配置和啟動
cd /opt/cloud_agent
cp .env.example .env
nano .env
docker-compose up -d
```

## 📁 目錄結構

```
cloud_agent/
├── app.py              # FastAPI 主程式
├── local_trigger.py    # 本地觸發器
├── requirements.txt    # Python 依賴
├── Dockerfile          # Docker 配置
├── docker-compose.yml  # Docker Compose 配置
├── deploy.sh           # 一鍵部署腳本
├── .env.example        # 環境變量模板
└── README.md           # 本文件
```

## 🔧 配置說明

### 環境變量

| 變量 | 必填 | 說明 |
|------|------|------|
| `CLAUDE_API_KEY` | ✅ | Anthropic API Key |
| `SMTP_AUTH_CODE` | ✅ | 163.com SMTP 認證碼 |
| `API_SECRET_KEY` | ✅ | API 訪問密鑰 |

### API Key 認證

所有 API 請求都需要在 Header 中包含：

```
X-API-Key: your-api-secret-key
```

## 📝 示例代碼

### Python 調用

```python
import requests

response = requests.post(
    "http://your-cloud-api.com/api/v1/tasks",
    headers={"X-API-Key": "your-key"},
    json={
        "task_type": "full_pipeline",
        "params": {"deep_analysis": True},
        "email_to": "your@email.com"
    }
)

print(response.json())
# {'task_id': 'xxx', 'status': 'pending', ...}
```

### JavaScript/Node.js 調用

```javascript
const response = await fetch('http://your-cloud-api.com/api/v1/tasks', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    task_type: 'full_pipeline',
    email_to: 'your@email.com'
  })
});

const result = await response.json();
console.log(result.task_id);
```

## ❓ 常見問題

**Q: 如何確保 API 安全？**
A: 使用 HTTPS + API Key 認證，可選增加 IP 白名單。

**Q: 任務執行失敗怎麼辦？**
A: 查詢 `/api/v1/tasks/{task_id}` 查看錯誤信息。

**Q: 如何實現定時執行？**
A: 雲端：配置定時觸發器；本地：使用 cron + local_trigger.py。

**Q: 報告生成在哪裡？**
A: 雲端存儲在 `/tmp/reports`，可通過 `/api/v1/tasks/{id}/download` 下載。

## 📞 支持

如需幫助，請聯繫技術支持。
