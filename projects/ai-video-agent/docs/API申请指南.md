# 🔑 AI 短视频运营 - API 密钥申请指南

> 更新日期：2026-04-05
> 包含：HeyGen、D-ID、ElevenLabs、TikTok API 申请教程

---

## 一、数字人视频 API

### 1.1 HeyGen（推荐）

**官网**：https://heygen.com

**免费额度**：每月 10 分钟视频生成

**申请步骤**：
```
1. 访问 https://app.heygen.com/  注册账号
2. 使用 Google 账号登录或邮箱注册
3. 进入 Dashboard，点击 "API" 或 "Developer"
4. 复制 API Key

API Key 格式：eyJhbGciOiJIUzI1NiJ9...
```

**申请地址**：https://app.heygen.com/settings?nav=API

**使用配置**：
```bash
HEYGEN_API_KEY=你的API密钥
ZEN_SISTER_AVATAR_ID=你的数字人形象ID
```

---

### 1.2 D-ID（备选）

**官网**：https://www.d-id.com

**免费额度**：每月 50 张图片转视频

**申请步骤**：
```
1. 访问 https://www.d-id.com/
2. 点击 "Get Started"
3. 注册账号（可用 Google）
4. 进入 API 控制台
5. 复制 API Key

API Key 格式：Basic a2V5X...
```

**申请地址**：https://www.d-id.com/clients

---

### 1.3 腾讯智影（国内用户）

**官网**：https://zenvideo.qq.com/

**特点**：中文界面，对国内用户友好

**申请步骤**：
```
1. 访问 https://zenvideo.qq.com/
2. 使用微信/QQ登录
3. 进入控制台
4. 申请数字人 API 使用权限
```

---

## 二、AI 配音 API

### 2.1 ElevenLabs（推荐）

**官网**：https://elevenlabs.io

**免费额度**：每月 10,000 字符，1 个自定义声音

**申请步骤**：
```
1. 访问 https://elevenlabs.io/
2. 点击 "Sign Up" 注册
3. 使用 Google 或邮箱注册
4. 进入 Profile → API Key
5. 复制 API Key

API Key 格式：sk_...
```

**声音克隆**：
```
1. 登录后进入 Voice Library
2. 点击 Add Voice
3. 上传 1-5 分钟的音频样本
4. 设置声音名称和参数
5. 获得 Voice ID
```

**申请地址**：https://elevenlabs.io/api

---

### 2.2 讯飞配音（国内用户）

**官网**：https://peiyin.xunfei.cn

**特点**：中文效果好

**申请步骤**：
```
1. 访问 https://console.xfyun.cn/
2. 注册账号并登录
3. 找到「语音合成」服务
4. 创建应用，获取 AppID 和 APIKey
```

---

## 三、社交媒体 API

### 3.1 TikTok API

**官网**：https://developers.tiktok.com/

**免费额度**：基础功能免费

**申请步骤**：
```
1. 访问 https://developers.tiktok.com/
2. 创建开发者账号
3. 创建应用（选择 Content Posting API）
4. 填写应用信息
5. 等待审核（通常1-3天）
6. 获得 Access Token

所需权限：
- video.upload
- video.publish
- user.info.basic
```

**注意**：TikTok API 需要应用审核，建议先申请企业认证

**申请地址**：https://developers.tiktok.com/

---

### 3.2 YouTube Data API

**官网**：https://console.cloud.google.com/

**免费额度**：每日 10,000 单位（每1000播放=1单位）

**申请步骤**：
```
1. 访问 https://console.cloud.google.com/
2. 创建项目
3. 启用 YouTube Data API v3
4. 创建凭据（API Key）
5. 复制 API Key

限制：
- 每日上传次数有限
- 需要 OAuth 2.0 才能上传视频
```

**申请地址**：https://console.cloud.google.com/apis/library/youtube.googleapis.com

---

## 四、数据分析 API

### 4.1 蝉妈妈（抖音数据）

**官网**：https://www.chanmama.com/

**价格**：¥299/月起

**申请步骤**：
```
1. 访问 https://www.chanmama.com/
2. 注册账号
3. 购买会员
4. 进入开发者中心
5. 申请 API 接口
```

---

## 五、配置 API 密钥

### 5.1 复制配置模板

```bash
# 在项目目录下
copy .env.example .env
```

### 5.2 编辑 .env 文件

```bash
# HeyGen 数字人
HEYGEN_API_KEY=eyJhbGciOiJIUzI1NiJ9...

# ElevenLabs 配音
ELEVENLABS_API_KEY=sk_xxxx...

# TikTok
TIKTOK_ACCESS_TOKEN=...

# YouTube
YOUTUBE_API_KEY=AIza...
```

### 5.3 在代码中使用

```python
import os
from dotenv import load_dotenv

load_dotenv()

heygen_key = os.getenv("HEYGEN_API_KEY")
```

---

## 六、快速开始（无需 API）

### 如果暂时没有 API，可以：

1. **手动制作视频**
   - 使用剪映等工具手动剪辑
   - 按照生成的脚本制作

2. **使用免费工具**
   - SadTalker（本地部署，数字人生成）
   - 讯飞配音（免费额度）
   - Canva（视频制作）

3. **跳过视频制作**
   - 只使用脚本生成和报告功能
   - 手动发布视频

---

## 七、API 申请优先级

| 优先级 | API | 用途 | 推荐度 |
|--------|-----|------|--------|
| ⭐⭐⭐⭐⭐ | ElevenLabs | 配音克隆 | 必须 |
| ⭐⭐⭐⭐ | HeyGen | 数字人视频 | 推荐 |
| ⭐⭐⭐ | 蝉妈妈 | 数据分析 | 可选 |
| ⭐⭐ | TikTok API | 自动发布 | 可选 |
| ⭐ | YouTube API | 自动发布 | 可选 |

---

## 八、常见问题

**Q：申请被拒绝怎么办？**
A：TikTok API 需要企业账号，可以先手动发布

**Q：免费额度够用吗？**
A：对于初期运营足够，每天1-2条视频

**Q：需要信用卡吗？**
A：部分API需要，建议用虚拟卡

---

*API配置完成后，运行 `python main.py` 启动自动化运营！*
