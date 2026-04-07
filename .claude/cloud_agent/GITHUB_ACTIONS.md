# CoBM GitHub Actions 自動化部署

使用 GitHub Actions 實現雲端自動化，全流程在 GitHub 伺服器運行。

## 🎯 架構

```
本地觸發 ──▶ GitHub Actions ──▶ 雲端執行
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
         數據爬蟲            AI 分析            報告生成
              │                  │                  │
              ▼                  ▼                  ▼
         market_data        analysis.md        PPT 報告
              │                  │                  │
              └──────────────────┴──────────────────┘
                                 │
                                 ▼
                          發送郵件
                          scott365888@gmail.com
```

## 📋 功能

| 觸發方式 | 說明 |
|---------|------|
| **定時執行** | 每天 UTC 1:00 (北京 9:00) 自動生成報告 |
| **手動觸發** | GitHub Actions 頁面點擊 "Run workflow" |
| **Push 觸發** | 推送代碼時自動測試 |

## 🚀 部署步驟

### 1. 建立 GitHub 倉庫

```bash
# 本地初始化
cd cloud_agent
git init
git add .
git commit -m "Initial commit"

# GitHub 建立倉庫後
git remote add origin https://github.com/YOUR_USERNAME/cobm-agent.git
git push -u origin main
```

### 2. 配置 Secrets

在 GitHub 倉庫 Settings → Secrets and variables → Actions 添加：

| Secret 名稱 | 值 | 說明 |
|------------|-----|------|
| `CLAUDE_API_KEY` | sk-ant-xxxxx | Claude API Key (可選，否則用演示模式) |
| `SMTP_AUTH_CODE` | xxxxx | Gmail App Password |
| `GMAIL_USER` | scott365888@gmail.com | 發件郵箱 |

### 3. 啟用 Actions

1. 前往 GitHub 倉庫
2. 點擊 "Actions" 頁面
3. 選擇 "CoBM Daily Report Automation"
4. 點擊 "Enable workflow"

### 4. 手動觸發測試

1. 前往 Actions 頁面
2. 點擊 "CoBM Daily Report Automation"
3. 點擊 "Run workflow"
4. 選擇報告類型並點擊 "Run workflow"

## 📁 生成的報告

| 報告類型 | 格式 | 說明 |
|---------|------|------|
| 市場數據 | JSON | GPU/電源市場動態 |
| AI 分析 | Markdown | Claude 分析結果 |
| PPT 報告 | PPTX | 完整演示報告 |

## ⏰ 定時設置

預設每天 UTC 1:00 (北京 9:00) 執行：

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 1:00
```

修改為其他時間：

| 時間 (北京) | cron 表達式 |
|-----------|------------|
| 早上 9:00 | `0 1 * * *` |
| 中午 12:00 | `0 4 * * *` |
| 下午 6:00 | `0 10 * * *` |
| 晚上 9:00 | `0 13 * * *` |

## 🔧 自定義報告類型

在手動觸發時選擇：

| 類型 | 說明 |
|------|------|
| `daily` | 每日市場動態 |
| `weekly` | 每週深度分析 |
| `full_pipeline` | 完整流程 |

## 📊 工作流程日誌

每次執行都會生成詳細日誌，可在 Actions 頁面查看：

1. 數據爬蟲 ✅
2. AI 分析 ✅
3. PPT 生成 ✅
4. 郵件發送 ✅

## 🔒 安全建議

1. **API Key 安全**：使用 GitHub Secrets，不要將 Key 寫入代碼
2. **郵箱驗證**：Gmail 需要 App Password，不是登錄密碼
3. **權限最小化**：Actions 僅需讀寫 contents 權限

## ❓ 常見問題

**Q: GitHub Actions 有使用限制嗎？**
A: 免費版每月 2000 分鐘，私有倉庫 500 分鐘。

**Q: 如何調整執行頻率？**
A: 修改 `.github/workflows/cobm_automation.yml` 中的 cron 表達式。

**Q: 報告發送到哪裡？**
A: 目前固定發送到 scott365888@gmail.com，可在 workflow 中修改。

**Q: 需要 Claude API Key 嗎？**
A: 不需要，系統會使用演示模式生成基本報告。

## 📞 聯絡窗口

- **Email**: scott365888@gmail.com
- **微信**: pts9800
