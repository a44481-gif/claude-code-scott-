# ============================================================
# GPU 電源線燒毀研究工具套件
# GPU Power Cable Burn Research Toolkit
# ============================================================

## 📁 目錄結構

```
gpu_research/
├── docs/                           # 文檔目錄
│   ├── gpu_report_complete.html    # 完整研究報告 (HTML)
│   └── gpu_case_database.json      # 案例數據庫 (JSON)
├── src/                            # 源碼目錄
│   ├── __init__.py
│   ├── config.py                   # 配置管理
│   ├── collector.py                # 資料收集器
│   ├── generator.py                # 報告生成器
│   ├── sender.py                   # 郵件發送器
│   └── lark_sync.py                # 飛書同步工具
├── skills/                         # Skill 目錄
│   └── lark-gpu-research/          # 增強版 Skill
│       ├── skill.yaml
│       ├── README.md
│       └── prompt.md
├── main.py                         # 主程序入口
├── requirements.txt                # 依賴
└── README.md                       # 說明文檔
```

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 配置
編輯 `src/config.py`:
```python
# 郵箱配置
SMTP_HOST = 'smtp.163.com'
SMTP_PORT = 465
SENDER_EMAIL = 'your_email@163.com'
SENDER_AUTH_CODE = 'your_auth_code'

# 飛書配置
LARK_APP_ID = 'your_app_id'
LARK_APP_SECRET = 'your_app_secret'
LARK_DOC_TOKEN = 'your_doc_token'

# 研究配置
RESEARCH_TOPICS = [
    'RTX 4090 12VHPWR 熔化',
    '顯卡供電接口燒毀',
    'GPU power connector burn'
]
```

### 運行主程序
```bash
python main.py
```

## 📋 功能模組

### 1. 資料收集器 (collector.py)
- 從多個平台收集案例數據
- 支持: Reddit, Tom's Hardware, 知乎, Bilibili, etc.
- 自動去重和分類

### 2. 報告生成器 (generator.py)
- 生成 HTML 研究報告
- 統計分析
- 可視化圖表

### 3. 郵件發送器 (sender.py)
- SMTP 郵箱發送
- 支持 HTML 格式
- 附件支持

### 4. 飛書同步工具 (lark_sync.py)
- 飛書文檔創建/更新
- 案例數據同步
- 多維表格支持

## 🔧 使用範例

### 完整流程
```python
from src.collector import GPUCollector
from src.generator import ReportGenerator
from src.sender import EmailSender

# 1. 收集數據
collector = GPUCollector()
cases = collector.collect_all()

# 2. 生成報告
generator = ReportGenerator()
report = generator.generate_html(cases)

# 3. 發送郵件
sender = EmailSender()
sender.send_report(report)
```

### 單獨使用
```python
# 只收集數據
collector = GPUCollector()
cases = collector.collect_all()
print(f"收集到 {len(cases)} 個案例")

# 只生成報告
generator = ReportGenerator()
report = generator.generate_html(cases)
generator.save_report(report, 'report.html')

# 只發送郵件
sender = EmailSender()
sender.send_email('主題', report, ['recipient@example.com'])
```

## 📊 案例數據格式

```json
{
  "case_id": "RTX-CN-001",
  "platform": "知乎",
  "region": "中國",
  "gpu_model": "RTX 4090",
  "issue_type": "12VHPWR接口熔化",
  "description": "使用第三方轉接線導致接口燒毀",
  "root_cause": "轉接線質量問題",
  "solution": "更換原廠線材",
  "status": "已解決",
  "date": "2024-06-15",
  "source": "https://zhihu.com/..."
}
```

## ⚠️ 注意事項

- WebSearch 工具可能需要權限
- 飛書 API 需要有效的 App ID 和 Secret
- 郵箱需要開通 SMTP 服務

## 📝 更新日誌

### v2.0.0 (2026-04-06)
- 完全重寫代碼架構
- 增加增強版 Skill
- 添加飛書同步功能
- 改善錯誤處理

### v1.0.0 (2026-04-03)
- 初始版本
- 基本報告生成
- 郵件發送功能

## 📧 聯繫

如有问题请联系: h13751019800@163.com

## 📄 許可證

MIT License
