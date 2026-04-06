# HeyGen 数字人 API 配置指南

## 1. 申请 HeyGen API Key

### 步骤 1：注册账号
1. 访问：https://app.heygen.com
2. 点击 "Sign Up" 或 "Get Started"
3. 使用 Google 账号或邮箱注册
4. 登录后进入控制台

### 步骤 2：获取 API Key
1. 进入：https://app.heygen.com/settings?nav=API
2. 找到 "API Key" 部分
3. 点击 "Create API Key" 或复制现有 Key
4. API Key 格式：`eyJhbGciOiJIUzI1NiJ9...`

### 步骤 3：创建数字人形象
1. 进入 Avatar 功能
2. 选择一个预设形象 或 上传自定义图片
3. 记录 Avatar ID

**禅心师姐推荐形象**：
- 搜索 "Asian woman serene" 或 "Zen Buddhist woman"
- 或上传 AI 生成的禅意女性图片

**爪爪博士推荐形象**：
- 搜索 "friendly doctor" 或 "Asian man friendly"
- 或上传 AI 生成的形象

---

## 2. 配置到项目

编辑 `config/settings.json`：

```json
{
  "tools": {
    "digital_human": {
      "provider": "heygen",
      "avatar_id_zen": "你的禅心师姐Avatar ID",
      "avatar_id_paw": "你的爪爪博士Avatar ID"
    }
  }
}
```

或创建 `.env` 文件：

```bash
HEYGEN_API_KEY=eyJhbGciOiJIUzI1NiJ9...
ZEN_SISTER_AVATAR_ID=your-avatar-id
PAW_DOCTOR_AVATAR_ID=your-avatar-id
```

---

## 3. 免费额度

| 套餐 | 额度 | 价格 |
|------|------|------|
| Free | 10分钟/月 | 免费 |
| Starter | 100分钟/月 | $29/月 |
| Pro | 500分钟/月 | $99/月 |

**免费额度足够每天制作1-2条视频**

---

## 4. HeyGen 数字人提示词

### 禅心师姐形象提示词（用于 Midjourney/DALL-E）

```
A serene Asian woman in her early 30s with an elegant oval face,
soft features, and gentle almond eyes. Long black hair flowing
past her shoulders with a subtle natural sheen. Wearing a
minimalist cream-colored linen shirt. Expressing a calm,
warm smile. Standing in a zen-inspired room with soft natural
light streaming through paper screens. Tea set on a wooden table.
High-end, ethereal, healing atmosphere. Photorealistic, 8K.
```

### 爪爪博士形象提示词

```
A friendly Asian man in his mid-30s with a round, approachable
face, wearing round golden glasses, short curly brown hair.
Dressed in a casual white lab coat over a cozy sweater.
A cute pet-themed badge on the chest. Expressing an enthusiastic,
warm smile. Professional yet fun aesthetic. Photorealistic, 8K.
```

---

## 5. 测试 HeyGen API

配置完成后，运行：

```bash
cd ai-video-agent
python -c "
from src.video.digital_human import DigitalHumanCreator
creator = DigitalHumanCreator()
creator.generate_avatar_image('禅心师姐')
"
```

---

## 6. 常见问题

**Q：HeyGen 免费吗？**
A：每月有10分钟免费额度，足够初期使用

**Q：需要信用卡吗？**
A：注册时不需要，升级付费套餐时需要

**Q：支持中文吗？**
A：支持，但中文配音推荐使用 ElevenLabs

---

## 7. 替代方案

如果 HeyGen 申请困难，可以使用：

1. **D-ID** (https://www.d-id.com) - 有免费额度
2. **腾讯智影** (https://zenvideo.qq.com) - 中文界面
3. **SadTalker** - 开源免费，需要本地部署

---

*配置完成后，AI 将自动生成数字人视频！*
