# 🚀 AI 短视频运营系统 - 快速启动指南

> 一键启动，自动运营！

---

## ✅ 已配置完成的功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 免费配音 | ✅ | Edge TTS（无限使用） |
| 邮件发送 | ✅ | 163邮箱已配置 |
| 数字人 | ⏳ | SadTalker（需安装） |
| 视频脚本 | ✅ | 7天禅心师姐+7天爪爪博士 |
| 变现追踪 | ✅ | 收入记录系统 |
| 运营报告 | ✅ | 自动生成+发送邮件 |

---

## 🎯 立即开始

### 步骤1：安装 SadTalker（数字人）

```bash
# 克隆仓库
git clone https://github.com/OpenTalker/SadTalker.git

# 安装依赖
cd SadTalker
pip install -r requirements.txt

# 运行网页界面
python app.py
```

### 步骤2：生成配音

```bash
cd "d:/claude mini max 2.7/projects/ai-video-agent"
python src/tts/edge_tts_voice.py
```

### 步骤3：创建数字人视频

```bash
# 在 SadTalker 目录运行
python inference.py --driven_audio ../output/audio/test.mp3 --source_image avatar.png
```

### 步骤4：发送测试邮件

```bash
python src/analytics/income_tracker.py
```

---

## 📁 项目文件结构

```
ai-video-agent/
├── config/
│   └── email_config.json          # 邮件配置
├── src/
│   ├── tts/
│   │   └── edge_tts_voice.py     # 免费配音工具
│   ├── email/
│   │   └── report_sender.py       # 邮件发送
│   └── analytics/
│       └── income_tracker.py      # 收入追踪
├── scripts/
│   └── video_scripts/
│       ├── zen_sister_week1.md    # 禅心师姐7天脚本
│       └── pet_doctor_week1.md    # 爪爪博士7天脚本
├── docs/
│   ├── SadTalker安装教程.md       # 数字人安装
│   └── 变现指南.md                # 赚钱攻略
└── output/
    ├── audio/                     # 配音文件
    └── video/                     # 视频文件
```

---

## 💰 变现清单

### 现在可以做的

```
□ 绑定支付宝到抖音
□ 申请创作者激励计划
□ 申请商品橱窗
□ 选择带货商品
```

### 本周目标

```
□ 每天发布1条视频
□ 7天后达到100粉丝
□ 30天后达到1000粉丝
□ 开启创作者激励计划
```

---

## 📧 邮件报告

系统会在每周一自动发送运营报告到：
**h13751019800@163.com**

报告内容包括：
- 本周播放量/点赞/粉丝增长
- 爆款视频分析
- 收入统计
- 下周优化建议

---

## 📞 需要帮助？

| 问题 | 解决方案 |
|------|---------|
| SadTalker 安装失败 | 查看 docs/SadTalker安装教程.md |
| 配音没声音 | 检查音频文件格式 |
| 邮件发送失败 | 检查授权码是否正确 |
| 变现问题 | 查看 docs/变现指南.md |

---

## 🎬 下一步行动

1. **今天**：安装 SadTalker，测试数字人视频
2. **明天**：用 Edge TTS 生成第一条配音
3. **本周**：拍摄/制作第一条视频并发布
4. **每天**：坚持发布，持续7天

---

**加油！坚持发布，赚钱是迟早的事！** 💪
