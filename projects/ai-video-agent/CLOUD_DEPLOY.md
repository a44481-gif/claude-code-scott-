# ☁️ 云端自动化部署指南

> GitHub Actions + 飞书 = 24/7 自动运营

---

## 📋 配置清单

### 联系信息
| 项目 | 内容 |
|------|------|
| 📧 邮箱 | scott365888@gmail.com |
| 💬 微信 | PTS9800 |
| 📱 通知邮箱 | h13751019800@163.com |

---

## 🚀 部署步骤

### 第一步：创建 GitHub 仓库

1. 打开 **https://github.com/new**
2. 仓库名称：`ai-video-agent`
3. 选择 **Private**（私有）
4. 点击 **Create repository**

### 第二步：上传代码

```bash
# 在项目目录执行
cd "d:/claude mini max 2.7/projects/ai-video-agent"
git init
git add .
git commit -m "Initial commit: AI 短视频运营系统"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-video-agent.git
git push -u origin main
```

### 第三步：配置 Secrets

1. 打开 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 添加以下 Secret：

| Secret Name | Value |
|-------------|-------|
| `EMAIL_PASSWORD` | `JWxaQXzrCQCWtPu3` |
| `FEISHU_WEBHOOK` | 飞书机器人 Webhook 地址 |

### 第四步：配置飞书机器人

1. 打开飞书群
2. 设置 → 群机器人 → 添加机器人
3. 选择 **自定义机器人**
4. 复制 Webhook 地址
5. 粘贴到 GitHub Secrets → `FEISHU_WEBHOOK`

### 第五步：激活 Actions

1. 打开 GitHub 仓库 → **Actions** 标签
2. 点击左侧 **AI 短视频运营**
3. 点击 **Enable workflow**

---

## ⏰ 自动运行时间

| 触发 | 时间 |
|------|------|
| 定时任务 | 每天 09:00 (北京时间) |
| 手动触发 | 随时可触发 |

---

## 📊 工作流程

```
┌─────────────────────────────────────────────────────┐
│  GitHub Actions 云端执行                            │
├─────────────────────────────────────────────────────┤
│  1. 检出代码                                       │
│  2. 安装依赖（Python）                             │
│  3. 生成每日内容                                   │
│  4. 发送飞书通知 → Scott (微信: PTS9800)          │
│  5. 发送邮件 → scott365888@gmail.com              │
│  6. 保存生成内容到 Artifacts                       │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 手动触发测试

1. 打开 GitHub 仓库 → **Actions**
2. 点击 **AI 短视频运营**
3. 点击 **Run workflow** → **Run workflow**

---

## 📱 通知效果

### 飞书通知
```
🤖 AI 短视频运营 - 2026-04-07
每日内容已自动生成，请查收邮件获取详情

生成时间：2026-04-07 09:00:00
```

### 邮件通知
```
收件人：scott365888@gmail.com
主题：AI 短视频运营报告 - 2026-04-07

内容：每日内容已生成，云端自动化运行成功
```

---

## 📁 文件结构

```
ai-video-agent/
├── .github/
│   └── workflows/
│       └── daily_content.yml   # GitHub Actions 工作流
├── src/
│   └── content/
│       └── daily_content_generator.py  # 内容生成器
├── scripts/
│   └── feishu_notify.py       # 飞书通知
├── config/
│   └── config.json             # 配置文件
└── README.md
```

---

## ❓ 常见问题

### Q: 如何修改运行时间？
编辑 `.github/workflows/daily_content.yml`，修改 cron 表达式：
```yaml
schedule:
  - cron: '0 1 * * *'  # 每天 9:00
```

### Q: 如何添加更多通知渠道？
在 `scripts/` 目录添加新的通知脚本

### Q: 如何查看运行日志？
GitHub 仓库 → Actions → 点击具体运行 → 查看日志

---

## 📞 联系

- 📧 scott365888@gmail.com
- 💬 微信: PTS9800

---

*云端自动化，24/7 不间断运行！*
