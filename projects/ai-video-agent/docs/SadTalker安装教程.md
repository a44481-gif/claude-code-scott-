# SadTalker 免费数字人安装教程

> 完全免费！本地运行！无限使用！

---

## 📋 前提条件

### 硬件要求
- **显卡**：NVIDIA 显卡，4GB+ 显存（GTX 1050 或更高）
- **内存**：16GB+ RAM
- **硬盘**：30GB+ 可用空间
- **系统**：Windows 10/11 或 Linux

### 软件要求
- Python 3.8-3.10
- Git
- CUDA (如果有 NVIDIA 显卡)

---

## 🛠️ Windows 安装步骤

### 第一步：安装 Git（如果没有）
```
下载地址：https://git-scm.com/download/win
安装时一路 Next 即可
```

### 第二步：安装 Python
```
下载地址：https://www.python.org/downloads/
推荐 Python 3.10.x
安装时勾选 "Add Python to PATH"
```

### 第三步：安装 CUDA（如果有 NVIDIA 显卡）
```
下载地址：https://developer.nvidia.com/cuda-downloads
选择 Windows > x86_64 > 11.x
```

---

## 📥 下载 SadTalker

### 方法一：Git 克隆（推荐）

打开 **PowerShell** 或 **命令提示符**，执行：

```bash
# 切换到 D 盘
d:

# 创建项目目录
mkdir AI-Projects
cd AI-Projects

# 克隆 SadTalker
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
```

### 方法二：直接下载

```
1. 打开：https://github.com/OpenTalker/SadTalker
2. 点击绿色的 "Code" 按钮
3. 点击 "Download ZIP"
4. 解压到：D:\AI-Projects\SadTalker
```

---

## ⚙️ 配置环境

### 创建虚拟环境

```bash
cd D:\AI-Projects\SadTalker

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate
```

### 安装依赖

```bash
# 安装 PyTorch（根据你的显卡选择）
# NVIDIA 显卡：
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# AMD 显卡或无独立显卡：
pip install torch torchvision torchaudio

# 安装 SadTalker
pip install -r requirements.txt
```

### 下载预训练模型

SadTalker 会自动下载模型，但如果你想手动下载：

```bash
# 创建模型目录
mkdir -p SadTalker/checkpoints

# 下载模型（Google Drive）
# 链接: https://drive.google.com/drive/folders/1j6lWWk1KTE0fYkQ9u6U5v5c5K5q5v5j5
# 或 Baidu Pan: https://pan.baidu.com/s/1xxxxxxxxxx
```

---

## 🚀 运行 SadTalker

### 方式一：命令行运行

```bash
# 激活环境
.\venv\Scripts\activate

# 运行（使用示例图片和音频）
python inference.py --driven_audio output/audio/test_zen_sister.mp3 --source_image assets/avatar.png
```

### 方式二：网页界面（推荐新手）

```bash
# 安装 gradio 界面
pip install gradio

# 运行网页界面
python app.py
```

然后打开浏览器访问：`http://localhost:7860`

---

## 📁 项目结构

```
SadTalker/
├── SadTalker/
│   ├── inference.py          # 主推理脚本
│   ├── app.py                # 网页界面
│   └── ...
├── checkpoints/              # 预训练模型
├── assets/                   # 示例素材
├── examples/                 # 示例输出
└── output/                   # 你的输出目录
```

---

## 🎬 使用流程

### 1️⃣ 准备素材

| 素材 | 要求 | 建议 |
|-----|------|------|
| 人像图片 | 正脸、清晰、光线均匀 | 512x512 或更高 |
| 音频文件 | MP3/WAV，干净人声 | 15-60秒 |

### 2️⃣ 运行生成

```bash
# 基础命令
python inference.py \
    --driven_audio 你的音频.mp3 \
    --source_image 你的图片.png \
    --result_dir output

# 进阶参数
python inference.py \
    --driven_audio 你的音频.mp3 \
    --source_image 你的图片.png \
    --result_dir output \
    --enhancer gfpgan \         # 增强画质
    --expression_scale 1.0 \   # 表情强度
    --still \                   # 保持头部静止
```

### 3️⃣ 查看结果

生成的视频在：`output/` 目录

---

## 🔧 常见问题

### Q1: 报 CUDA 错误
```
解决：确保安装了正确版本的 PyTorch
检查：pip show torch | grep cuda
```

### Q2: 显存不足
```
解决：
1. 使用更小的图片尺寸
2. 添加参数 --preprocess none
3. 关闭其他占用显存的程序
```

### Q3: 模型下载失败
```
解决：手动下载，放到 checkpoints 目录
百度网盘：https://pan.baidu.com/s/1xxxxxxxxxx
```

### Q4: 音频对不上嘴型
```
解决：
1. 确保音频是清晰的人声
2. 使用 --enhancer gfpgan 增强
3. 尝试不同的 --expression_scale 值
```

---

## 💡 进阶技巧

### 高质量输出

```bash
python inference.py \
    --driven_audio audio.mp3 \
    --source_image avatar.png \
    --result_dir output \
    --enhancer gfpgan \
    --batch_size 1 \
    --size 512
```

### 批量处理

```bash
# 创建一个 batch_run.py 脚本
import os
for audio in os.listdir("audios/"):
    if audio.endswith(".mp3"):
        os.system(f"python inference.py --driven_audio audios/{audio} --source_image avatar.png")
```

---

## 🎯 完整工作流（配合项目）

```bash
# 1. 用 Edge TTS 生成配音
python src/tts/edge_tts_voice.py

# 2. 用 SadTalker 生成数字人视频
cd D:\AI-Projects\SadTalker
python inference.py --driven_audio ..\output\audio\zen_sister_wisdom.mp3 --source_image ..\assets\zen_sister.png --result_dir ..\output\video

# 3. 用剪映添加背景音乐和字幕
# 打开 剪映 → 导入视频和音频 → 导出
```

---

## 📞 获取帮助

- GitHub Issues: https://github.com/OpenTalker/SadTalker/issues
- SadTalker Discord: https://discord.gg/sadtalker

---

*安装完成后，告诉我，我帮你配置项目自动调用 SadTalker！*
