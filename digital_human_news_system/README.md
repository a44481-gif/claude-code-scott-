# AI数字人新闻内容生产与全球分发系统

## 项目简介

一套完整的AI数字人新闻自动化生产与分发系统，实现从新闻抓取、AI二创、数字人视频生成到多平台发布全流程自动化。

## 功能特性

- **每日自动抓取全球新闻**
  - 定时采集全球公开新闻源
  - 筛选四大领域：佛学正能量、道教正能量、宠物、农业
  - 新闻摘要、去重、分类、情感过滤

- **AI二次创作与剪辑**
  - 基于新闻生成适合短视频的二创文案
  - 自动生成字幕、配音脚本
  - 支持中英文双语内容

- **AI数字人播报**
  - 调用数字人生成接口，生成数字人播报视频
  - 支持多语言：中文、英文
  - 可扩展其他语言

- **多平台自动分发**
  - 发布平台：抖音、YouTube
  - 按语言与赛道分类上传
  - 自动生成标题、标签、封面文案

- **结果通知与日志**
  - 执行完成后自动发送日报邮件
  - 详细执行日志记录

## 目录结构

```
digital_human_news_system/
├── config/
│   └── settings.json          # 配置文件
├── src/
│   ├── news/
│   │   └── news_fetcher.py   # 新闻抓取模块
│   ├── filter/
│   │   └── content_filter.py # 内容筛选模块
│   ├── creator/
│   │   └── ai_creator.py     # AI二创模块
│   ├── human/
│   │   └── digital_human.py  # 数字人视频生成模块
│   ├── publisher/
│   │   └── publisher.py      # 多平台分发模块
│   ├── notifier/
│   │   └── email_notifier.py # 邮件通知模块
│   └── utils/
│       ├── config_loader.py  # 配置加载工具
│       └── logger.py         # 日志工具
├── data/
│   ├── raw/                  # 原始新闻数据
│   ├── processed/            # 处理后数据
│   └── output/               # 输出视频信息
├── logs/                     # 日志文件
├── main.py                   # 主程序入口
├── n8n_webhook.py            # n8n Webhook API服务
├── n8n_workflow_template.json # n8n工作流模板
├── n8n_quick_fetch_workflow.json # 快速抓取工作流
├── n8n_INTEGRATION_GUIDE.md  # n8n集成指南
├── requirements.txt          # 依赖包
├── run.sh                    # Linux/macOS启动脚本
└── run.bat                   # Windows启动脚本
```

## ⚡ n8n 自动化集成

### 启动 n8n Webhook 服务

```bash
# 启动 Webhook 服务器
python n8n_webhook.py --port 8080

# 服务启动后显示:
# 🌐 n8n Webhook服务器启动
#    地址: http://localhost:8080
#    端点:
#    - POST /webhook/trigger  触发完整流程
#    - POST /webhook/fetch    抓取新闻
#    - GET  /health           健康检查
```

### 在 n8n 中导入工作流

1. 打开 n8n (http://localhost:5678)
2. 工作流程 → 从 JSON 导入
3. 选择 `n8n_workflow_template.json`

### Webhook API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/webhook/trigger` | POST | 触发完整工作流 |
| `/webhook/fetch` | POST | 仅抓取新闻 |
| `/webhook/create` | POST | AI二创 |
| `/webhook/generate` | POST | 生成视频 |
| `/webhook/publish` | POST | 发布视频 |
| `/health` | GET | 健康检查 |

详细说明见 [n8n集成指南](n8n_INTEGRATION_GUIDE.md)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置系统

编辑 `config/settings.json` 文件：

```json
{
  "digital_human": {
    "api_url": "你的数字人API地址",
    "api_key": "你的API密钥"
  },
  "email": {
    "sender": "发件邮箱",
    "password": "邮箱授权码",
    "receiver": "收件邮箱"
  },
  "publishing": {
    "douyin": {
      "cookie": "抖音Cookie"
    },
    "youtube": {
      "client_secrets": "youtube_client_secrets.json路径"
    }
  }
}
```

### 3. 运行系统

**完整流程：**
```bash
# Windows
run.bat

# Linux/macOS
chmod +x run.sh
./run.sh
```

**单独模块：**
```bash
python main.py --mode fetch    # 仅抓取新闻
python main.py --mode filter   # 仅筛选内容
python main.py --mode create   # 仅AI二创
python main.py --mode generate # 仅生成视频
python main.py --mode publish  # 仅发布视频
```

**定时任务：**
```bash
python main.py --mode scheduler
```

## 使用说明

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--mode full` | 运行完整流程 |
| `--mode fetch` | 仅抓取新闻 |
| `--mode filter` | 仅内容筛选 |
| `--mode create` | 仅AI二创 |
| `--mode generate` | 仅视频生成 |
| `--mode publish` | 仅平台发布 |
| `--mode scheduler` | 启动定时调度器 |
| `--test` | 测试模式 |
| `--config <path>` | 指定配置文件 |

### 新闻源配置

在 `settings.json` 中配置新闻源：

```json
{
  "news_sources": {
    "buddhism": ["佛学新闻URL1", "佛学新闻URL2"],
    "taoism": ["道教新闻URL1"],
    "pets": ["宠物新闻URL1"],
    "agriculture": ["农业新闻URL1"]
  }
}
```

### 邮箱配置

使用163邮箱时，需要开启SMTP服务并获取授权码：
1. 登录163邮箱
2. 设置 → POP3/SMTP/IMAP
3. 开启SMTP服务
4. 获取授权码

## 扩展开发

### 添加新的数字人API

编辑 `src/human/digital_human.py`，在 `_call_digital_human_api` 方法中添加API调用逻辑。

### 添加新的发布平台

编辑 `src/publisher/publisher.py`，添加新的平台上传方法。

### 自定义内容分类

编辑 `config/settings.json` 中的 `filtering.positive_keywords` 和 `filtering.negative_keywords`。

## 注意事项

1. 首次运行需要配置所有API密钥和授权信息
2. 数字人API和平台发布API需要自行申请
3. 邮件发送需要开启SMTP服务
4. 建议使用虚拟环境运行

## 免责声明

本系统仅供学习和研究使用，请遵守各平台的使用条款和相关法律法规。

## 许可证

MIT License
