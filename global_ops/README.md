# GlobalOPS · 统一短剧出海自动运营平台

[![Daily Content](https://github.com/YOUR_USER/global_ops/actions/workflows/daily_content.yml/badge.svg)](https://github.com/YOUR_USER/global_ops/actions/workflows/daily_content.yml)
[![Deploy](https://github.com/YOUR_USER/global_ops/actions/workflows/deploy.yml/badge.svg)](https://github.com/YOUR_USER/global_ops/actions/workflows/deploy.yml)

多平台（YouTube / TikTok / Instagram）全流程自动运营系统。

## 系统架构

```
GlobalOPS
├── python_engine/       Python 执行引擎（视频处理/上传/分析）
├── content_engine/      Node.js 内容生成（题材/文案/标签）
├── n8n_workflows/       n8n 工作流（调度/通知/报表）
├── database/            PostgreSQL Schema
├── config/               平台配置/环境变量
├── scripts/              初始化/迁移脚本
├── .github/workflows/    GitHub Actions CI/CD
└── docker-compose.yml   一键启动
```

## 快速启动

### 本地开发
```bash
# 复制环境变量
cp config/.env.example config/.env
# 填写 .env 中的凭证

# 启动数据库
docker compose up -d postgres redis

# 安装依赖
pip install -r python_engine/requirements.txt
cd content_engine && npm install && cd ..

# 运行迁移
PGPASSWORD=xxx psql -h localhost -U postgres -d global_ops \
  -f database/migrations/001_initial_schema.sql

# 启动 n8n（可选）
docker compose up -d n8n
```

### 一键启动
```bash
# Windows
.\scripts\start.bat

# Linux/Mac
bash scripts/start.sh
```

## 核心命令

```bash
# 生成内容（10条，存入DB）
node content_engine/src/generator.js --db --count=10

# 查看内容库统计
node content_engine/src/manager.js stats

# 发布到 YouTube
python python_engine/main.py publish --platform youtube --limit=3

# 查看收益报表
python python_engine/main.py revenue --days=30

# 查看数据分析
python python_engine/main.py analytics --days=7

# 添加平台账号
python python_engine/main.py add-account \
  --platform youtube --account-id yaoweiba3300 \
  --account-name "Manhua Sharing" --region global

# 数据迁移（从 manhua-system 迁入）
python scripts/migrate_content.py
```

## 自动调度

### n8n 工作流（本地）
| 工作流 | 触发时间 | 功能 |
|--------|----------|------|
| `daily_content_trigger` | 每天 08:00 | 生成10条内容入库 |
| `multi_platform_publish` | 每天 12:00 & 20:30 | 发布到 YouTube/TikTok |
| `weekly_report` | 每周一 09:00 | 发送周报（飞书+邮件）|

### GitHub Actions（云端，无需 VPS）
| 工作流 | 触发 | 功能 |
|--------|------|------|
| `daily_content.yml` | 每天 00:00 UTC | 生成+发布+通知 |
| `weekly_report.yml` | 每周一 01:00 UTC | 周报生成 |
| `deploy.yml` | push main | CI/CD 部署 |

## 数据库表

| 表 | 用途 |
|----|------|
| `content_items` | 统一内容库 |
| `publish_log` | 发布记录 |
| `platform_accounts` | 账号矩阵 |
| `scheduled_tasks` | 调度任务 |
| `daily_revenue` | 每日收益 |
| `copyright_risks` | 版权风险 |
| `daily_stats` | 每日统计 |
| `content_themes` | 题材模板库（60条）|

## 技术栈

| 层次 | 技术 |
|------|------|
| 调度层 | n8n 1.60 (Docker) |
| CI/CD | GitHub Actions |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 内容生成 | Node.js 20 + AI API |
| 视频处理 | Python 3.11 + FFmpeg |
| 发布 | YouTube API v3 + Selenium |

## 平台支持

| 平台 | 状态 | 上传方式 |
|------|------|----------|
| YouTube | ✅ 已实现 | API / Selenium |
| TikTok | 🔄 开发中 | Selenium |
| Instagram | 🔄 开发中 | Graph API |
| Facebook | 🔄 开发中 | Creator Studio |
| Pinterest | 🔄 规划中 | Pinterest API |

## 配置

在 `config/.env` 中配置：

```bash
# 数据库
POSTGRES_HOST=localhost
POSTGRES_DB=global_ops
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# AI
ANTHROPIC_API_KEY=sk-ant-xxx
DEEPL_API_KEY=xxx

# 通知
LARK_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# YouTube（可选，有 Cookie 可用 Selenium 降级）
YOUTUBE_CLIENT_ID=xxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=xxx
YOUTUBE_REFRESH_TOKEN=1//xxx
```
