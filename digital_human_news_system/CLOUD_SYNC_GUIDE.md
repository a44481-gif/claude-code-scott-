# 雲端協同架構 - 完整指南

## 架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                         雲端 (n8n Cloud)                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  定時觸發 → 新聞抓取 → AI二創 → 視頻生成 → 結果推送      │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│                        本地服務器                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ cloud_sync_server │→│    SQLite DB     │→│  郵件通知    │ │
│  │   (端口 8081)    │  │  數據存儲       │  │  h137510... │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 兩種部署模式

### 模式A：本地n8n + 本地服務器
```
本地電腦運行 n8n → 調用 localhost:8080 → 本地接收 localhost:8081
```

### 模式B：n8n Cloud + 本地服務器 ⭐推薦
```
n8n Cloud 定時執行 → 推送至本地 localhost:8081 → SQLite存儲
```

---

## 快速啟動

### 步驟1：啟動本地接收服務器
```bash
cd d:\claude mini max 2.7\digital_human_news_system
python cloud_sync_server.py --port 8081
```

### 步驟2：啟動Webhook服務（可選，如需本地觸發）
```bash
python n8n_webhook.py --port 8080
```

### 步驟3：配置n8n Cloud

1. 打開 https://n8n.io/cloud
2. 導入工作流：`n8n_cloud_sync_workflow.json`
3. 修改本地服務器地址為你的公網IP或內網IP

### 步驟4：配置端口轉發（如需外網訪問）

如需從雲端訪問本地服務器，使用 ngrok：

```bash
ngrok http 8081
# 複製顯示的 URL
# 在 n8n 中使用該 URL 作為推送地址
```

---

## 端點說明

### 本地接收服務器 (端口 8081)

| 端點 | 方法 | 說明 |
|------|------|------|
| `/webhook/cloud-result` | POST | 接收雲端結果 |
| `/webhook/content` | POST | 接收雲端內容 |
| `/webhook/stats` | POST | 接收雲端統計 |
| `/health` | GET | 健康檢查 |
| `/stats` | GET | 今日統計 |
| `/pending` | GET | 待處理內容 |
| `/all-stats` | GET | 多日統計 |

### Webhook服務 (端口 8080)

| 端點 | 方法 | 說明 |
|------|------|------|
| `/webhook/trigger` | POST | 觸發完整流程 |
| `/webhook/fetch` | POST | 抓取新聞 |
| `/webhook/create` | POST | AI二創 |
| `/webhook/generate` | POST | 生成視頻 |
| `/webhook/live-start` | POST | 開始直播 |
| `/health` | GET | 健康檢查 |

---

## 數據庫結構

### sync_results 表
```sql
id, source, result_type, data, received_at, status, processed_at
```

### daily_stats 表
```sql
id, date, news_fetched, content_created, videos_generated, errors
```

### content_queue 表
```sql
id, title, script, category, language, tags, status, source, received_at
```

---

## 常見問題

### Q: 如何從外網訪問本地服務器？

使用 ngrok 或內網穿透工具：

```bash
ngrok http 8081
# 獲得公網 URL: https://xxxx.ngrok.io
# 在 n8n 中使用: https://xxxx.ngrok.io/webhook/content
```

### Q: 如何查看數據庫內容？

```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/cloud_sync.db')
cursor = conn.execute('SELECT * FROM daily_stats')
for row in cursor:
    print(row)
"
```

### Q: 如何備份數據？

```bash
copy data\cloud_sync.db data\cloud_sync_backup_%date%.db
```

---

## 自動化流程

### 每日自動執行

1. n8n Cloud 定時觸發 (06:00)
2. 執行新聞抓取、AI二創、視頻生成
3. 結果自動推送至本地
4. 本地發送郵件通知

### 查看執行日誌

```bash
type logs\main_*.log
type logs\n8n_webhook_*.log
```

---

## 安全性配置

### Webhook 簽名驗證

在 `cloud_sync_server.py` 中設置密鑰：

```python
webhook_secret = "your_secret_key"
```

在 n8n 中添加 Header：
```
X-Signature: sha256=計算的簽名
```

### 防火牆配置

確保本地端口開放：
```bash
netsh advfirewall firewall add rule name="CloudSync" action=allow protocol=tcp localport=8081
```
