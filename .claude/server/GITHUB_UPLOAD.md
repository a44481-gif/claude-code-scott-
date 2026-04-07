# SCOTT Payment System - GitHub 仓库

## 上传到 GitHub

### 1. 创建 GitHub 仓库

1. 打开 https://github.com/new
2. **Repository name**: `scott-payment-system`
3. **Description**: `SCOTT豆包赚钱 - AI代运营收款系统`
4. 选择 **Private**（私有仓库）
5. 点击 **Create repository**

### 2. 本地初始化（已准备好）

仓库代码已准备好，位于：
```
d:/claude mini max 2.7/.claude/server/
```

### 3. 上传命令

在 **GitHub 创建仓库后**，复制仓库地址，然后执行：

```bash
cd "d:/claude mini max 2.7/.claude/server"
git init
git add .
git commit -m "Initial commit: SCOTT豆包赚钱收款系统"
git remote add origin https://github.com/YOUR_USERNAME/scott-payment-system.git
git push -u origin main
```

**注意**: 把 `YOUR_USERNAME` 换成你的 GitHub 用户名

---

## 或者使用 GitHub 网页上传

如果不想用命令行：

1. 打开 https://github.com/new
2. 创建仓库名 `scott-payment-system`
3. 选择 **Private**
4. 点击 **Create repository**
5. 点击 **uploading an existing file**
6. 把 `server` 文件夹里的所有文件拖进去
7. 点击 **Commit changes**

---

## 仓库文件结构

```
scott-payment-system/
├── app.py                 # Flask 主程序
├── config.py              # 配置管理
├── notification.py        # 通知服务
├── alipay_service.py      # 支付宝服务
├── order_service.py       # 订单服务
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量（部署时在 Railway 设置）
├── data/
│   ├── orders.db         # SQLite 数据库
│   └── alipay_qr.png     # 收款码图片
├── Dockerfile             # Docker 配置
├── docker-compose.yml     # Docker Compose
├── setup.bat             # Windows 安装脚本
└── CONFIG_GUIDE.md       # 配置指南
```
