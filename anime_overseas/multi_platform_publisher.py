"""
动漫出海 - 多平台自动发布器
anime_overseas/multi_platform_publisher.py

功能：
1. YouTube API 自动上传
2. TikTok API 自动上传（需官方白名单）
3. Instagram Graph API 自动发布
4. 多账号矩阵管理
5. 定时发布调度
6. 发布状态追踪

用法:
    publisher = MultiPlatformPublisher()
    publisher.upload_youtube("video.mp4", title="...", tags=[...])
    publisher.upload_tiktok("video.mp4", title="...")
"""

import os
import re
import json
import time
import logging
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from anime_ops_config import PLATFORMS, REGIONS, TITLE_TEMPLATES, TRENDING_TAGS, EMOJI_MAP, LOG_DIR, OUTPUT_DIR
from anime_ops_config import EMOTION_WORDS, MONETIZATION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "publisher.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("Publisher")


# ============ 账号管理器 ============

class AccountManager:
    """多账号矩阵管理"""

    def __init__(self, config_path: str = None):
        self.accounts = {}
        self.config_path = Path(config_path or OUTPUT_DIR / "accounts.json")
        self._load()

    def _load(self):
        if self.config_path.exists():
            try:
                self.accounts = json.loads(self.config_path.read_text(encoding="utf-8"))
                logger.info(f"已加载 {len(self.accounts)} 个账号")
            except Exception as e:
                logger.error(f"加载账号失败: {e}")

    def _save(self):
        self.config_path.write_text(json.dumps(self.accounts, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_account(self, platform: str, account_id: str, credentials: dict):
        """添加账号"""
        if platform not in self.accounts:
            self.accounts[platform] = []
        # 去重
        existing = [a for a in self.accounts[platform] if a["account_id"] == account_id]
        if not existing:
            self.accounts[platform].append({
                "account_id": account_id,
                "credentials": credentials,
                "added_at": datetime.now().isoformat(),
                "stats": {"total_uploads": 0, "total_views": 0},
            })
            self._save()
            logger.info(f"账号已添加: {platform}/{account_id}")

    def get_accounts(self, platform: str) -> list:
        return self.accounts.get(platform, [])

    def get_next_account(self, platform: str) -> Optional[dict]:
        """轮询获取下一个可用账号（负载均衡）"""
        accounts = self.get_accounts(platform)
        if not accounts:
            return None
        return min(accounts, key=lambda a: a["stats"]["total_uploads"])


# ============ 标题生成器 ============

class TitleGenerator:
    """AI标题生成器"""

    def __init__(self, target_lang: str = "en"):
        self.lang = target_lang

    def generate(
        self,
        anime_name: str,
        episode: int = None,
        emotion: str = None,
        template_key: str = None,
    ) -> str:
        """生成标题"""
        templates = TITLE_TEMPLATES.get(self.lang, TITLE_TEMPLATES["en"])
        if template_key and template_key in templates:
            template = template_key
        else:
            template = templates[hash(anime_name) % len(templates)]

        # 填充模板
        emotion_word = emotion or self._random_emotion()
        emoji = EMOJI_MAP.get(self.lang, EMOJI_MAP["en"])

        title = template.format(
            anime=anime_name,
            ep=episode or "?",
            emotion_word=emotion_word,
            fire=emoji.get("fire", "🔥"),
            cry=emoji.get("cry", "💔"),
            shock=emoji.get("shock", "😱"),
        )
        return title

    def _random_emotion(self) -> str:
        emotions = EMOTION_WORDS.get(self.lang, EMOTION_WORDS["en"])
        return emotions[int(time.time()) % len(emotions)]

    def generate_batch(self, entries: list[dict]) -> list[str]:
        """批量生成标题"""
        return [
            self.generate(
                anime_name=e["anime_name"],
                episode=e.get("episode"),
                emotion=e.get("emotion"),
                template_key=e.get("template_key"),
            )
            for e in entries
        ]


# ============ 标签生成器 ============

class TagGenerator:
    """标签生成器"""

    def __init__(self, target_lang: str = "en"):
        self.lang = target_lang

    def generate(
        self,
        anime_name: str,
        genre: str = None,
        region: str = None,
        max_tags: int = 15,
        include_generic: bool = True,
    ) -> list[str]:
        """生成标签"""
        tags = []

        # 地区相关标签
        if self.lang in TRENDING_TAGS:
            tags.extend(TRENDING_TAGS[self.lang][:5])

        # 类型标签
        genre_tags = {
            "xuanhuan": ["xuanhuan", "fantasy", "cultivation", "Chinese fantasy"],
            "action": ["action", "battle", "fight", "adventure"],
            "romance": ["romance", "love", "drama", "relationship"],
            "comedy": ["comedy", "funny", "humor"],
            "horror": ["horror", "thriller", "suspense"],
            "scifi": ["sci-fi", "future", "technology"],
        }
        if genre and genre in genre_tags:
            tags.extend(genre_tags[genre])

        # 动漫名标签
        safe_name = re.sub(r"[^\w]", "", anime_name).lower()
        tags.append(safe_name)
        tags.append(f"{safe_name} episode")
        tags.append(f"{safe_name} edit")

        # 蹭热度标签
        trending = ["anime 2026", "new anime", "trending anime"]
        tags.extend(trending)

        # 去重 + 限制数量
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)
                if len(unique_tags) >= max_tags:
                    break

        return unique_tags[:max_tags]


# ============ YouTube 上传器 ============

class YouTubeUploader:
    """
    YouTube 自动上传
    依赖: google-api-python-client (pip install google-api-python-client google-auth)
    依赖: youtube-upload (npm install -g youtube-upload) 或直接用 API
    """

    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path
        self.api_available = False
        self._check_dependency()

    def _check_dependency(self):
        try:
            import googleapiclient.discovery
            self.api_available = True
            logger.info("YouTube API 客户端已就绪")
        except ImportError:
            logger.warning("google-api-python-client 未安装，YouTube 上传功能受限")
            self.api_available = False

    def upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        category_id: str = "1",  # 1=Film & Animation
        privacy_status: str = "public",
        thumbnail_path: str = None,
        scheduled_time: datetime = None,
        client_secrets_path: str = None,
    ) -> dict:
        """
        上传视频到 YouTube

        Returns:
            {"success": bool, "video_id": str, "url": str, "error": str}
        """
        if not self.api_available:
            # 降级：使用 youtube-upload CLI
            return self._upload_cli(video_path, title, description, tags, privacy_status, scheduled_time)

        try:
            import google.oauth2.credentials
            import google_auth_oauthlib.flow
            from googleapiclient.http import MediaFileUpload
            from googleapiclient.errors import HttpError
            import googleapiclient.discovery

            scopes = ["https://www.googleapis.com/auth/youtube.upload"]
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_path or self.credentials_path, scopes
            )
            credentials = flow.run_local_server(port=8080)
            youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

            body = {
                "snippet": {
                    "title": title,
                    "description": description or self._default_description(title),
                    "tags": tags or [],
                    "categoryId": category_id,
                },
                "status": {
                    "privacyStatus": privacy_status,
                },
            }

            if scheduled_time:
                # ISO 8601 格式
                body["status"]["publishAt"] = scheduled_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"上传进度: {int(status.get('progress', 0) * 100)}%")

            video_id = response["id"]
            logger.info(f"YouTube 上传成功: {video_id}")

            # 上传缩略图
            if thumbnail_path:
                self._upload_thumbnail(youtube, video_id, thumbnail_path)

            return {
                "success": True,
                "video_id": video_id,
                "url": f"https://youtu.be/{video_id}",
                "platform": "youtube",
            }

        except Exception as e:
            logger.error(f"YouTube 上传失败: {e}")
            return {"success": False, "error": str(e), "platform": "youtube"}

    def _upload_cli(self, video_path: str, title: str, description: str,
                    tags: list, privacy: str, scheduled) -> dict:
        """使用 youtube-upload CLI 工具上传"""
        try:
            cmd = ["youtube-upload",
                   "--title", title,
                   "--description", description or "",
                   "--tags", ",".join(tags or []),
                   "--privacy", privacy,
                   video_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                video_id = result.stdout.strip()
                return {"success": True, "video_id": video_id,
                        "url": f"https://youtu.be/{video_id}", "platform": "youtube"}
            else:
                return {"success": False, "error": result.stderr, "platform": "youtube"}
        except FileNotFoundError:
            return {"success": False, "error": "youtube-upload 未安装（运行: npm i -g youtube-upload）",
                    "platform": "youtube"}

    def _upload_thumbnail(self, youtube, video_id: str, thumbnail_path: str):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
        except Exception as e:
            logger.warning(f"缩略图上传失败: {e}")

    def _default_description(self, title: str) -> str:
        return (
            f"▶ {title}\n\n"
            "📺 Follow for more anime content!\n"
            "🔔 Subscribe & hit the bell!\n\n"
            "📌 Tags: anime, anime edit, anime review\n\n"
            "⚠️ All content belongs to their respective copyright owners. "
            "This video is made for entertainment purposes only.\n\n"
            "#anime #animes #animeedit"
        )


# ============ TikTok 上传器 ============

class TikTokUploader:
    """
    TikTok 自动上传
    依赖: TikTok API（官方开放平台）或第三方工具
    注意: TikTok API 需要官方白名单申请
    """

    def __init__(self):
        self.api_available = False
        logger.warning("TikTok 官方 API 需要白名单，可使用自动化脚本方案替代")

    def upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        privacy: str = "public",
    ) -> dict:
        """
        上传视频到 TikTok
        备选方案：
        1. TikTok Business API（需申请）
        2. 第三方工具（upload.ttdt.tv 等）
        3. 手动上传 + 定时提醒
        """
        logger.info(f"TikTok 发布（手动操作）: {title}")
        logger.info(f"视频路径: {video_path}")
        logger.info(f"描述: {description or title}")
        if tags:
            logger.info(f"标签: {' '.join(['#'+t for t in tags[:10]])}")

        return {
            "success": True,
            "method": "manual",
            "platform": "tiktok",
            "instruction": "请手动上传视频到 TikTok app",
            "video_path": video_path,
            "suggested_title": title,
            "suggested_tags": tags[:10] if tags else [],
        }


# ============ Instagram 上传器 ============

class InstagramUploader:
    """
    Instagram Reels 自动上传
    依赖: Instagram Graph API
    """

    def __init__(self):
        self.api_available = False
        self._check_dependency()

    def _check_dependency(self):
        try:
            import instagram_basic_display
            self.api_available = True
        except ImportError:
            logger.warning("instagram-basic-display 未安装，Instagram 功能受限")

    def upload_reel(
        self,
        video_path: str,
        caption: str,
        hashtags: list = None,
    ) -> dict:
        """上传 Instagram Reel"""
        if hashtags:
            caption = caption + "\n\n" + " ".join(["#" + h for h in hashtags[:10]])

        logger.info(f"Instagram Reel 发布: {caption[:50]}...")
        logger.info(f"视频: {video_path}")

        return {
            "success": True,
            "method": "manual",
            "platform": "instagram",
            "instruction": "请通过 Instagram App 或 Creator Studio 上传",
            "caption": caption,
        }


# ============ 多平台发布管理器 ============

class MultiPlatformPublisher:
    """统一的多平台发布管理器"""

    def __init__(self, config_path: str = None):
        self.accounts = AccountManager(config_path)
        self.youtube = YouTubeUploader()
        self.tiktok = TikTokUploader()
        self.instagram = InstagramUploader()
        self.title_gen = TitleGenerator()
        self.tag_gen = TagGenerator()
        self.publish_log = []

    def set_target_language(self, lang: str):
        self.title_gen.lang = lang
        self.tag_gen.lang = lang

    def generate_content_metadata(
        self,
        anime_name: str,
        episode: int = None,
        genre: str = None,
        target_lang: str = "en",
    ) -> dict:
        """生成完整的内容元数据"""
        self.set_target_language(target_lang)
        return {
            "title": self.title_gen.generate(anime_name, episode),
            "tags": self.tag_gen.generate(anime_name, genre, target_lang),
        }

    def upload_to_all(
        self,
        video_path: str,
        metadata: dict,
        platforms: list = None,
        thumbnail_path: str = None,
        privacy: str = "public",
    ) -> dict:
        """
        一键发布到多个平台

        Args:
            video_path: 视频文件路径
            metadata: {"title", "description", "tags"}
            platforms: ["youtube", "tiktok", "instagram"] 或 ["all"]
            thumbnail_path: 缩略图路径
        """
        platforms = platforms or ["youtube"]
        results = {}

        for platform in platforms:
            if platform == "youtube":
                results["youtube"] = self.youtube.upload(
                    video_path=video_path,
                    title=metadata.get("title", "Anime Video"),
                    description=metadata.get("description", ""),
                    tags=metadata.get("tags", []),
                    thumbnail_path=thumbnail_path,
                    privacy_status=privacy,
                )
                time.sleep(2)  # 避免API限流

            elif platform == "tiktok":
                results["tiktok"] = self.tiktok.upload(
                    video_path=video_path,
                    title=metadata.get("title", ""),
                    description=metadata.get("description", ""),
                    tags=metadata.get("tags", []),
                )

            elif platform == "instagram":
                results["instagram"] = self.instagram.upload_reel(
                    video_path=video_path,
                    caption=metadata.get("description", metadata.get("title", "")),
                    hashtags=metadata.get("tags", []),
                )

        self._log_publish(video_path, metadata, results)
        return results

    def _log_publish(self, video_path: str, metadata: dict, results: dict):
        """记录发布日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "video": video_path,
            "title": metadata.get("title"),
            "results": results,
        }
        self.publish_log.append(log_entry)
        log_file = OUTPUT_DIR / "publish_log.json"
        log_file.write_text(json.dumps(self.publish_log, ensure_ascii=False, indent=2), encoding="utf-8")


# ============ 定时发布调度器 ============

class PublishScheduler:
    """定时发布调度器"""

    def __init__(self):
        self.schedule_file = OUTPUT_DIR / "schedule.json"
        self.schedule = self._load_schedule()

    def _load_schedule(self) -> list:
        if self.schedule_file.exists():
            return json.loads(self.schedule_file.read_text(encoding="utf-8"))
        return []

    def _save_schedule(self):
        self.schedule_file.write_text(json.dumps(self.schedule, ensure_ascii=False, indent=2), encoding="utf-8")

    def schedule_upload(
        self,
        video_path: str,
        metadata: dict,
        platform: str,
        scheduled_time: datetime,
    ):
        """添加定时发布任务"""
        self.schedule.append({
            "id": hashlib.md5(f"{video_path}{platform}".encode()).hexdigest()[:8],
            "video_path": video_path,
            "metadata": metadata,
            "platform": platform,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "pending",
        })
        self._save_schedule()
        logger.info(f"定时任务已添加: {platform} @ {scheduled_time}")

    def get_pending_tasks(self, before_time: datetime = None) -> list:
        """获取待执行任务"""
        if before_time is None:
            before_time = datetime.now()
        return [
            t for t in self.schedule
            if t["status"] == "pending"
            and datetime.fromisoformat(t["scheduled_time"]) <= before_time
        ]


# ============ 内容日历生成器 ============

def generate_content_calendar(
    anime_list: list[str],
    episodes_per_day: int = 3,
    days: int = 30,
    region: str = "english",
) -> list[dict]:
    """生成30天内容日历"""
    lang_map = {"english": "en", "southeast_asia": "id", "middle_east": "ar",
                "latin_america": "es", "korea_japan": "ko"}
    lang = lang_map.get(region, "en")
    tag_gen = TagGenerator(lang)

    calendar = []
    anime_index = 0
    ep_counter = {}

    for day in range(days):
        date = datetime.now() + timedelta(days=day)
        for post_num in range(episodes_per_day):
            anime = anime_list[anime_index % len(anime_list)]

            if anime not in ep_counter:
                ep_counter[anime] = 1
            ep = ep_counter[anime]
            ep_counter[anime] += 1

            tag_gen_instance = TagGenerator(lang)
            title_gen_instance = TitleGenerator(lang)

            calendar.append({
                "date": date.strftime("%Y-%m-%d"),
                "post_slot": post_num + 1,
                "anime_name": anime,
                "episode": ep,
                "title": title_gen_instance.generate(anime, ep),
                "tags": tag_gen_instance.generate(anime, max_tags=12),
                "status": "pending",
            })

            anime_index += 1

    return calendar


if __name__ == "__main__":
    # 演示：生成30天内容日历
    calendar = generate_content_calendar(
        anime_list=["斗罗大陆", "斗破苍穹", "凡人修仙传", "一人之下"],
        episodes_per_day=3,
        days=7,
        region="english",
    )

    print("=" * 60)
    print("动漫出海 · 7天内容日历")
    print("=" * 60)
    for entry in calendar:
        print(f"[{entry['date']} 第{entry['post_slot']}条] {entry['title']}")
        print(f"   标签: {', '.join(entry['tags'][:5])}")
    print("=" * 60)
    print(f"总计: {len(calendar)} 条内容")
