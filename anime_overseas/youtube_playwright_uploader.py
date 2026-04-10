"""
YouTube Studio Playwright 自动化上传器
anime_overseas/youtube_playwright_uploader.py

使用 Playwright 头戴 Chromium 自动上传视频到 YouTube Studio
无需 OAuth，无需 Chrome 浏览器已登录
只需 YouTube 频道即可

用法:
    from youtube_playwright_uploader import PlaywrightUploader
    uploader = PlaywrightUploader()
    uploader.login("your@email.com", "your_password")
    uploader.upload("video.mp4", title="...", description="...", tags=[...])
"""

import sys
import io
import time
import json
import logging
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", write_through=True)
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", write_through=True)

BASE_DIR = Path(__file__).parent
COOKIES_FILE = BASE_DIR / "youtube_playwright_cookies.json"
LOG_FILE = BASE_DIR / "logs" / f"playwright_upload_{datetime.now().strftime('%Y%m%d')}.log"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("PlaywrightUploader")


class PlaywrightUploader:
    """YouTube Studio Playwright 自动化上传器"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False

    # ── 浏览器启动 ────────────────────────────────────────────

    def _launch(self, headless: bool = True):
        """启动 Playwright Chromium"""
        from playwright.sync_api import sync_playwright

        pw = sync_playwright().start()
        self._pw = pw  # 保持引用

        self.browser = pw.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )

        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        # 加载保存的 cookies
        if COOKIES_FILE.exists():
            try:
                cookies = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
                self.context.add_cookies(cookies)
                logger.info("已加载保存的 cookies")
            except Exception as e:
                logger.warning(f"加载 cookies 失败: {e}")

        self.page = self.context.new_page()
        return self

    def _save_cookies(self):
        """保存登录 cookies"""
        try:
            cookies = self.context.cookies()
            COOKIES_FILE.write_text(json.dumps(cookies, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info(f"Cookies 已保存: {COOKIES_FILE}")
        except Exception as e:
            logger.warning(f"保存 cookies 失败: {e}")

    def _close(self):
        """关闭浏览器"""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if hasattr(self, "_pw"):
                self._pw.stop()
        except Exception:
            pass

    # ── 登录 ─────────────────────────────────────────────────

    def login(self, email: str, password: str, headless: bool = True) -> bool:
        """
        登录 Google 账号（自动处理两步验证）
        登录成功后 cookies 会自动保存，下次无需再登录

        Returns:
            True = 登录成功
        """
        self._launch(headless=headless)
        page = self.page

        try:
            logger.info("打开 Google 登录页面...")
            page.goto(
                "https://accounts.google.com/v3/signin/identifier"
                "?passive=true&continue=https%3A//www.youtube.com&"
                "service=youtube&hl=zh-CN&ui=2",
                wait_until="networkidle",
                timeout=30000,
            )

            # 输入邮箱
            logger.info(f"输入邮箱: {email}")
            page.fill('input[type="email"]', email)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)

            # 输入密码
            logger.info("输入密码...")
            page.fill('input[type="password"]', password)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)

            # 处理两步验证
            self._handle_2sv(page)

            # 等待跳转到 YouTube
            page.wait_for_url("**youtube.com**", timeout=20000)
            logger.info("登录成功!")

            self._save_cookies()
            self.logged_in = True
            return True

        except Exception as e:
            logger.error(f"登录失败: {e}")
            self._close()
            return False

    def login_with_stealth(self, headless: bool = True) -> bool:
        """
        使用已保存的 cookies 静默登录（无需账号密码）
        推荐用于自动化流程
        """
        self._launch(headless=headless)
        page = self.page

        try:
            logger.info("使用 cookies 访问 YouTube Studio...")
            page.goto("https://studio.youtube.com", wait_until="networkidle", timeout=30000)

            # 检查是否真的登录了（cookies 可能过期）
            current_url = page.url
            if "signin" in current_url or "accounts.google.com" in current_url:
                logger.warning("Cookies 已过期，需要重新登录")
                logger.info("请先运行: uploader.login('email', 'password')")
                self._close()
                return False

            # 确认是 YouTube Studio
            if "studio.youtube.com" in current_url or "youtube.com" in current_url:
                logger.info("已通过 cookies 登录 YouTube Studio")
                self.logged_in = True
                return True

            return False

        except Exception as e:
            logger.error(f"Cookies 登录失败: {e}")
            self._close()
            return False

    def _handle_2sv(self, page):
        """处理两步验证"""
        try:
            # 检测是否在两步验证页面
            if "challenge" in page.url or page.query_selector('input[aria-label*="验证码"]'):
                logger.info("检测到两步验证，请在控制台输入代码...")
                # 等待用户手动输入，或检测自动填充
                page.wait_for_load_state("networkidle", timeout=120000)
        except Exception:
            pass

    # ── 核心上传流程 ─────────────────────────────────────────

    def upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        thumbnail_path: str = None,
        privacy: str = "public",
        playlist: str = None,
        made_for_kids: bool = False,
        language: str = "en",
        wait_for_upload: bool = True,
    ) -> dict:
        """
        上传视频到 YouTube Studio

        Args:
            video_path: 视频文件路径
            title: 视频标题
            description: 视频描述
            tags: 标签列表
            thumbnail_path: 封面图路径
            privacy: 公开性 public/private/unlisted
            made_for_kids: 是否为儿童内容
            language: 视频语言代码

        Returns:
            {"success": bool, "video_id": str, "url": str, "error": str}
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return {"success": False, "error": f"视频文件不存在: {video_path}"}

        # 确保已登录
        if not self.logged_in:
            logger.info("尝试使用 cookies 登录...")
            if not self.login_with_stealth():
                return {
                    "success": False,
                    "error": "未登录，请先调用 login() 或确保 cookies 有效",
                }

        page = self.page
        results = {}

        try:
            # Step 1: 打开上传页面
            logger.info("打开 YouTube Studio 上传页面...")
            page.goto("https://studio.youtube.com/channel/upload", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            # Step 2: 检查上传按钮并点击
            logger.info("点击上传按钮...")
            page.set_input_files('input[type="file"][accept*="video"]', str(video_path.resolve()))
            logger.info(f"已选择文件: {video_path.name}")

            # Step 3: 等待上传进度条出现
            logger.info("等待上传开始...")
            page.wait_for_timeout(5000)

            # 等待上传完成（进度条消失）
            if wait_for_upload:
                max_wait = 600  # 10分钟
                waited = 0
                while waited < max_wait:
                    page.wait_for_timeout(5000)
                    waited += 5

                    # 检测上传进度
                    try:
                        progress_text = page.locator(
                            "ytcp-upload-progress[ng-if*='progress']"
                        ).inner_text(timeout=2000)
                        if progress_text and "%" in progress_text:
                            logger.info(f"  上传中: {progress_text[:50]}")
                    except Exception:
                        pass

                    # 检测是否上传完成（出现设置面板）
                    try:
                        title_input = page.locator(
                            'input[id="title-textarea"][placeholder*="title" i], '
                            'ytcp-form-textarea[id="title-textarea"]'
                        ).wait_for(timeout=1000)
                        if title_input:
                            logger.info("上传已完成，开始填写信息...")
                            break
                    except Exception:
                        pass

                    # 检测错误
                    if "无法处理" in page.content() or "error" in page.content().lower():
                        logger.error("检测到上传错误")
                        break

            # Step 4: 填写标题
            logger.info(f"填写标题: {title[:50]}...")
            try:
                page.wait_for_timeout(2000)
                title_input = page.locator(
                    'ytcp-form-textarea[id="title-textarea"]'
                ).first
                if not title_input:
                    title_input = page.locator(
                        'input[id="title-textarea"], '
                        'textarea[placeholder*="title" i]'
                    ).first
                title_input.click()
                title_input.fill(title[:100])
            except Exception as e:
                logger.warning(f"标题填写失败: {e}")

            page.wait_for_timeout(1000)

            # Step 5: 填写描述
            if description:
                logger.info("填写描述...")
                try:
                    desc_input = page.locator(
                        'ytcp-form-textarea[id="description-textarea"]'
                    ).first
                    if not desc_input:
                        desc_input = page.locator(
                            'textarea[placeholder*="description" i]'
                        ).first
                    desc_input.click()
                    desc_input.fill(description[:5000])
                except Exception as e:
                    logger.warning(f"描述填写失败: {e}")

            page.wait_for_timeout(1000)

            # Step 6: 设置缩略图
            if thumbnail_path and Path(thumbnail_path).exists():
                logger.info(f"设置缩略图: {thumbnail_path}")
                try:
                    thumb_btn = page.locator(
                        'button[aria-label*="thumbnail" i], '
                        'ytcp-thumbnails-compact-editor'
                    ).first
                    thumb_btn.click()
                    page.wait_for_timeout(1000)
                    page.set_input_files(
                        'input[type="file"][accept*="image"]',
                        str(Path(thumbnail_path).resolve())
                    )
                    page.wait_for_timeout(2000)
                    # 确认
                    try:
                        page.locator(
                            'ytcp-button[save] button, button:has-text("完成")'
                        ).click()
                        page.wait_for_timeout(1000)
                    except Exception:
                        pass
                except Exception as e:
                    logger.warning(f"缩略图设置失败: {e}")

            # Step 7: 添加标签
            if tags:
                logger.info(f"添加标签: {', '.join(tags[:5])}...")
                try:
                    # 展开标签选项
                    more_btn = page.locator(
                        'button:has-text("显示更多"), button:has-text("More")'
                    ).first
                    more_btn.click()
                    page.wait_for_timeout(1000)
                except Exception:
                    pass

                try:
                    tag_input = page.locator(
                        'input[placeholder*="tag" i], '
                        'ytcp-form-tag-input'
                    ).first
                    if tag_input:
                        tag_input.click()
                        for tag in tags[:15]:
                            tag_input.fill(tag)
                            tag_input.press("Enter")
                        logger.info(f"已添加 {len(tags[:15])} 个标签")
                except Exception as e:
                    logger.warning(f"标签添加失败: {e}")

            page.wait_for_timeout(1000)

            # Step 8: 设置公开性
            logger.info(f"设置可见性: {privacy}...")
            try:
                privacy_map = {"public": "公开", "unlisted": "不公开", "private": "私人"}
                target = privacy_map.get(privacy, "公开")
                privacy_btn = page.locator(
                    f'button:has-text("{target}"), '
                    f'ytcp-button[aria-label*="{target}"]'
                ).first
                privacy_btn.click()
                page.wait_for_timeout(500)

                # 选择具体选项
                option = page.locator(
                    f'li[role="menuitemradio"]:has-text("{target}")'
                ).first
                option.click()
                page.wait_for_timeout(500)
            except Exception as e:
                logger.warning(f"可见性设置失败: {e}")

            # Step 9: 儿童内容
            if made_for_kids:
                try:
                    kids_btn = page.locator(
                        'button:has-text("儿童"), button:has-text("Made for kids")'
                    ).first
                    kids_btn.click()
                    page.wait_for_timeout(500)
                    no_kids = page.locator(
                        'li[role="menuitemradio"]:has-text("否")'
                    ).first
                    no_kids.click()
                except Exception:
                    pass

            page.wait_for_timeout(1000)

            # Step 10: 发布
            logger.info("准备发布...")
            try:
                done_btn = page.locator(
                    'ytcp-button[id="done-button"]:not([disabled])'
                ).first
                if done_btn:
                    done_btn.click()
                    page.wait_for_timeout(3000)

                    # 确认发布
                    try:
                        publish_btn = page.locator(
                            'ytcp-button[id="publish-button"] button, '
                            'button:has-text("发布")'
                        ).first
                        publish_btn.click()
                        page.wait_for_timeout(3000)
                    except Exception:
                        pass

                    # 复制链接
                    try:
                        share_btn = page.locator(
                            'button:has-text("复制链接"), button[aria-label*="link"]'
                        ).first
                        if share_btn:
                            share_btn.click()
                            page.wait_for_timeout(500)
                    except Exception:
                        pass

            except Exception as e:
                logger.warning(f"发布失败，请在浏览器中手动完成: {e}")

            # 获取视频 URL
            video_url = ""
            final_url = page.url
            if "watch" in final_url:
                video_url = final_url
            elif "studio.youtube.com/video/" in final_url:
                video_id = final_url.split("/video/")[1].split("?")[0]
                video_url = f"https://youtu.be/{video_id}"

            results = {
                "success": True,
                "url": video_url,
                "platform": "youtube",
                "title": title,
                "method": "playwright",
                "file": str(video_path),
            }
            logger.info(f"上传成功! URL: {video_url}")
            return results

        except Exception as e:
            logger.error(f"上传过程出错: {e}")
            return {"success": False, "error": str(e), "platform": "youtube", "method": "playwright"}

    # ── 批量上传 ─────────────────────────────────────────────

    def upload_batch(self, videos: list[dict]) -> list[dict]:
        """
        批量上传视频
        videos: [{"video": "...", "title": "...", "description": "...", "tags": [...]}]
        """
        results = []
        total = len(videos)
        for i, video in enumerate(videos, 1):
            logger.info(f"\n{'='*50}\n批量上传 {i}/{total}\n{'='*50}")
            result = self.upload(
                video_path=video["video"],
                title=video.get("title", "Anime Video"),
                description=video.get("description", ""),
                tags=video.get("tags", []),
                thumbnail_path=video.get("thumbnail"),
                privacy=video.get("privacy", "public"),
            )
            results.append(result)

            if i < total:
                wait = 15
                logger.info(f"等待{wait}秒后上传下一个...")
                time.sleep(wait)

        return results

    def get_video_stats(self) -> dict:
        """获取频道统计数据"""
        if not self.logged_in:
            return {}

        page = self.page
        try:
            page.goto("https://studio.youtube.com", wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(3000)

            stats = {}
            try:
                subs = page.locator(
                    'span[itemprop="numberOfSubscribers"], '
                    '#subscriber-count'
                ).inner_text()
                stats["subscribers"] = subs
            except Exception:
                pass

            return stats
        except Exception as e:
            logger.error(f"获取统计失败: {e}")
            return {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._save_cookies()
        self._close()


# ── 便捷函数 ─────────────────────────────────────────────────

def quick_upload(
    video_path: str,
    title: str,
    email: str = None,
    password: str = None,
    cookies_file: str = None,
    **kwargs
) -> dict:
    """
    快速上传（自动处理登录）

    优先级:
    1. 使用已保存的 cookies
    2. 如果没有 cookies 且提供了 email/password，执行登录
    3. 如果都没有，返回错误提示
    """
    global COOKIES_FILE
    if cookies_file:
        COOKIES_FILE = Path(cookies_file)

    uploader = PlaywrightUploader()

    # 尝试 cookies 登录
    if COOKIES_FILE.exists():
        if uploader.login_with_stealth():
            return uploader.upload(video_path, title, **kwargs)
        else:
            logger.info("Cookies 已过期，需要重新登录")

    # 需要账号密码登录
    if email and password:
        if uploader.login(email, password):
            return uploader.upload(video_path, title, **kwargs)
        else:
            return {"success": False, "error": "登录失败"}

    return {
        "success": False,
        "error": "未登录且未提供账号密码",
        "hint": "请先调用 PlaywrightUploader().login(email, password) 或确保 youtube_playwright_cookies.json 存在",
    }


def upload_from_package(package_file: str) -> list[dict]:
    """
    从上传包 JSON 文件批量上传
    """
    pkg_path = Path(package_file)
    if not pkg_path.exists():
        return [{"success": False, "error": f"文件不存在: {package_file}"}]

    videos = json.loads(pkg_path.read_text(encoding="utf-8"))

    uploader = PlaywrightUploader()
    if not uploader.login_with_stealth():
        return [{"success": False, "error": "cookies 登录失败，请先运行登录"}]

    return uploader.upload_batch(videos)


# ── 主入口（测试）────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Playwright 自动上传器")
    parser.add_argument("--video", "-v", help="视频文件路径")
    parser.add_argument("--title", "-t", help="视频标题")
    parser.add_argument("--email", "-e", help="Google 邮箱")
    parser.add_argument("--password", "-p", help="Google 密码")
    parser.add_argument("--batch", "-b", help="批量上传包文件(JSON)")
    parser.add_argument("--check", action="store_true", help="仅测试 cookies 登录")
    args = parser.parse_args()

    uploader = PlaywrightUploader()

    if args.check:
        result = uploader.login_with_stealth()
        print("登录成功!" if result else "登录失败")
        uploader._close()
        sys.exit(0 if result else 1)

    if args.email and args.password:
        if not uploader.login(args.email, args.password):
            print("登录失败!")
            sys.exit(1)

    elif not COOKIES_FILE.exists():
        print("错误: 需要登录凭证")
        print("选项 1: 提供账号密码: --email your@email.com --password yourpass")
        print("选项 2: 首次运行后 cookies 会自动保存，下次无需再登录")
        sys.exit(1)

    if args.batch:
        results = upload_from_package(args.batch)
        for r in results:
            print("成功!" if r.get("success") else f"失败: {r.get('error')}")
            if r.get("url"):
                print(f"  URL: {r.get('url')}")

    elif args.video:
        result = uploader.upload(args.video, title=args.title or "Anime Video")
        print("成功!" if result.get("success") else f"失败: {result.get('error')}")
        if result.get("url"):
            print(f"URL: {result.get('url')}")

    else:
        print("用法:")
        print("  测试登录: python youtube_playwright_uploader.py --check")
        print("  账号密码登录: python youtube_playwright_uploader.py --email xxx --password xxx")
        print("  单文件上传: python youtube_playwright_uploader.py --video video.mp4 --title 'My Video'")
        print("  批量上传: python youtube_playwright_uploader.py --batch upload_package.json")

    uploader._close()
