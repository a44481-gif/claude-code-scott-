# IT Hardware Daily Report Automation System (IT 日報)

## 項目目標
Build an automated daily report system for IT hardware (PSU/顯示卡/筆電) that:
1. Collects data from multiple e-commerce platforms (京東/天貓/Amazon/Newegg)
2. Generates AI-powered analysis via MiniMax API
3. Sends精美 HTML report via email (163/QQ/Outlook)
4. Scheduled to run automatically every morning

## 現有可复用組件
- ✅ `msi_psu_automation/` — crawler base classes, AI analyzer, email sender
- ✅ `psu_daily_report/` — httpx crawlers for JD/Tmall/Amazon
- ✅ `email_sender.py`, `send_email_v2.py` — SMTP email with attachments
- ✅ `MiniMaxAnalyzer` in `ai_pc_deep_analysis.py` — AI + local fallback
- ✅ `generate_report.py` — HTML report generation with brand data
- ✅ `settings.json` / `email_config.json` — config patterns

---

## 實施計劃

### Phase 1：項目框架搭建（第 1 天）
- [ ] 創建 `it_daily_report/` 目錄結構
- [ ] 配置 `config/settings.json` 和 `email_config.json`
- [ ] 配置 `requirements.txt`
- [ ] 實現 `crawlers/base_crawler.py`（复用現有 httpx 模式）
- [ ] 實現 `analysis/ai_analyzer.py`（MiniMax + local fallback）
- [ ] 實現 `notification/email_sender.py`

### Phase 2：爬蟲模組（第 2 天）
- [ ] 實現 `crawlers/jd_crawler.py`（京東）
- [ ] 實現 `crawlers/tmall_crawler.py`（天貓）
- [ ] 實現 `crawlers/amazon_crawler.py`（Amazon US/CN/TW）
- [ ] 實現 `crawlers/newegg_crawler.py`（Newegg）
- [ ] 測試各爬蟲模組

### Phase 3：報告生成與 AI 分析（第 3 天）
- [ ] 實現 `reporting/html_generator.py`（精美 HTML 報告）
- [ ] 整合 AI 分析到報告流程
- [ ] 實現 `run_daily.py` 主入口
- [ ] 端到端測試（爬蟲→分析→報告→郵件）

### Phase 4：自動化部署（第 4-5 天）
- [ ] 配置 Windows Task Scheduler 每日執行
- [ ] 實現 `test_crawlers.py` 測試腳本
- [ ] 撰寫使用文檔
- [ ] 交付驗收

---

## 項目結構

```
it_daily_report/
├── config/
│   ├── settings.json         # 系統配置 + 定時調度
│   ├── email_config.json     # SMTP + 收件人
│   └── brands.json           # 品牌 + 關鍵詞
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py        # 抽象基類（httpx + retry）
│   ├── jd_crawler.py          # 京東
│   ├── tmall_crawler.py       # 天貓
│   ├── amazon_crawler.py      # Amazon
│   └── newegg_crawler.py      # Newegg
├── analysis/
│   ├── __init__.py
│   └── ai_analyzer.py         # MiniMax API + 本地統計回退
├── reporting/
│   ├── __init__.py
│   ├── html_generator.py      # HTML 報告生成
│   └── templates/             # Jinja2 模板
├── notification/
│   ├── __init__.py
│   └── email_sender.py        # 統一郵件發送器
├── run_daily.py               # CLI 入口
├── test_crawlers.py           # 測試腳本
└── requirements.txt
```

---

## 核心模組設計

### 1. 數據收集（Crawlers）
| 爬蟲 | 目標平台 | 收集內容 |
|------|----------|----------|
| `jd_crawler.py` | 京東 | 電源/顯卡/筆電 價格、銷量、品牌 |
| `tmall_crawler.py` | 天貓 | 同上 |
| `amazon_crawler.py` | Amazon US/CN | 同上 + 評分 |
| `newegg_crawler.py` | Newegg | 同上 |

**复用策略**：直接复用 `psu_daily_report/crawlers/` 的 httpx + BeautifulSoup 架構。

### 2. AI 分析引擎（Analysis）
使用 MiniMax API（與現有 `psu_daily_report` 相同），執行：
- 市場趨勢分析
- 價格區間分析
- 品牌競爭力評估
- 重點產品推薦

### 3. HTML 報告內容
1. 執行摘要（關鍵指標卡片）
2. AI 市場洞察
3. 平台數據對比表格
4. 暢銷產品排行
5. 價格趨勢圖
6. 建議行動

### 4. 郵件發送
- SMTP SSL（163.com）- 發送至指定收件人
- 支持 HTML 正文 + JSON 附件

---

## 技術棧

| 層面 | 技術 |
|------|------|
| 爬蟲 | `httpx` + `BeautifulSoup` + `lxml` |
| AI 分析 | MiniMax `chatcompletion_v2` API |
| 郵件 | SMTP SSL（163.com/QQ） |
| 報告 | HTML + CSS（自定義样式）|
| 調度 | Windows Task Scheduler |

---

## 與現有系統的复用關係

| 現有組件 | 复用方式 |
|----------|----------|
| `psu_daily_report/crawlers/base_crawler.py` | 直接复用 httpx 架構 |
| `psu_daily_report/analysis/ai_analyzer.py` | 直接复用 MiniMax 調用模式 |
| `email_sender.py` | 直接复用 SMTP 郵件發送 |
| `generate_report.py` | 参考 HTML 報告樣式 |
| `ai_pc_deep_analysis.py` | MiniMaxAnalyzer 模式 |

---

## 交付物清單

1. `it_daily_report/` 完整代碼
2. 定時任務配置（每日自動執行）
3. 首份 IT 硬體每日報告（HTML + 郵件）
4. 使用文檔

---

## 風險評估

| 風險 | 緩解策略 |
|------|----------|
| 電商平台反爬 | 使用 httpx + 隨機 User-Agent + 延遲 |
| API Key 缺失 | 本地統計回退（local_analyzer.py）|
| 郵件送達率 | 添加 SPF/DKIM + 白名單 |
| 數據質量 | 去重 + 異常值過濾 |
