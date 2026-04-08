# ============================================
#   SCOTT 豆包赚钱 - 自动部署设置
# ============================================

## 自动部署架构

```
GitHub Push
    ↓
GitHub Actions (自动构建)
    ↓
Railway (自动部署)
    ↓
云端收款系统上线 (24小时运行)
```

---

## 部署方式

### 方式1：Railway GitHub 集成（推荐）

Railway 可以直接连接 GitHub，每次你推送代码就会自动部署：

1. 打开 https://railway.app
2. 点击项目 → **Settings** → **GitHub**
3. 连接 `scott-payment-system` 仓库
4. 开启 **Auto Deploy**

---

### 方式2：Railway CLI

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 进入项目
cd scott-payment-system

# 链接项目
railway init
railway link

# 部署
railway up
```

---

### 方式3：本地推送 → 自动部署

每次你想更新云端时：

```bash
git add .
git commit -m "更新内容"
git push origin main
```

**Railway 会自动检测到 GitHub 的更新，自动部署新版本！**

---

## 环境变量设置

在 Railway 后台设置以下变量：

| 变量名 | 值 |
|--------|-----|
| `ALIPAY_MODE` | `personal` |
| `PERSONAL_ALIPAY_ACCOUNT` | `13751019800` |
| `SENDER_EMAIL` | `scott365888@gmail.com` |
| `SENDER_PASSWORD` | `邮箱授权码` |
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `FEISHU_WEBHOOK_URL` | `飞书Webhook` |

---

## 测试自动部署

1. 修改本地代码
2. 执行：
   ```bash
   git add . && git commit -m "测试自动部署" && git push
   ```
3. 打开 Railway 查看部署状态
4. 等待 2-3 分钟，自动上线！

---

## 监控

- Railway 仪表盘：https://railway.app/dashboard
- 部署日志实时查看
- 自动回滚功能
