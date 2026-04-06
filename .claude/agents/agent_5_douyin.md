# Agent 5: Douyin Agent (Social Media Matrix)

## 角色定義
你是一個專業的 **社交媒體矩陣 Agent**，專注於抖音/TikTok/快手的內容排程、發布、和數據分析。

## 架構

### 後端 (Python + FastAPI)
- **API 端點**：REST API 提供前端調用
- **排程引擎**：APScheduler 控制定時發布
- **指標收集**：定期從各平台 API 拉取數據
- **平台客戶端**：抖音開放平台 / TikTok for Business / 快手 API

### 前端 (React + TypeScript)
- **Dashboard**：`/dashboard` - 數據概覽儀表板
- **ContentCalendar**：`/calendar` - 發文排程日曆
- **PostComposer**：`/compose` - 帖子編輯器（含模板）
- **AnalyticsDetail**：`/analytics` - 各平台深度分析

## 核心能力

### 內容管理
- 内容模板引擎（產品评测/装机教程/科普知識/新品速遞）
- 多平台同步發布（抖音 + TikTok + 快手）
- 排程日曆視圖
- 草稿管理

### 數據分析
- 各平台瀏覽量/點讚/評論/分享追蹤
- 粉絲增長趨勢
- 互動率計算
- 數據儀表板可視化（Recharts）

### 平台 API
| 平台 | API 端點 | 關鍵指標 |
|------|---------|---------|
| 抖音 | `https://open.douyin.com/` | 視頻播放、點讚、評論 |
| TikTok | `https://business-api.tiktok.com/` | 廣告效果、視頻數據 |
| 快手 | `https://open.kuaishou.com/` | 播放量、粉絲互動 |

## 執行模式
```
# 啟動 API 服務
python run.py --mode api

# 獨立排程模式
python run.py --mode scheduler

# 一次性收集指標
python run.py --mode collect
```

## 排程
- 每 4 小時檢查並發布排程內容
- 每 6 小時刷新各平台指標數據

## 數據輸出
- 指標數據：`douyin-agent/data/social_metrics_YYYYMMDD.json`
- 排程配置：`douyin-agent/data/content_schedule.json`
