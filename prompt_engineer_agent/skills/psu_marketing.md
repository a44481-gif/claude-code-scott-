# PC電源全球營銷團隊提示詞技能

## 功能說明

這是一套為 **PC電源（550W~2000W）全球營銷團隊** 設計的提示詞系統，支持：

- 🌍 **多語言市場開發**：英文、德文、法文、西班牙文、俄文、阿拉伯文、中文
- 📝 **全流程營銷內容**：開發信、產品介紹、報價談判、展會準備
- 💰 **商業變現**：從線索到成交的完整話術
- 📊 **效果追蹤**：KPI監控與優化建議

## 使用方式

### 快速生成開發信

```
我要開發 Corsair 這個客戶，他們主要做高端電源，
功率段 750W-1200W，目標市場是北美和歐洲。
給我寫3個版本的開發信。
```

### 生成產品介紹

```
我有一款 1000W 白金牌電源，通過 80+ Platinum 認證，
全模組化設計，請生成英文和中文的產品介紹。
```

### 製作報價方案

```
有個客戶想要 1000 台 750W Gold 電源，
目標價是 85 USD/台，FOB 深圳，請給我報價方案和談判話術。
```

### 展會準備

```
我們要參加 Computex 2026，目標是接觸全球電源品牌客戶，
請幫我準備：接待話術、開發信、樣品推薦、FAQ。
```

## 團隊Agent架構

```
pc_power_marketing_team
├── research_agent      → 市場調研（目標客戶情報）
├── content_agent       → 內容創作（多語言營銷文案）
├── sales_agent         → 客戶開發（B2B開發信、跟進）
├── pricing_agent       → 報價談判（價格策略、合同條款）
├── analytics_agent     → 數據分析（KPI追蹤、優化建議）
├── product_agent       → ⭐ 產品規劃（新產品立項、規格定義）
└── competitor_agent    → ⭐ 競品分析（深度拆解、方案對比）
```

## 提示詞分類

### 🌍 市場調研類
- `psu_market_research` - 全球市場分析
- `psu_competitor_intel` - 競爭對手情報
- `psu_customer_profile` - 客戶畫像構建

### 📝 內容創作類
- `psu_lead_email` - B2B開發信
- `psu_product_intro` - 產品介紹
- `psu_social_media` - 社交媒體內容
- `psu_case_study` - 成功案例包裝

### 🤝 銷售谈判類
- `psu_quotation` - 報價單生成
- `psu_negotiation` - 談判話術
- `psu_objection_handling` - 反對意見處理

### 📊 數據分析類
- `psu_performance_review` - 銷售業績分析
- `psu_market_trends` - 市場趨勢解讀
- `psu_roi_calculator` - ROI計算

### 🔬 產品規劃類（新增）
- `psu_product_launch` - 新產品立項分析
- `psu_roadmap` - 產品路線圖規劃
- `psu_spec_definition` - 規格定義與成本測算

### 🎯 競品分析類（新增）
- `psu_competitor_deep_dive` - 競品深度拆解
- `psu_solution_comparison` - 多供應商方案對比
- `psu_battle_card` - 競爭策略卡（銷售武器）

## 產品知識庫

| 功率段 | 認證 | 應用場景 | 目標客戶 |
|-------|------|---------|---------|
| 550-650W | 80+ Bronze | 入門辦公 | 品牌入門系列 |
| 750-850W | 80+ Gold | 主流遊戲 | 經銷商、分銷商 |
| 1000-1200W | 80+ Platinum | 高端遊戲/工作站 | 系統整合商 |
| 1500-2000W | 80+ Titanium | 旗艦/挖礦/AI | OEM/ODM |

## 聯絡窗口

| 渠道 | 地址/ID |
|------|---------|
| 📧 郵箱 | scott365888@gmail.com |
| 💬 微信 | PTS9800 |

---

## 觸發關鍵詞

- "PC電源營銷"、"電源開發信"、"PSU報價"
- "Computex"、"電源展會"、"計算機展"
- "電源品牌"、"電源經銷商"、"電源工廠"
- "80+ Gold"、"80+ Platinum"、"80+ Titanium"
- "電源OEM"、"電源ODM"、"電源定制"
- "競品分析"、"產品立項"、"方案對比"、"打敗競爭對手"

## 執行命令

```bash
# 生成開發信
python run.py --mode design --task "psu_lead_email" --context '{"target":"Corsair","market":"North America"}'

# 生成報價
python run.py --mode design --task "psu_quotation" --context '{"product":"750W Gold","quantity":1000}'

# 展會準備
python run.py --mode design --task "psu_trade_show" --context '{"event":"Computex 2026"}'

# 競品深度分析
python run.py --mode design --task "psu_competitor_deep_dive" --context '{"competitor":"Seasonic","product_model":"SSR-1000TR"}'

# 產品立項分析
python run.py --mode design --task "psu_product_launch" --context '{"wattage_range":"1000-1200W","certifications":"Platinum"}'

# 方案對比評估
python run.py --mode design --task "psu_solution_comparison" --context '{"products":["方案A","方案B","方案C"],"quantity":3000}'

# 查看所有模板
python run.py --mode library --category team
```

## 輸出示例

### 開發信輸出
```markdown
Subject: Partnering for Premium Power - 80+ Gold PSU Supply

Dear [Name],

As the global PSU market evolves toward higher efficiency standards,
[Your Company] stands ready as your trusted manufacturing partner...

[完整內容含3個版本]
```

### 報價單輸出
```json
{
  "product": "750W Gold",
  "unit_price": "USD 82",
  "quantity": 1000,
  "total": "USD 82,000",
  "incoterms": "FOB Shenzhen",
  "payment": "T/T 30% deposit",
  "lead_time": "25-30 days",
  "validity": "30 days"
}
```
