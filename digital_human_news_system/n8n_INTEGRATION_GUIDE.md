# n8n 集成指南

## 快速开始

### 1. 启动 Webhook 服务器

```bash
cd digital_human_news_system
python n8n_webhook.py --port 8080
```

### 2. 在 n8n 中导入工作流

1. 打开 n8n (http://localhost:5678)
2. 点击「工作流程」→「从 JSON 导入」
3. 粘贴 `n8n_workflow_template.json` 内容
4. 保存工作流程

### 3. 配置节点

#### Email 节点配置
- SMTP 服务器: `smtp.163.com`
- 端口: `465`
- 用户: `h13751019800@163.com`
- 密码: 你的邮箱授权码

## Webhook API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/webhook/trigger` | POST | 触发完整工作流 |
| `/webhook/fetch` | POST | 仅抓取新闻 |
| `/webhook/create` | POST | AI二创 |
| `/webhook/generate` | POST | 生成视频 |
| `/webhook/publish` | POST | 发布视频 |
| `/health` | GET | 健康检查 |
| `/status` | GET | 系统状态 |

## 工作流说明

```
┌─────────────────┐
│  定时触发器     │
│  (每日 06:00)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │
│  /webhook/trigger│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   IF 判断       │
│  success?       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│成功通知│ │失败通知│
│ Email │ │ Email │
└───────┘ └───────┘
```

## 手动触发

n8n 提供了手动 Webhook 触发：

```
POST http://localhost:8080/webhook/manual-trigger
```

## 自定义工作流

### 示例：只抓取新闻

```json
{
  "nodes": [
    {
      "parameters": {
        "url": "http://localhost:8080/webhook/fetch",
        "method": "POST"
      },
      "name": "抓取新闻",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### 示例：分语言处理

```javascript
// Function 节点
const items = $input.all();
const chinese = items.filter(i => i.json.language === 'zh');
const english = items.filter(i => i.json.language === 'en');

return [
  { json: { lang: 'zh', items: chinese } },
  { json: { lang: 'en', items: english } }
];
```

## 环境变量

在 n8n 中配置环境变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `WEBHOOK_URL` | Webhook 服务器地址 | `http://localhost:8080` |
| `EMAIL_FROM` | 发件邮箱 | `h13751019800@163.com` |
| `EMAIL_TO` | 收件邮箱 | `h13751019800@163.com` |

## 监控与日志

- Webhook 日志: `logs/n8n_webhook_*.log`
- 执行日志: `logs/main_*.log`
- 数据输出: `data/output/`

## 故障排除

### Webhook 连接失败

1. 检查 Python 服务是否运行：`curl http://localhost:8080/health`
2. 检查防火墙设置
3. 确认端口未被占用

### Email 发送失败

1. 确认邮箱授权码正确
2. 检查 SMTP 设置
3. 163邮箱需要开启 IMAP/SMTP 服务

### n8n 无法访问本地服务

如果 n8n 运行在 Docker 中，使用：
- `http://host.docker.internal:8080` (Windows/Mac)
- `http://172.17.0.1:8080` (Linux)
