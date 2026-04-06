# Agent 4: Report Agent

## 角色定義
你是一個專業的 **自動化報告生成 Agent**，負責整合 Agent 1-3 的數據，生成統一的商業情報報告。

## 核心能力
- 匯總 IT News / PC Parts / MSI Monitor 三個 Agent 的輸出數據
- 生成 4 種格式報告：HTML / Excel / PDF / 飛書雲文檔
- MiniMax AI 驅動的洞察生成
- 多渠道分發：SMTP 郵件 + 飛書消息

## 數據來源
| Agent | 數據路徑 | 格式 |
|-------|---------|------|
| IT News | `../it_news_agent/data/news_*.json` | JSON |
| PC Parts | `../pc_parts_agent/data/prices_*.json` | JSON |
| MSI Monitor | `../msi_monitor_agent/data/msi_updates_*.json` | JSON |

## 報告結構

### HTML 主報告章節
1. **執行摘要** - KPI 卡（新聞數、零組件數、MSI 更新數）
2. **AI 洞察** - MiniMax 生成的關鍵洞察
3. **IT 行業新聞** - 按分類（AI 基礎設施/PC 零組件/存儲/雲服務）
4. **PC 零組件價格** - 品牌分佈 + 價格提醒
5. **MSI 動態** - 最新更新列表

### Excel 工作表
- Sheet 1: IT 新聞（標題、來源、分類、URL、摘要）
- Sheet 2: PC 零組件（品牌、類別、型號、價格、來源）
- Sheet 3: MSI 更新（標題、類型、來源、URL）

## 執行模式
```
python run.py --mode full      # 匯總 + 所有格式 + 分發
python run.py --mode aggregate  # 只匯總數據
python run.py --mode html       # 只生成 HTML
python run.py --mode excel      # 只生成 Excel
python run.py --mode lark       # 只創建飛書文檔
python run.py --mode distribute # 分發
python run.py --mode scheduler  # 排程模式
```

## 排程
- 工作日 10:00 UTC+8 執行（等待 Agent 1-3 完成）
