# 双AI代理系统 - 京东电竞游戏本数据分析

## 系统概述
双AI代理协作系统，用于抓取京东JD.com电竞游戏本数据并生成分析报告。

## 文件结构
```
.claude/
├── jd_crawler.py        # 代理A：爬虫模块
├── jd_analyst.py        # 代理B：分析师模块
└── skills/
    ├── SKILL.md         # 本技能文档
    └── AGENTS_README.md # PPT分析技能说明
```

## 代理A：爬虫模块 (jd_crawler.py)

### 功能
- 多策略爬取：requests → playwright → 模拟数据降级
- 品牌覆盖：ROG玩家国度、MSI微星、联想拯救者、HP暗影精灵、外星人Alienware
- 智能数据清洗：GPU等级标签、屏幕标签、价格段标签等
- 反爬策略：User-Agent池（20+条）、Cookie轮换、指数退让重试

### 使用方法
```bash
# 全自动（依次尝试所有策略）
python jd_crawler.py

# 强制使用模拟数据（最快）
python jd_crawler.py --force-mock

# 指定策略
python jd_crawler.py --force-strategy playwright

# 仅检测可用策略
python jd_crawler.py --check
```

### 输出
- `jd_gaming_laptops_raw.json` - 原始数据（550条商品）
- `jd_crawler.log` - 运行日志

---

## 代理B：分析师模块 (jd_analyst.py)

### 功能
- 数据统计分析：品牌对比、价格分布、市场份额
- 销量TOP10分析
- 性价比指数分析（新增）
- 8+Sheet Excel报告（含图表）
- HTML邮件自动发送

### 使用方法
```bash
# 默认运行（生成报表+发送邮件）
python jd_analyst.py

# 指定输入文件
python jd_analyst.py --input my_data.json

# 跳过邮件发送
python jd_analyst.py --skip-email

# 跳过Excel美化
python jd_analyst.py --skip-style
```

### 输出
- `jd_analysis_report.xlsx` - 8+Sheet美化报表
  - 概览总览
  - 品牌对比分析（含柱状图）
  - 价格分布分析（含图表）
  - 销量TOP10
  - 品牌市场份额（含饼图）
  - 显卡型号分布（含横向柱状图）
  - CPU型号分布
  - 性价比TOP10（新增）
  - 品牌性价比指数（新增）
  - 原始数据
- `jd_analysis_summary.txt` - 文字报告摘要

### 邮件配置
- SMTP服务器：smtp.163.com (SSL 465)
- 发件人：h13751019800@163.com
- 收件人：h13751019800@163.com
- 授权码：JWxaQXzrCQCWtPu3

---

## 触发关键词
- "爬取京东"、"抓取数据"、"运行爬虫"
- "生成报告"、"数据分析"、"发送邮件"
- "更新数据"、"刷新报告"

## 依赖
- requests、beautifulsoup4（网页抓取）
- playwright（无头浏览器，可选）
- pandas（数据分析）
- openpyxl（Excel生成与美化）
- smtplib（邮件发送）
- Python 3.8+

## 定时训练
系统每6小时自动训练一次，持续优化代码。
训练日志：`d:\claude mini max 2.7\.claude\training_log.md`
