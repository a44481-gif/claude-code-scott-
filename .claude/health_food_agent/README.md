# 健康食品 AI 扩客代理人

自动化健康食品跨境销售代理系统，支持台湾市场拓展。

## 功能特性

- **数据收集**: 淘宝/1688/虾皮多平台产品爬虫
- **AI分析**: MiniMax API 市场趋势分析
- **智能选品**: 基于多维度评分的产品推荐
- **供应商评估**: 综合评分系统
- **定价策略**: 成本+运费+关税+利润自动计算
- **渠道规划**: 线上线下多渠道策略
- **报告生成**: HTML格式可视化报告
- **邮件发送**: SMTP + 飞书邮件双轨发送
- **定时任务**: APScheduler自动调度

## 快速开始

```bash
cd health_food_agent

# 安装依赖
pip install -r requirements.txt

# 测试模式
python run.py --mode test

# 完整执行
python run.py --mode full

# 定时调度
python run.py --mode scheduler
```

## 配置

编辑 `config/settings.json` 和 `config/email_config.json`:
- MiniMax API Key
- 163.com SMTP 密码
- 飞书应用配置

## 目录结构

```
health_food_agent/
├── config/          # 配置文件
├── src/
│   ├── data_collection/  # 爬虫模块
│   ├── analysis/         # AI分析
│   ├── operations/       # 运营决策
│   ├── reporting/        # 报告生成
│   ├── database/         # 数据库
│   ├── scheduling/       # 调度器
│   └── automation/       # 自动化执行
├── reports/         # 生成的报告
├── data/           # 原始数据
└── run.py          # 主入口
```
