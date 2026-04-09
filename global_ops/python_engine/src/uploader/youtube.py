"""
GlobalOPS · YouTube 上传器
支持 API 模式和 Selenium 降级模式
"""

import logging
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger("GlobalOPS.YouTube")

# 复用 anime_overseas 的 Selenium 降级方案
ANIME_OPS_BASE = Path("d:/claude mini max 2.7/anime_overseas")


class YouTubeUploader:
    """YouTube 视频上传器"""

    def __init__(self, account: dict):
        self.account = account
        self.platform = "youtube"
        self.credentials = account.get("credentials", {})
        self.cookies_file = Path("d:/claude mini max 2.7/anime_overseas/data/youtube_cookies.json")

    def upload_content(self, content: dict) -> Optional[dict]:
        """
        上传单条内容到 YouTube
        返回 {'id': video_id, 'url': watch_url} 或 None
        """
        title = content.get("title_en") or content.get("title", "")
        description = content.get("caption_en") or content.get("caption", "")
        tags = content.get("tags", [])
        tags = tags[:30] if isinstance(tags, list) else []

        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")][:30]

        video_file = content.get("source_file")
        thumbnail_file = content.get("thumbnail_output")

        # 优先使用 API 模式（有完整凭证时）
        if self._has_api_credentials():
            return self._upload_api(video_file, title, description, tags, thumbnail_file)
        # 降级使用 Selenium（已有登录 Cookie）
        elif self.cookies_file.exists():
            return self._upload_selenium(video_file, title, description, tags, thumbnail_file)
        else:
            logger.error("没有可用的 YouTube 上传方式（无 API 凭证且无 Cookie）")
            return None

    def _has_api_credentials(self) -> bool:
        client_id = self.credentials.get("client_id") or ""
        client_secret = self.credentials.get("client_secret") or ""
        refresh_token = self.credentials.get("refresh_token") or ""
        return bool(client_id and client_secret and refresh_token)

    def _upload_api(self, video_file: str, title: str, description: str, tags: list, thumbnail: str = None) -> Optional[dict]:
        """使用 YouTube Data API v3 上传"""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.http import MediaFileUpload
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_info(self.credentials)
            youtube = build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description[:5000],
                    "tags": tags[:500],
                    "categoryId": "22",  # People & Blogs
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                },
            }

            media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"   上传进度: {int(status.progress() * 100)}%")

            video_id = response["id"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"✅ API上传成功: {video_url}")
            return {"id": video_id, "url": video_url}

        except Exception as e:
            logger.error(f"API上传失败: {e}")
            return None

    def _upload_selenium(self, video_file: str, title: str, description: str, tags: list, thumbnail: str = None) -> Optional[dict]:
        """
        Selenium 降级上传（复用已登录 Chrome 会话）
        来自 anime_overseas/anime_ops.py 的成熟方案
        """
        if not video_file or not Path(video_file).exists():
            logger.error(f"视频文件不存在: {video_file}")
            return None

        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import webdriver_manager

            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

            driver = webdriver.Chrome(
                service=Service(webdriver_manager.chrome.ChromeDriverManager().install()),
                options=chrome_options
            )

            driver.get("https://www.youtube.com/upload")
            time.sleep(5)

            # 上传文件
            input_box = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            input_box.send_keys(str(Path(video_file).resolve()))
            logger.info("   视频文件已选择，等待上传...")

            # 等待上传完成
            time.sleep(8)

            # 设置标题
            title_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="title"]'))
            )
            title_input.clear()
            title_input.send_keys(title[:100])

            # 设置描述
            desc_box = driver.find_element(By.CSS_SELECTOR, 'textarea[name="description"]')
            desc_box.clear()
            desc_box.send_keys(description[:5000])

            # 公开
            privacy_btn = driver.find_element(By.XPATH, '//*[@id="privacy-radios"]/label[1]')
            privacy_btn.click()

            # 发布
            publish_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            publish_btn.click()
            logger.info("   点击发布，等待处理...")

            time.sleep(10)

            current_url = driver.current_url
            if "watch" in current_url:
                video_id = current_url.split("v=")[-1].split("&")[0]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                logger.info(f"✅ Selenium上传成功: {video_url}")
                driver.quit()
                return {"id": video_id, "url": video_url}
            else:
                logger.warning(f"未能获取视频ID，当前URL: {current_url}")
                driver.quit()
                return {"id": None, "url": None}

        except Exception as e:
            logger.error(f"Selenium上传失败: {e}")
            return None
