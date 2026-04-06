# AI 短视频运营 Agent - 数字人视频制作模块
# 支持: HeyGen, D-ID, SadTalker

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

class DigitalHumanCreator:
    """数字人视频制作器"""

    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.load_config()
        self.setup_paths()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                tools = config.get("tools", {})
                self.digital_human = tools.get("digital_human", {})
                self.tts = tools.get("tts", {})
                self.heygen_api_key = os.getenv("HEYGEN_API_KEY", "")
                self.d_id_api_key = os.getenv("DID_API_KEY", "")
                self.zen_avatar_id = os.getenv("ZEN_SISTER_AVATAR_ID", self.digital_human.get("avatar_id_zen", ""))
                self.paw_avatar_id = os.getenv("PAW_DOCTOR_AVATAR_ID", self.digital_human.get("avatar_id_paw", ""))
        except Exception as e:
            print(f"⚠️ 配置加载失败: {e}")
            self.heygen_api_key = ""
            self.d_id_api_key = ""

    def setup_paths(self):
        """设置路径"""
        self.outputs_dir = Path("outputs/videos")
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def create_video(self, script):
        """创建数字人视频"""
        ip_name = script.get("ip_name", "禅心师姐")
        content = script.get("content", {})
        script_text = self.extract_script_text(content)

        print(f"\n🎬 开始制作数字人视频...")
        print(f"   IP: {ip_name}")
        print(f"   内容: {script_text[:50]}...")

        # 检查API配置
        if self.heygen_api_key and self.heygen_api_key != "your-heygen-api-key-here":
            print(f"   ✅ HeyGen API 已配置")
            return self.create_heygen_video(script, script_text)
        elif self.d_id_api_key and self.d_id_api_key != "your-d-id-api-key-here":
            print(f"   ✅ D-ID API 已配置")
            return self.create_d_id_video(script, script_text)
        else:
            print(f"   ⏳ API未配置，跳过视频制作")
            print(f"   📝 请在 .env 文件中配置 API 密钥")
            return None

    def extract_script_text(self, content):
        """提取脚本文本"""
        if isinstance(content, dict):
            # 尝试按优先级提取关键文本
            for key in ["main", "opening", "hook", "opener", "intro", "question"]:
                if key in content:
                    return content[key]
            # 如果没有明确的关键字段，连接所有文本
            return " ".join(str(v) for v in content.values() if v)
        return str(content)

    def generate_audio(self, text, voice_id=None):
        """生成配音 - 使用 ElevenLabs"""
        try:
            from elevenlabs import generate, play, set_api_key

            api_key = os.getenv("ELEVENLABS_API_KEY", "")
            if not api_key or api_key == "your-elevenlabs-api-key-here":
                print("   ⚠️ ElevenLabs API 未配置，跳过配音")
                return None

            set_api_key(api_key)

            # 根据IP选择声音
            voice_id = voice_id or os.getenv("ZEN_SISTER_VOICE_ID", "Rachel")

            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )

            # 保存音频文件
            audio_path = self.outputs_dir / f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            with open(audio_path, "wb") as f:
                f.write(audio)

            print(f"   ✅ 配音已生成: {audio_path}")
            return str(audio_path)

        except ImportError:
            print("   ⚠️ 请安装 elevenlabs: pip install elevenlabs")
            return None
        except Exception as e:
            print(f"   ⚠️ 配音生成失败: {e}")
            return None

    def create_heygen_video(self, script, script_text):
        """使用 HeyGen API 创建视频"""
        ip_name = script.get("ip_name", "禅心师姐")
        avatar_id = self.zen_avatar_id if "禅心" in ip_name else self.paw_avatar_id

        if not avatar_id:
            print(f"   ⚠️ {ip_name} Avatar ID 未配置")
            return None

        # 1. 生成配音
        audio_path = self.generate_audio(script_text)
        if not audio_path:
            return None

        # 2. 调用 HeyGen API
        url = "https://api.heygen.com/v1/video/generate"

        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "audio",
                    "audio_url": f"file://{audio_path}"
                },
                "background": {
                    "type": "color",
                    "value": "#FAF8F5"
                }
            }],
            "dimension": {
                "width": 1080,
                "height": 1920
            }
        }

        headers = {
            "Authorization": f"Bearer {self.heygen_api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            result = response.json()

            if "data" in result and "video_id" in result["data"]:
                video_id = result["data"]["video_id"]
                print(f"   ✅ HeyGen 视频任务已创建: {video_id}")

                # 等待视频生成
                video_url = self.wait_for_heygen_video(video_id)

                if video_url:
                    # 下载视频
                    video_path = self.download_video(video_url, script["id"])
                    return video_path

            print(f"   ⚠️ HeyGen 响应: {result}")
            return None

        except Exception as e:
            print(f"   ❌ HeyGen API 调用失败: {e}")
            return None

    def wait_for_heygen_video(self, video_id, max_wait=300):
        """等待 HeyGen 视频生成"""
        url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        headers = {"Authorization": f"Bearer {self.heygen_api_key}"}

        print(f"   ⏳ 等待视频生成...")
        for i in range(max_wait // 10):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                result = response.json()

                status = result.get("data", {}).get("status", "")
                print(f"   状态: {status} ({i*10}s)")

                if status == "completed":
                    return result.get("data", {}).get("video_url")
                elif status == "failed":
                    print(f"   ❌ 视频生成失败")
                    return None

                time.sleep(10)

            except Exception as e:
                print(f"   ⚠️ 状态检查失败: {e}")
                time.sleep(10)

        print(f"   ⏳ 等待超时")
        return None

    def create_d_id_video(self, script, script_text):
        """使用 D-ID API 创建视频"""
        # D-ID 实现类似...
        print("   ⏳ D-ID 视频功能开发中")
        return None

    def download_video(self, video_url, script_id):
        """下载视频"""
        try:
            response = requests.get(video_url, timeout=120, stream=True)
            response.raise_for_status()

            video_path = self.outputs_dir / f"video_{script_id}.mp4"

            with open(video_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"   ✅ 视频已保存: {video_path}")
            return str(video_path)

        except Exception as e:
            print(f"   ❌ 视频下载失败: {e}")
            return None

    def generate_avatar_image(self, ip_name, prompt=None):
        """使用 AI 生成数字人形象图"""
        print(f"   ⏳ 正在生成 {ip_name} 形象图...")

        # 预定义提示词
        prompts = {
            "禅心师姐": """
A serene Asian woman in her early 30s with an elegant oval face,
soft features, and gentle almond eyes. Long black hair flowing
past her shoulders. Wearing a minimalist cream-colored linen shirt.
Expressing a calm, warm smile. Standing in a zen-inspired room
with soft natural light. High-end, ethereal, healing atmosphere.
Photorealistic, 4K.
""",
            "爪爪博士": """
A friendly Asian man in his mid-30s with a round, approachable
face, wearing round golden glasses, short curly brown hair.
Dressed in a casual white lab coat over a cozy sweater.
A cute pet-themed badge on the chest. Expressing an enthusiastic,
warm smile. Professional yet fun aesthetic.
Photorealistic, 4K.
"""
        }

        # 这里可以集成 Midjourney / DALL-E API
        print(f"   ⏳ 请使用 Midjourney 或 DALL-E 生成形象图")
        print(f"   📝 参考提示词:")
        print(f"   {prompts.get(ip_name, prompts['禅心师姐'])}")

        return None


if __name__ == "__main__":
    # 测试数字人制作
    creator = DigitalHumanCreator()

    test_script = {
        "id": "TEST-001",
        "ip_name": "禅心师姐",
        "type": "早安禅语",
        "content": {
            "opening": "早安。此刻，你的心在哪里？",
            "main": "昨天再好，也走不回去。明天再难，也要抬脚继续。",
            "closing": "愿你今天，心安，自在。"
        }
    }

    print("=" * 50)
    print("🎬 数字人视频制作器 - 测试")
    print("=" * 50)

    # 测试视频生成（需要API配置）
    # video_path = creator.create_video(test_script)
    # print(f"视频路径: {video_path}")

    # 测试形象图生成
    creator.generate_avatar_image("禅心师姐")
