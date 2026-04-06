#!/usr/bin/env python3
"""
免费配音工具 - Edge TTS
完全免费，无限使用！
"""

import asyncio
import edge_tts
import os
from pathlib import Path

# 配置
OUTPUT_DIR = Path("output/audio")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 推荐的声音（中文温柔女声）
VOICES = {
    # 禅心师姐 - 温柔治愈风格
    "zh_sister_calm": "zh-CN-XiaoxiaoNeural",      # 晓晓 - 标准温柔女声
    "zh_sister_warm": "zh-CN-XiaoyiNeural",        # 晓伊 - 年轻温柔

    # 爪爪博士 - 专业温暖风格
    "zh_doctor": "zh-CN-XiaoxiaoNeural",           # 晓晓 - 专业可信

    # 英文（出海用）
    "en_calm": "en-US-AriaNeural",
    "en_gentle": "en-GB-SoniaNeural",
}

async def generate_voice(text, voice_name, output_file, speed="slow"):
    """
    生成配音文件

    Args:
        text: 要配音的文本
        voice_name: 声音名称（如 zh-CN-XiaoxiaoNeural）
        output_file: 输出文件名
        speed: 语速 (-50% 到 +100%)
    """
    communicate = edge_tts.Communicate(text, voice_name, rate=speed)
    await communicate.save(str(OUTPUT_DIR / output_file))
    print(f"✅ 生成成功: {output_file}")

async def generate_with_ssml(text, voice_name, output_file):
    """
    使用 SSML 生成带停顿和语调的配音

    Args:
        text: 带有 SSML 标记的文本
        voice_name: 声音名称
        output_file: 输出文件名
    """
    communicate = edge_tts.Communicate(text, voice_name)
    communicate.endpoint = "https://eastasia.tts.speech.microsoft.com/"
    await communicate.save(str(OUTPUT_DIR / output_file))
    print(f"✅ SSML生成成功: {output_file}")

def generate_voice_sync(text, voice_name, output_file, speed="slow"):
    """同步版本"""
    asyncio.run(generate_voice(text, voice_name, output_file, speed))

# ==================== 预设配音函数 ====================

async def zen_sister_intro():
    """禅心师姐 - 开场白"""
    text = """心静了，一切就对了。

    大家好，我是禅心师姐。

    每天清晨，用一段禅语，开启美好的一天。

    愿你的心，此刻开始平静。"""
    await generate_voice(text, VOICES["zh_sister_calm"], "zen_sister_intro.mp3", speed="-10%")

async def zen_sister_wisdom():
    """禅心师姐 - 禅语智慧"""
    text = """修行，不是在庙里。

    而是在每一个当下。

    当你能够觉察自己的念头，

    当你能够接纳一切发生，

    当你学会与自己和解，

    这，就是最好的修行。"""
    await generate_voice(text, VOICES["zh_sister_warm"], "zen_sister_wisdom.mp3", speed="-15%")

async def pet_doctor_tip():
    """爪爪博士 - 宠物知识"""
    text = """铲屎官们注意了！

    你的猫咪如果出现这三种表现，
    说明它非常信任你。

    第一，猫咪会在你身边睡觉。

    第二，猫咪会用头蹭你。

    第三，猫咪会对你露肚子。

    恭喜你，成为被猫咪选中的人！"""
    await generate_voice(text, VOICES["zh_doctor"], "pet_doctor_tip.mp3", speed="+5%")

# ==================== 示例脚本 ====================

async def main():
    print("=" * 50)
    print("🎙️  免费AI配音生成器 - Edge TTS")
    print("=" * 50)
    print()

    # 生成示例配音
    print("📝 生成示例配音...")

    await zen_sister_intro()
    await zen_sister_wisdom()
    await pet_doctor_tip()

    print()
    print("=" * 50)
    print("✅ 所有配音生成完成！")
    print(f"📁 文件位置: {OUTPUT_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
