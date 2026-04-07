# n8n AI Agent 自動化工作流系統

## 系統架構

```
n8n AI Agent
├── workflows/              # 工作流定義
│   ├── psu_marketing/       # PC電源營銷工作流
│   ├── competitor_analysis/ # 競品分析工作流
│   └── data_sync/          # 數據同步工作流
├── nodes/                   # 自定義節點
├── triggers/               # 觸發器配置
├── credentials/            # 憑證管理
└── config.json             # 全局配置
```

## 核心工作流

### 1. 競品情報自動收集工作流

```yaml
name: "PC電源競品情報收集"
version: "1.0"

trigger:
  type: schedule
  cron: "0 8 * * *"  # 每天早上8點

nodes:
  - name: "觸發器"
    type: "schedule"
    config:
      rule: "everyDay"
      hour: 8

  - name: "爬取 AnandTech"
    type: "httpRequest"
    config:
      url: "https://www.anandtech.com/tag/psu"
      method: "GET"
    output: "anand_data"

  - name: "爬取 Tom's Hardware"
    type: "httpRequest"
    config:
      url: "https://www.tomshardware.com/tag/power-supplies"
      method: "GET"
    output: "tom_data"

  - name: "爬取 Amazon 價格"
    type: "httpRequest"
    config:
      url: "https://www.amazon.com/s?k=power+supply+1000W"
      method: "GET"
    output: "amazon_data"

  - name: "AI 分析整理"
    type: "anthropic"
    config:
      model: "claude-sonnet-4-6"
      prompt: |
        分析以下PC電源競品情報，生成結構化報告：

        AnandTech數據：{{ $json.anand_data }}
        Tom's Hardware數據：{{ $json.tom_data }}
        Amazon價格數據：{{ $json.amazon_data }}

        輸出格式：
        1. 本週新產品發布
        2. 價格變動監控
        3. 技術趨勢解讀
        4. 競爭對手動態
        5. 機會與威脅分析

  - name: "發送飛書通知"
    type: "lark"
    config:
      webhook: "{{ $env.LARK_WEBHOOK }}"
      message: "{{ $json.ai_report }}"

  - name: "存入數據庫"
    type: "postgres"
    config:
      operation: "insert"
      table: "competitor_intel"
      data: "{{ $json }}"
```

---

### 2. 客戶開發自動化工作流

```yaml
name: "PC電源客戶自動開發"
version: "1.0"

trigger:
  type: webhook
  path: "/webhook/psu-lead"

nodes:
  - name: "接收客戶信息"
    type: "webhook"
    output: "lead_data"

  - name: "AI 資格審查"
    type: "anthropic"
    config:
      model: "claude-sonnet-4-6"
      prompt: |
        對以下潛在客戶進行資格審查：

        公司：{{ $json.company }}
        市場：{{ $json.market }}
        採購需求：{{ $json.requirement }}
        歷史採購：{{ $json.purchase_history }}

        評估維度：
        1. 採購能力（1-10分）
        2. 需求匹配度（1-10分）
        3. 成交可能性（1-10分）
        4. 優先級：高/中/低
        5. 建議跟進策略

  - name: "判斷優先級"
    type: "if"
    conditions:
      - expression: "{{ $json.priority }}" == "高"
    output:
      high: "高優先級流程"
      other: "標準流程"

  # 高優先級流程
  - name: "高優先級-生成個性化開發信"
    type: "anthropic"
    config:
      model: "claude-sonnet-4-6"
      prompt: |
        生成個性化的B2B開發信：

        目標客戶：{{ $json.company }}
        採購需求：{{ $json.requirement }}
        市場背景：{{ $json.market }}

        要求：
        - 語言：{{ $json.language }}
        - 長度：200字以內
        - 包含具體產品建議
        - 明確下一步行動

  - name: "發送高優先級郵件"
    type: "smtp"
    config:
      to: "{{ $json.email }}"
      subject: "PC電源解決方案 - {{ $json.company }}定製"
      body: "{{ $json.email_content }}"

  # 標準流程
  - name: "標準-加入培育序列"
    type: "n8nQueue"
    config:
      queue: "lead_nurture"
      data: "{{ $json }}"
```

---

### 3. 報價自動生成工作流

```yaml
name: "PC電源報價自動生成"
version: "1.0"

trigger:
  type: webhook
  path: "/webhook/psu-quote"

nodes:
  - name: "接收詢價"
    type: "webhook"
    output: "rfq_data"

  - name: "AI 報價計算"
    type: "anthropic"
    config:
      model: "claude-sonnet-4-6"
      prompt: |
        根據以下詢價信息，生成完整報價方案：

        客戶：{{ $json.customer }}
        產品：{{ $json.products }}
        數量：{{ $json.quantity }}
        目標價：{{ $json.target_price }}
        市場：{{ $json.market }}
        競爭對手：{{ $json.competitors }}

        輸出要求：
        1. 詳細報價單（含單價、總價）
        2. 價格構成分析
        3. 交期方案
        4. 付款條件建議
        5. 談判策略（如果目標價低於成本）
        6. 有效期限
        7. 備注條款

  - name: "利潤率檢查"
    type: "if"
    conditions:
      - expression: "{{ $json.margin }}" < 0.15
        action: "flag_review"
      - expression: "{{ $json.margin }}" >= 0.15
        action: "auto_approve"

  - name: "需要主管審批"
    type: "slack"
    config:
      channel: "#sales-approvals"
      message: |
        報價需要審批：
        客戶：{{ $json.customer }}
        產品：{{ $json.products }}
        數量：{{ $json.quantity }}
        預期利潤率：{{ $json.margin }}%
        原因：利潤率低於15%

  - name: "生成PDF報價單"
    type: "pdf"
    config:
      template: "psu_quote_template"
      data: "{{ $json }}"

  - name: "發送報價郵件"
    type: "smtp"
    config:
      to: "{{ $json.customer_email }}"
      subject: "PC電源報價單 - {{ $json.quote_number }}"
      attachments:
        - "{{ $json.pdf_path }}"
      body: |
        尊敬的 {{ $json.customer }}：

        感謝您的詢價，請查收附件中的詳細報價單。

        如有任何疑問，請回覆此郵件或致電聯繫。

        期待與您合作！

  - name: "存入CRM"
    type: "hubspot"
    config:
      operation: "create"
      entity: "deal"
      data: "{{ $json }}"
```

---

### 4. 每週銷售報告自動生成

```yaml
name: "PC電源每週銷售報告"
version: "1.0"

trigger:
  type: schedule
  cron: "0 9 * * 1"  # 每週一早上9點

nodes:
  - name: "觸發器"
    type: "schedule"

  - name: "獲取本週數據"
    type: "postgres"
    config:
      query: |
        SELECT
          DATE_TRUNC('week', created_at) as week,
          customer,
          product,
          quantity,
          revenue,
          margin,
          status
        FROM sales_orders
        WHERE created_at >= NOW() - INTERVAL '4 weeks'

  - name: "獲取競品情報"
    type: "postgres"
    config:
      query: |
        SELECT *
        FROM competitor_intel
        WHERE collected_at >= NOW() - INTERVAL '7 days'

  - name: "AI 生成週報"
    type: "anthropic"
    config:
      model: "claude-sonnet-4-6"
      prompt: |
        生成PC電源業務每週報告：

        銷售數據：
        {{ $json.sales_data }}

        競品情報：
        {{ $json.competitor_data }}

        報告結構：
        1. 本週概覽（關鍵指標）
        2. 銷售業績分析
        3. 產品線表現
        4. 客戶開發進展
        5. 競品動態
        6. 風險預警
        7. 下週行動計劃

  - name: "生成Excel報告"
    type: "exceljs"
    config:
      template: "weekly_report_template"
      data: "{{ $json }}"

  - name: "發送郵件"
    type: "smtp"
    config:
      to: "{{ $env.SALES_TEAM_EMAIL }}"
      subject: "PC電源每週報告 - {{ $json.week }}"
      attachments:
        - "{{ $json.excel_path }}"

  - name: "發布到飛書文檔"
    type: "lark"
    config:
      operation: "create_document"
      title: "PC電源週報 - {{ $json.week }}"
      content: "{{ $json.report }}"
```

---

## n8n + AI 整合配置

### Anthropic API 節點配置

```json
{
  "nodes": {
    "anthropic": {
      "name": "Claude AI",
      "type": "@n8n/n8n-nodes-langchain.anthropic",
      "position": [250, 300],
      "parameters": {
        "resource": "chat",
        "model": "claude-sonnet-4-6",
        "messages": {
          "values": [
            {
              "role": "system",
              "content": "你是一個專業的PC電源行業分析師。"
            },
            {
              "role": "user",
              "content": "{{ $json.user_prompt }}"
            }
          ]
        },
        "options": {
          "temperature": 0.7,
          "maxTokens": 4096
        }
      },
      "credentials": {
        "anthropicApi": "anthropic-api"
      }
    }
  }
}
```

---

## 自定義 n8n 節點

### PC電源競品情報節點

```javascript
// nodes/CompetitorIntel/node.js

module.exports = {
  displayName: 'PC電源競品情報',
  name: 'competitorIntel',
  icon: 'file:psu.svg',
  group: ['transform'],
  version: 1,
  description: '收集PC電源競品情報',
  defaults: {
    name: 'PC電源競品情報',
  },
  inputs: ['main'],
  outputs: ['main'],
  credentials: [],
  properties: [
    {
      displayName: '競品名稱',
      name: 'competitor',
      type: 'string',
      required: true,
      options: [
        { name: 'Seasonic', value: 'seasonic' },
        { name: 'Corsair', value: 'corsair' },
        { name: 'Super Flower', value: 'superflower' },
        { name: 'be quiet!', value: 'bequiet' },
        { name: 'EVGA', value: 'evga' },
      ]
    },
    {
      displayName: '功率段',
      name: 'wattage',
      type: 'string',
      options: [
        { name: '550-650W', value: '550-650' },
        { name: '750-850W', value: '750-850' },
        { name: '1000-1200W', value: '1000-1200' },
        { name: '1500W+', value: '1500+' },
      ]
    },
    {
      displayName: '數據來源',
      name: 'sources',
      type: 'multiOptions',
      options: [
        { name: '官網', value: 'official' },
        { name: '評測網站', value: 'review' },
        { name: '電商價格', value: 'ecommerce' },
        { name: '社交媒體', value: 'social' },
      ]
    }
  ],

  async execute() {
    const items = this.getInputData();
    const competitor = this.getNodeParameter('competitor', 0);
    const wattage = this.getNodeParameter('wattage', 0);
    const sources = this.getNodeParameter('sources', 0);

    const results = [];

    // 收集官網數據
    if (sources.includes('official')) {
      const officialData = await this.collectOfficialData(competitor, wattage);
      results.push(...officialData);
    }

    // 收集評測數據
    if (sources.includes('review')) {
      const reviewData = await this.collectReviewData(competitor, wattage);
      results.push(...reviewData);
    }

    // 收集電商價格
    if (sources.includes('ecommerce')) {
      const priceData = await this.collectPriceData(competitor, wattage);
      results.push(...priceData);
    }

    return this.prepareOutputData(results);
  },

  async collectOfficialData(competitor, wattage) {
    // 實現數據收集邏輯
    return [{
      competitor,
      wattage,
      source: 'official',
      data: {}
    }];
  },

  async collectReviewData(competitor, wattage) {
    return [{
      competitor,
      wattage,
      source: 'review',
      data: {}
    }];
  },

  async collectPriceData(competitor, wattage) {
    return [{
      competitor,
      wattage,
      source: 'ecommerce',
      data: {}
    }];
  }
};
```

---

## 觸發器配置

### Schedule Trigger（定時觸發）

```json
{
  "triggers": {
    "daily_competitor_scan": {
      "type": "schedule",
      "cron": "0 8 * * *",
      "workflow": "competitor_intel_daily"
    },
    "weekly_report": {
      "type": "schedule",
      "cron": "0 9 * * 1",
      "workflow": "weekly_sales_report"
    },
    "monthly_business_review": {
      "type": "schedule",
      "cron": "0 10 1 * *",
      "workflow": "monthly_business_review"
    }
  }
}
```

---

## 環境變量配置

```bash
# .env 文件

# n8n 基本配置
N8N_BASIC_AUTH_ACTIVE=true
N8N_HOST=https://n8n.yourdomain.com
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n.yourdomain.com/

# AI API
ANTHROPIC_API_KEY=sk-xxx

# 數據庫
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=psu_marketing
POSTGRES_USER=xxx
POSTGRES_PASSWORD=xxx

# 郵件
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=465
SMTP_USER=xxx@yourdomain.com
SMTP_PASSWORD=xxx

# 飛書
LARK_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
LARK_APP_ID=cli_xxx
LARK_APP_SECRET=xxx

# Slack
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_TEAM_ID=Txxx

# CRM
HUBSPOT_API_KEY=xxx

# 團隊郵箱
SALES_TEAM_EMAIL=sales@yourdomain.com
```

---

## Docker Compose 部署

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    container_name: n8n_psu_marketing
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - EXECUTIONS_MODE=regular
      - EXECUTIONS_TIMEOUT_MAX=600
    volumes:
      - ./data:/home/node/.n8n
      - ./workflows:/workflows
    restart: unless-stopped

  postgres:
    image: postgres:15
    container_name: n8n_postgres
    environment:
      - POSTGRES_DB=psu_marketing
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: n8n_redis
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

## 快速啟動

```bash
# 1. 克隆配置
git clone https://github.com/your-repo/n8n-psu-marketing.git
cd n8n-psu-marketing

# 2. 配置環境變量
cp .env.example .env
# 編輯 .env 填入實際值

# 3. 啟動服務
docker-compose up -d

# 4. 訪問 n8n
open http://localhost:5678

# 5. 導入工作流
# Settings > Import from File > 選擇 workflows/*.json
```

---

## 工作流列表

| 工作流名稱 | 觸發方式 | 功能 |
|-----------|--------|------|
| 競品情報每日收集 | 每天8:00 | 自動爬取競品動態 |
| 客戶開發自動跟進 | Webhook | 接收客戶信息自動處理 |
| 報價自動生成 | Webhook | 接收詢價自動報價 |
| 每週銷售報告 | 每週一9:00 | 自動生成並發送週報 |
| 月度業務回顧 | 每月1日10:00 | 生成月度總結 |
| 庫存監控預警 | 每小時 | 監控庫存發送預警 |

---

## 聯絡窗口

所有對外聯絡統一使用以下窗口：

| 渠道 | 地址/ID |
|------|---------|
| 📧 郵箱 | scott365888@gmail.com |
| 💬 微信 | PTS9800 |
