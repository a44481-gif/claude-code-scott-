# ElevenLabs 配音 API 配置指南

## 1. 申请 ElevenLabs API

### 步骤 1：注册账号
1. 访问：https://elevenlabs.io
2. 点击 "Sign Up Free"
3. 使用 Google 或邮箱注册
4. 验证邮箱

### 步骤 2：获取 API Key
1. 登录后进入：https://elevenlabs.io/app/settings/api-key
2. 找到 "API Key" 部分
3. 复制 API Key
4. 格式：`sk_xxxxxxxxxxxxxxxxxxxxxxxx`

### 步骤 3：（可选）克隆声音
1. 进入：https://elevenlabs.io/voice-library
2. 点击 "Add Voice"
3. 上传 1-5 分钟的音频样本
4. 等待声音生成（10-30分钟）
5. 获得 Voice ID

---

## 2. 配置到项目

### 方式一：编辑 .env 文件

```bash
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxx
ZEN_SISTER_VOICE_ID=your-zen-voice-id
PAW_DOCTOR_VOICE_ID=your-paw-voice-id
```

### 方式二：安装并配置

```bash
pip install elevenlabs
```

---

## 3. 推荐声音

### 禅心师姐（温柔女声）

**预设声音推荐**：
| Voice ID | 名称 | 特点 |
|----------|------|------|
| Rachel | Rachel | 温暖低沉女声 |
| Bella | Bella | 温柔亲切女声 |
| Antoni | Antoni | 温暖男声 |

**中文推荐参数**：
```python
voice_id = "eleven_multilingual_v2"
# 或使用中文优化模型
```

### 爪爪博士（活力男声）

**预设声音推荐**：
| Voice ID | 名称 | 特点 |
|----------|------|------|
| Antoni | Antoni | 温暖活力男声 |
| Arnold | Arnold | 专业权威男声 |
| Josh | Josh | 友好亲切男声 |

---

## 4. 免费额度

| 套餐 | 字符数 | 自定义声音 | 价格 |
|------|--------|-----------|------|
| Free | 10,000/月 | 1个 | 免费 |
| Starter | 30,000/月 | 3个 | $5/月 |
| Pro | 100,000/月 | 10个 | $22/月 |

**免费额度足够每天生成 5-10 条配音**

---

## 5. 使用示例

```python
from elevenlabs import generate, play, set_api_key

# 设置 API Key
set_api_key("your-api-key")

# 生成配音
audio = generate(
    text="早安。此刻，你的心在哪里？",
    voice="Rachel",
    model="eleven_multilingual_v2"
)

# 播放
play(audio)

# 保存
with open("audio.mp3", "wb") as f:
    f.write(audio)
```

---

## 6. 中文优化

ElevenLabs 支持中文，使用 `eleven_multilingual_v2` 模型：

```python
audio = generate(
    text="早安禅语内容...",
    voice="Rachel",
    model="eleven_multilingual_v2",  # 中文优化模型
    language="zh"  # 指定中文
)
```

---

## 7. 测试 ElevenLabs

```bash
cd ai-video-agent
pip install elevenlabs

python -c "
import os
os.environ['ELEVENLABS_API_KEY'] = 'your-api-key'

from elevenlabs import generate, play, set_api_key
set_api_key('your-api-key')

# 测试中文配音
audio = generate(
    text='早安。此刻，你的心在哪里？',
    voice='Rachel',
    model='eleven_multilingual_v2'
)

with open('test_audio.mp3', 'wb') as f:
    f.write(audio)

print('Audio saved to test_audio.mp3')
"
```

---

## 8. 声音克隆教程

### 准备音频样本
- 时长：3-5 分钟
- 内容：清晰朗读的段落
- 环境：安静，无背景音乐
- 格式：MP3 或 WAV
- 语言：中文普通话

### 上传样本
1. 进入 Voice Library
2. 点击 "Add Voice"
3. 选择 "Professional Voice Clone"
4. 上传音频文件
5. 填写声音名称和描述
6. 等待处理（10-30分钟）

### 使用克隆声音
```python
voice_id = "your-cloned-voice-id"
audio = generate(text="配音文本", voice=voice_id)
```

---

## 9. 替代方案

### 国内用户推荐
1. **讯飞配音** - https://peiyin.xunfei.cn
   - 中文效果好
   - 有免费额度

2. **百度语音合成** - https://ai.baidu.com/tech/speech/tts
   - 免费额度大
   - 中文自然

3. **阿里云语音合成** - https://ai.aliyun.com/mas
   - 效果好
   - 按量付费

---

## 10. 常见问题

**Q：中文效果好吗？**
A：使用 `eleven_multilingual_v2` 模型，中文效果很好

**Q：可以克隆自己的声音吗？**
A：可以，上传5分钟音频即可

**Q：免费额度够用吗？**
A：每天5-10条视频足够

**Q：需要信用卡吗？**
A：免费版不需要

---

*配置完成后，AI 将自动生成自然流畅的配音！*
