# 豆包运营代理人 - 支付宝收款配置指南

## 快速开始

### 1. 安装依赖

双击运行 `setup.bat`，或手动安装：

```bash
cd server
pip install flask flask-cors qrcode Pillow python-dotenv
```

### 2. 配置环境变量

复制配置文件：
```bash
copy .env.example .env
```

然后编辑 `.env` 文件。

---

## 支付宝收款配置

### 方案一：个人快速收款（无需申请商户）

适合：刚开始运营、收款量不大的用户

**步骤：**

1. **获取支付宝收款码**
   - 打开支付宝 → 我的 → 收款码
   - 或支付宝首页搜索"收钱码"

2. **将收款码放入项目**
   - 将收款码图片重命名为 `alipay_qr.png`
   - 放入 `server/data/` 目录

3. **编辑 .env 配置**
   ```env
   ALIPAY_MODE=personal
   PERSONAL_ALIPAY_ACCOUNT=你的支付宝账号（手机号或邮箱）
   ```

4. **启动服务**
   ```bash
   python app.py
   ```

5. **测试收款**
   - 访问 http://localhost:5000
   - 选择金额，填写信息
   - 生成收款二维码
   - 用支付宝扫码测试

**注意：** 个人模式无法自动回调，支付后需要在管理后台手动确认收款。

---

### 方案二：商户API收款（支持自动回调）

适合：有一定业务量、需要自动化运营的用户

**步骤：**

1. **申请支付宝当面付**
   - 访问 https://b.alipay.com
   - 选择产品 → 当面付
   - 提交企业/个体户资质

2. **创建支付宝应用**
   - 访问 https://open.alipay.com
   - 开发者中心 → 创建应用
   - 添加"当面付"能力

3. **获取密钥**
   - 下载支付宝密钥生成工具
   - 生成 RSA2 公钥/私钥
   - 在支付宝后台配置公钥

4. **配置 .env 文件**
   ```env
   # 收款模式
   ALIPAY_MODE=merchant

   # 应用ID（从支付宝开放平台获取）
   ALIPAY_APP_ID=2021001234567890

   # 应用私钥（RSA2）
   ALIPAY_PRIVATE_KEY=
   -----BEGIN RSA PRIVATE KEY-----
   [你的私钥内容]
   -----END RSA PRIVATE KEY-----

   # 支付宝公钥
   ALIPAY_PUBLIC_KEY=
   -----BEGIN PUBLIC KEY-----
   [支付宝公钥内容]
   -----END PUBLIC KEY-----

   # 回调地址（必须是公网可访问）
   ALIPAY_NOTIFY_URL=https://your-domain.com/api/alipay-notify
   ALIPAY_RETURN_URL=https://your-domain.com/success
   ```

5. **配置公网回调（重要！）**
   - 使用 ngrok 将本地服务暴露到公网：
     ```bash
     ngrok http 5000
     ```
   - 将 ngrok 提供的 https 地址填入 `ALIPAY_NOTIFY_URL`
   - 示例：`https://abc123.ngrok.io/api/alipay-notify`

6. **启动服务**
   ```bash
   python app.py
   ```

---

## 邮件通知配置

用于向客户发送订单确认、服务合同等。

### QQ邮箱配置

1. **开启SMTP服务**
   - 登录 mail.qq.com
   - 设置 → 账户 → POP3/SMTP服务 → 开启

2. **获取授权码**
   - 点击"生成授权码"
   - 短信验证后获取

3. **配置 .env**
   ```env
   SMTP_SERVER=smtp.qq.com
   SMTP_PORT=465
   SENDER_EMAIL=your-email@qq.com
   SENDER_PASSWORD=your-authorization-code
   SMTP_SSL=true
   ```

### 其他邮箱

| 邮箱 | SMTP服务器 | 端口 |
|------|-----------|------|
| QQ邮箱 | smtp.qq.com | 465/587 |
| 163邮箱 | smtp.163.com | 465 |
| Gmail | smtp.gmail.com | 587 |

---

## 部署到服务器

### 使用宝塔面板

1. 安装宝塔面板
2. 添加Python项目
3. 设置反向代理到 5000 端口
4. 配置SSL证书

### 使用Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

---

## 常见问题

### Q: 支付成功后订单状态没更新？

**检查项：**
1. 商户模式是否配置了正确的回调地址？
2. 回调地址是否公网可访问？
3. 签名验证是否通过？

**个人模式：** 需要在管理后台手动确认收款

### Q: 邮件发送失败？

**检查项：**
1. SMTP配置是否正确？
2. 邮箱是否开启SMTP服务？
3. 密码是否使用授权码而非登录密码？

### Q: 二维码无法生成？

**检查项：**
1. 是否安装了 qrcode 和 Pillow 库？
2. 个人模式是否将收款码放入正确目录？

---

## 联系与支持

如有问题，请检查：
1. 终端错误日志
2. 浏览器开发者工具 Network 面板
3. 服务器日志文件
