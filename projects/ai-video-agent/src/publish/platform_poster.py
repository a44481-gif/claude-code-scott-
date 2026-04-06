# AI 短视频运营 Agent - 多平台发布模块
# 支持: 抖音, TikTok, YouTube Shorts, Instagram

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

class PlatformPoster:
    """多平台视频发布器"""

    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.load_config()
        self.setup_paths()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                self.platforms_config = self.config.get("platforms", {})

                # 加载 API tokens
                self.tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN", "")
                self.youtube_key = os.getenv("YOUTUBE_API_KEY", "")

        except Exception as e:
            print(f"⚠️ 配置加载失败: {e}")
            self.config = {}
            self.platforms_config = {}

    def setup_paths(self):
        """设置路径"""
        self.logs_dir = Path("outputs/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def publish_video(self, video_path, script):
        """发布视频到多平台"""
        if not video_path:
            print("⚠️ 无视频文件，跳过发布")
            return {}

        posting_config = script.get("posting_config", {})
        platforms = posting_config.get("platforms", ["douyin"])

        results = {}
        for platform in platforms:
            if not self.platforms_config.get(platform, {}).get("enabled", False):
                continue

            try:
                if platform == "douyin":
                    results["douyin"] = self.publish_douyin(video_path, script)
                elif platform == "tiktok":
                    results["tiktok"] = self.publish_tiktok(video_path, script)
                elif platform == "youtube":
                    results["youtube"] = self.publish_youtube(video_path, script)
                elif platform == "instagram":
                    results["instagram"] = self.publish_instagram(video_path, script)

            except Exception as e:
                print(f"   ❌ {platform} 发布失败: {e}")
                results[platform] = {"status": "error", "message": str(e)}

        return results

    def publish_douyin(self, video_path, script):
        """发布到抖音"""
        print(f"\n📤 发布到抖音...")

        # 抖音 API 需要企业认证，这里提供手动发布指南
        print(f"   ⏳ 抖音 API 需要企业认证")
        print(f"   📝 请手动上传视频到抖音创作服务平台")
        print(f"   🔗 https://creator.douyin.com/")

        # 生成发布信息
        publish_info = {
            "platform": "douyin",
            "video_path": video_path,
            "title": script.get("title", ""),
            "description": " ".join(script.get("hashtags", [])),
            "status": "manual_required",
            "url": "https://creator.douyin.com/",
            "scheduled_time": script.get("posting_config", {}).get("time", "12:00")
        }

        self.log_publish(publish_info)
        return publish_info

    def publish_tiktok(self, video_path, script):
        """发布到 TikTok"""
        print(f"\n📤 发布到 TikTok...")

        if not self.tiktok_token or self.tiktok_token == "your-tiktok-access-token":
            print(f"   ⏳ TikTok API Token 未配置")
            print(f"   📝 请配置 TIKTOK_ACCESS_TOKEN")
            return {"status": "not_configured"}

        try:
            # TikTok API 调用
            url = "https://open.tiktokapis.com/v2/post/publish/video/init/"

            with open(video_path, "rb") as f:
                video_data = f.read()

            headers = {
                "Authorization": f"Bearer {self.tiktok_token}",
                "Content-Type": "application/octet-stream"
            }

            payload = {
                "title": script.get("title", ""),
                "description": " ".join(script.get("hashtags", [])),
                "post_mode": "IMMEDIATELY"
            }

            response = requests.post(
                url,
                headers=headers,
                data=video_data,
                params=payload,
                timeout=60
            )

            result = response.json()
            print(f"   ✅ TikTok 发布响应: {result}")

            return {
                "platform": "tiktok",
                "status": "success" if response.ok else "failed",
                "response": result
            }

        except Exception as e:
            print(f"   ❌ TikTok 发布失败: {e}")
            return {"status": "error", "message": str(e)}

    def publish_youtube(self, video_path, script):
        """发布到 YouTube Shorts"""
        print(f"\n📤 发布到 YouTube Shorts...")

        # YouTube API 需要 OAuth，这里提供指南
        print(f"   ⏳ YouTube API 需要 OAuth 认证")
        print(f"   📝 请使用 YouTube Studio 手动上传")
        print(f"   🔗 https://studio.youtube.com/")

        return {
            "platform": "youtube",
            "status": "manual_required",
            "url": "https://studio.youtube.com/"
        }

    def publish_instagram(self, video_path, script):
        """发布到 Instagram Reels"""
        print(f"\n📤 发布到 Instagram...")

        # Instagram API 限制较多
        print(f"   ⏳ Instagram API 需要 Meta Business 认证")
        print(f"   📝 请使用 Meta Business Suite 手动上传")
        print(f"   🔗 https://business.facebook.com/")

        return {
            "platform": "instagram",
            "status": "manual_required",
            "url": "https://business.facebook.com/"
        }

    def log_publish(self, info):
        """记录发布信息"""
        log_file = self.logs_dir / f"publish_log_{datetime.now().strftime('%Y%m')}.json"

        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append({
            "timestamp": datetime.now().isoformat(),
            **info
        })

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def get_scheduled_posts(self):
        """获取已排期的发布计划"""
        # 从配置文件读取发布计划
        return self.config.get("content", {}).get("posting_schedule", {})


class Scheduler:
    """定时发布调度器"""

    def __init__(self):
        self.tasks = []

    def add_task(self, platform, video_path, script, scheduled_time):
        """添加定时任务"""
        self.tasks.append({
            "platform": platform,
            "video_path": video_path,
            "script": script,
            "scheduled_time": scheduled_time,
            "status": "pending"
        })

    def run_pending(self):
        """执行待发布的任务"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        for task in self.tasks:
            if task["status"] == "pending" and task["scheduled_time"] == current_time:
                poster = PlatformPoster()
                result = poster.publish_video(task["video_path"], task["script"])
                task["status"] = "completed" if result else "failed"
                task["result"] = result
                print(f"✅ 已发布: {task['platform']} - {task['scheduled_time']}")

    def get_status(self):
        """获取任务状态"""
        return {
            "total": len(self.tasks),
            "pending": len([t for t in self.tasks if t["status"] == "pending"]),
            "completed": len([t for t in self.tasks if t["status"] == "completed"]),
            "failed": len([t for t in self.tasks if t["status"] == "failed"])
        }


if __name__ == "__main__":
    # 测试发布功能
    poster = PlatformPoster()

    print("=" * 50)
    print("📤 多平台发布器 - 测试")
    print("=" * 50)

    # 查看配置的平台
    print("\n📋 已配置的平台:")
    for platform, config in poster.platforms_config.items():
        status = "✅ 已启用" if config.get("enabled") else "❌ 已禁用"
        print(f"   {platform}: {status}")
        print(f"      最佳时间: {config.get('best_times', [])}")
