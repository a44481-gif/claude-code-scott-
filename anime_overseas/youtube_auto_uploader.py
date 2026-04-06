"""
YouTube 全自动上传器
anime_overseas/youtube_auto_uploader.py

功能：
1. YouTube OAuth 授权登录
2. 自动上传视频（无需浏览器）
3. 自动设置标题、描述、标签
4. 支持定时发布
5. 支持多账号切换

用法:
    uploader = YouTubeUploader()
    uploader.authenticate()  # 首次运行，会打开浏览器授权
    uploader.upload("video.mp4", title="...", description="...", tags=["a","b"])
"""

import os
import sys
import io
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 确保utf-8输出
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent
CLIENT_SECRETS = BASE_DIR / "client_secrets.json"
TOKEN_FILE = BASE_DIR / "youtube_token.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("YouTubeUploader")

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def check_dependencies():
    """检查依赖是否安装"""
    missing = []
    try:
        import googleapiclient.discovery
    except ImportError:
        missing.append("google-api-python-client")
    try:
        import google.oauth2.credentials
    except ImportError:
        missing.append("google-auth")
    try:
        import google_auth_oauthlib.flow
    except ImportError:
        missing.append("google-auth-oauthlib")

    if missing:
        print(f"缺少依赖，请运行安装：")
        print(f"pip install {' '.join(missing)}")
        return False
    return True


class YouTubeUploader:
    """YouTube 自动上传器"""

    def __init__(self, credentials_path: str = None):
        self.credentials_path = Path(credentials_path or str(CLIENT_SECRETS))
        self.token_path = Path(str(self.credentials_path).replace(".json", "_token.json"))
        self.youtube = None
        self.channel_id = None

    def authenticate(self) -> bool:
        """
        OAuth 授权（首次运行会自动打开浏览器）
        """
        if not check_dependencies():
            return False

        if not self.credentials_path.exists():
            print(f"\n{'='*60}")
            print("錯誤：找不到 client_secrets.json")
            print(f"請把下載的 JSON 文件放到：{self.credentials_path}")
            print(f"然後重新運行這個腳本。")
            print(f"{'='*60}\n")
            return False

        try:
            import google.oauth2.credentials
            import google_auth_oauthlib.flow
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError

            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path), YOUTUBE_SCOPES
            )

            # 尝试加载已保存的 token
            credentials = None
            if self.token_path.exists():
                try:
                    credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(
                        str(self.token_path), YOUTUBE_SCOPES
                    )
                    if credentials and credentials.valid:
                        logger.info("已加载保存的授权令牌")
                except Exception:
                    credentials = None

            # 如果没有有效 token，重新授权
            if not credentials or not credentials.valid:
                print("\n正在打开浏览器进行授权...")
                print("请在浏览器中登录 Google 账号并授权。\n")
                credentials = flow.run_local_server(
                    port=8080,
                    prompt="consent",
                    access_type="offline"
                )
                # 保存 token
                with open(self.token_path, "w") as f:
                    f.write(credentials.to_json())
                print("授权已保存，下次运行无需重新授权。\n")

            self.youtube = build("youtube", "v3", credentials=credentials)
            logger.info("YouTube API 认证成功！")

            # 获取频道信息
            response = self.youtube.channels().list(part="snippet,contentDetails", mine=True).execute()
            if response["items"]:
                self.channel_id = response["items"][0]["id"]
                title = response["items"][0]["snippet"]["title"]
                print(f"已绑定频道：{title}")
            return True

        except Exception as e:
            logger.error(f"认证失败: {e}")
            print(f"\n认证失败: {e}")
            print("\n请确保：")
            print("1. client_secrets.json 文件正确放置")
            print("2. 你的 Google 账号可以访问 YouTube")
            print("3. 网络可以访问 Google 服务")
            return False

    def upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        category_id: str = "1",  # 1=Film, 22=People, 23=Comedy, 24=Entertainment, 28=Science & Tech
        privacy_status: str = "public",
        thumbnail_path: str = None,
        scheduled_time: datetime = None,
    ) -> dict:
        """
        上传视频到 YouTube

        Returns:
            {"success": bool, "video_id": str, "url": str, "error": str}
        """
        if not self.youtube:
            return {"success": False, "error": "未认证，请先调用 authenticate()", "platform": "youtube"}

        if not Path(video_path).exists():
            return {"success": False, "error": f"视频文件不存在: {video_path}", "platform": "youtube"}

        try:
            from googleapiclient.http import MediaFileUpload
            from googleapiclient.errors import HttpError

            body = {
                "snippet": {
                    "title": title[:100],  # YouTube 标题最长100字符
                    "description": (description or "")[:5000],
                    "tags": (tags or [])[:500],  # 标签最多500字符
                    "categoryId": category_id,
                    "defaultLanguage": "en",
                    "localized": {
                        "title": title[:100],
                        "description": (description or "")[:5000],
                    },
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False,
                },
            }

            if scheduled_time:
                body["status"]["publishAt"] = scheduled_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                logger.info(f"定时发布: {scheduled_time}")

            # 上传
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            print(f"\n正在上传: {title}")
            print(f"文件: {video_path}")

            response = None
            uploaded = 0
            while response is None:
                status, response = request.next_chunk()
                if status:
                    pct = int(status.get("progress", 0) * 100)
                    if pct > uploaded:
                        print(f"\r  上传进度: {pct}%", end="", flush=True)
                        uploaded = pct

            video_id = response["id"]
            video_url = f"https://youtu.be/{video_id}"

            print(f"\n\n{'='*60}")
            print(f"上传成功!")
            print(f"视频ID: {video_id}")
            print(f"链接: {video_url}")
            print(f"{'='*60}\n")

            # 上传缩略图
            if thumbnail_path and Path(thumbnail_path).exists():
                try:
                    self.youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_path)
                    ).execute()
                    print("缩略图上传成功")
                except Exception as e:
                    print(f"缩略图上传失败: {e}")

            return {
                "success": True,
                "video_id": video_id,
                "url": video_url,
                "platform": "youtube",
                "title": title,
            }

        except HttpError as e:
            error_msg = f"HTTP错误: {e.resp.status} - {e.error_details}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "platform": "youtube"}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"上传失败: {e}")
            return {"success": False, "error": error_msg, "platform": "youtube"}

    def upload_batch(self, videos: list[dict]) -> list[dict]:
        """
        批量上传视频
        videos: [{"video_path": "...", "title": "...", "description": "...", "tags": [...]}, ...]
        """
        results = []
        for i, video in enumerate(videos, 1):
            print(f"\n{'='*60}")
            print(f"批量上传 {i}/{len(videos)}")
            print(f"{'='*60}")
            result = self.upload(
                video_path=video["video_path"],
                title=video["title"],
                description=video.get("description", ""),
                tags=video.get("tags", []),
                category_id=video.get("category_id", "1"),
                privacy_status=video.get("privacy", "public"),
                thumbnail_path=video.get("thumbnail"),
                scheduled_time=video.get("scheduled"),
            )
            results.append(result)
            if i < len(videos):
                print("等待10秒后上传下一个...\n")
                import time; time.sleep(10)
        return results

    def get_channel_stats(self) -> dict:
        """获取频道统计"""
        if not self.youtube:
            return {}
        try:
            response = self.youtube.channels().list(
                part="statistics,snippet,contentDetails",
                mine=True
            ).execute()
            if response["items"]:
                stats = response["items"][0]["statistics"]
                return {
                    "subscribers": int(stats.get("viewCount", 0)),
                    "views": int(stats.get("subscriberCount", 0)),
                    "videos": int(stats.get("videoCount", 0)),
                    "title": response["items"][0]["snippet"]["title"],
                }
        except Exception as e:
            logger.error(f"获取频道统计失败: {e}")
        return {}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="YouTube 自动上传工具")
    parser.add_argument("--video", "-v", help="视频文件路径")
    parser.add_argument("--title", "-t", help="视频标题")
    parser.add_argument("--description", "-d", help="视频描述")
    parser.add_argument("--tags", help="标签（逗号分隔）", default="anime,chinese anime")
    parser.add_argument("--thumbnail", help="缩略图路径")
    parser.add_argument("--batch", help="批量文件（JSON）")
    parser.add_argument("--auth-only", action="store_true", help="仅测试认证")
    args = parser.parse_args()

    uploader = YouTubeUploader()

    # 先认证
    if not uploader.authenticate():
        sys.exit(1)

    if args.auth_only:
        print("认证测试通过！")
        sys.exit(0)

    # 批量上传
    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            videos = json.load(f)
        print(f"\n批量上传 {len(videos)} 个视频...")
        results = uploader.upload_batch(videos)
        for r in results:
            status = "成功" if r.get("success") else "失败"
            print(f"  [{status}] {r.get('title', '未知')}")
            if r.get("success"):
                print(f"    URL: {r.get('url')}")
            else:
                print(f"    错误: {r.get('error')}")
        return

    # 单个上传
    if args.video:
        result = uploader.upload(
            video_path=args.video,
            title=args.title or Path(args.video).stem,
            description=args.description or "",
            tags=args.tags.split(",") if args.tags else [],
            thumbnail_path=args.thumbnail,
        )
        if result["success"]:
            print(f"\n上传成功: {result['url']}")
        else:
            print(f"\n上传失败: {result.get('error')}")
        return

    # 无参数：演示
    print("\n用法示例：")
    print("  python youtube_auto_uploader.py --video video.mp4 \\")
    print("    --title 'My Anime Video' \\")
    print("    --description 'Check out this anime!' \\")
    print("    --tags 'anime,donghua' \\")
    print("    --thumbnail thumb.png")


if __name__ == "__main__":
    main()
