# 全球 PSU 每日自動化報告系統

> 收集全球 35+ 電商平台 PSU 電源供應器銷售數據，AI 分析，自動發送每日 PPT 報告至指定郵箱

## 功能概覽

| 模組 | 說明 |
|------|------|
| 🌐 數據收集 | 覆蓋全球 35+ 電商平台的 PSU 爬蟲 |
| 🤖 AI 分析 | MiniMax API 驅動的全球市場深度分析 |
| 📊 PPT 報告 | 自動生成 9 頁專業 PowerPoint 報告 |
| 📧 自動郵寄 | 每日 9:00 自動發送至指定郵箱 |
| ⏰ 定時執行 | Windows Task Scheduler 每日自動運行 |

## 支援平台

### 北美
- Amazon US, Amazon Canada
- Newegg, Best Buy US, Best Buy Canada

### 歐洲
- Amazon DE, Amazon UK
- MediaMarkt, Saturn

### 俄羅斯
- Ozon, Wildberries, Yandex Market

### 中國
- 京東, 天貓, 淘寶

### 台灣
- PChome 24h, Momo 購物網

### 日本
- Amazon JP, 樂天市場

### 韓國
- Gmarket, Coupang

### 印度
- Flipkart, Amazon.in

### 東南亞
- Shopee (泰/越/印尼/馬/菲), Lazada (泰/越/印尼/馬), Tokopedia

### 南美
- Mercado Libre (阿根廷/巴西/墨西哥)

### 中東
- Noon, Amazon UAE

## 快速開始

### 1. 安裝依賴

```bash
cd psu_global_report
pip install -r requirements.txt
```

### 2. 配置設定

編輯 `config.yaml`，填入：
- `minimax.api_key`: MiniMax API Key
- `email.password`: 163 郵箱授權碼

### 3. 測試運行

```bash
# 完整流程（收集+分析+PPT+郵寄）
python run_daily.py

# 只收集數據
python run_daily.py --mode collect

# 分析+PPT+郵寄（使用上次數據）
python run_daily.py --mode analyze
```

### 4. 設定每日自動執行

以**系統管理員身份**執行 PowerShell：

```powershell
cd d:\claude mini max 2.7\psu_global_report
.\scheduler_setup.ps1
```

## 依賴套件

```
httpx>=0.27.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
pyyaml>=6.0.1
python-pptx>=0.6.23
```

## ⚠️ 注意事項

- 部分平台（Ozon、Wildberries、Coupang 等）使用 JavaScript 渲染，需要 **Playwright** 才能穩定抓取
- 163.com 郵箱需要使用「授權碼」而非登入密碼
- 建議首次運行使用 `--mode collect` 確認數據收集正常

## 平台備註

| 平台 | 狀態 | 說明 |
|------|------|------|
| 京東/天貓/淘寶 | ✅ 直接可用 | HTTP 抓取 |
| Amazon 各站 | ✅ 直接可用 | HTTP 抓取 |
| PChome/Momo | ✅ 直接可用 | HTTP 抓取 |
| Newegg/BestBuy | ✅ 直接可用 | HTTP 抓取 |
| MediaMarkt/Saturn | ⚠️ 可能需 Playwright | JS 渲染 |
| Rakuten | ⚠️ 可能需 Playwright | JS 渲染 |
| Shopee/Lazada | ⚠️ 建議 Playwright | JS 渲染 |
| Ozon/Wildberries | 🔴 建議 Playwright/API | 強反爬 |
| Coupang | 🔴 建議 Playwright | 強反爬 |
