# PSU 每日市場報告自動化

全自動收集京東、天貓、Amazon 電源供應器（PSU）銷售數據，經 MiniMax AI 分析後 Email 寄送。

## 目標品牌

華碩 (ASUS) / 技嘉 (GIGABYTE) / 微星 (MSI) / 海盜船 (Corsair) / 海韻 (Seasonic) / Antec / 酷冷至尊 (Cooler Master) / BQT / 九州風神 (DeepCool) / 聯力 (Lian Li)

## 專案結構

```
psu_daily_report/
├── config.yaml              # ⚙️ 設定檔（請填入 API Key）
├── requirements.txt         # Python 依賴
├── run_daily.py             # 🏃 主執行腳本
├── scheduler_setup.ps1      # ⏰ Windows 工作排程器設定
├── crawlers/
│   ├── base_crawler.py      # 爬蟲基類
│   ├── jd_crawler.py        # 京東爬蟲
│   ├── amazon_crawler.py    # Amazon 爬蟲
│   └── tmall_crawler.py     # 天貓爬蟲
├── analysis/
│   └── ai_analyzer.py       # MiniMax AI 分析器
├── notification/
│   └── email_sender.py      # Email 發送器
└── reports/                 # 📁 報告輸出目錄（自動建立）
```

## 快速開始

### 1. 安裝依賴

```bash
cd psu_daily_report
pip install -r requirements.txt
```

### 2. 填寫設定檔 `config.yaml`

```yaml
# MiniMax API（申請：https://platform.minimax.chat/）
minimax:
  api_key: "你的 MiniMax API Key"

# 163.com SMTP（需開通 POP3/SMTP 並取得授權碼）
email:
  sender: "h13751019800@163.com"
  password: "你的163授權碼"
  recipient: "h13751019800@163.com"
```

> 163.com 授權碼取得方式：登入網頁版 163 郵箱 → 設定 → POP3/SMTP/IMAP → 開通並取得授權碼

### 3. 立即測試一次

```bash
python run_daily.py
```

### 4. 設定每日自動執行

```powershell
# 以系統管理員身份執行 PowerShell
Set-ExecutionPolicy -Scope RemoteSigned -Force
.\scheduler_setup.ps1
```

預設每天早上 **09:00** 執行。若要修改時間，編輯 `config.yaml` 中的 `schedule.time`，或：
```powershell
.\scheduler_setup.ps1 -RunTime "08:30"
```

## 常用指令

```powershell
# 手動觸發一次
Start-ScheduledTask -TaskName "PSU_DailyReport"

# 查看下次執行時間
Get-ScheduledTask -TaskName "PSU_DailyReport" | Get-ScheduledTaskInfo

# 刪除排程
Unregister-ScheduledTask -TaskName "PSU_DailyReport" -Confirm:$false
```

## 手動模式

```bash
# 只收集數據（不分析不寄送）
python run_daily.py --mode collect

# 只做分析（讀取上次數據）
python run_daily.py --mode analyze
```

## 疑難排解

**Q: 爬蟲收集不到數據？**
京東/天貓有反爬機制，正式環境建議配合代理 IP 使用。可在 `config.yaml` 中設定代理，或改用 Playwright/Selenium。

**Q: MiniMax API Key 怎麼拿？**
到 https://platform.minimax.chat/ 註冊即可取得。

**Q: 163.com SMTP 發送失敗？**
確認使用了「授權碼」而非登入密碼，且已開通 SMTP 服務。
