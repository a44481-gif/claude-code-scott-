# SCOTT豆包赚钱 - 云端部署配置

# ==========================================
# Railway 部署 (推荐 - 免费500小时/月)
# ==========================================
# 1. 注册 https://railway.app
# 2. 连接 GitHub 仓库
# 3. 添加 Environment Variables
# 4. Deploy

# ==========================================
# Render 部署 (免费750小时/月)
# ==========================================
# 1. 注册 https://render.com
# 2. 创建 Web Service
# 3. 连接 GitHub
# 4. 设置 Build Command: pip install -r requirements.txt
# 5. 设置 Start Command: gunicorn app:app

# ==========================================
# 阿里云函数计算 (按量付费)
# ==========================================
# 1. 注册阿里云账号
# 2. 创建函数计算服务
# 3. 上传代码包
# 4. 配置触发器

# ==========================================
# 环境变量配置
# ==========================================

# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-in-production

# 支付宝 (商户模式需要)
ALIPAY_MODE=merchant
ALIPAY_APP_ID=your-app-id
ALIPAY_PRIVATE_KEY=your-private-key
ALIPAY_PUBLIC_KEY=alipay-public-key
ALIPAY_NOTIFY_URL=https://your-domain.com/api/alipay-notify

# 数据库 (云端使用 PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# 邮件
SMTP_SERVER=smtp.163.com
SMTP_PORT=465
SENDER_EMAIL=your-email@163.com
SENDER_PASSWORD=your-authorization-code

# 飞书
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# n8n
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/payment

# Server酱 (微信推送)
SERVERCHAN_SENDKEY=SCTxxx

# 云端域名
DOMAIN=https://your-payment-domain.com
