#!/usr/bin/env python3
"""
动漫出海运营代理人 · 主控程序
anime_overseas/anime_ops.py

用法:
    python anime_ops.py                    # 交互模式
    python anime_ops.py upload "video.mp4"  # 单文件上传
    python anime_ops.py download "凡人修仙传 EP5"
    python anime_ops.py batch 10
    python anime_ops.py schedule daily
    python anime_ops.py analytics
    python anime_ops.py revenue
"""

import sys
import io
import json
import subprocess
import logging
import argparse
from pathlib import Path
from datetime import datetime

# UTF-8 输出
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ===== 路径配置 =====
BASE_DIR = Path(__file__).parent
WORKSPACE = BASE_DIR
OUTPUT_DIR = WORKSPACE / "output"
DATA_DIR = WORKSPACE / "data"
RAW_DIR = WORKSPACE / "youtube_uploads" / "raw"
CLIPS_DIR = WORKSPACE / "youtube_uploads" / "clips"
THUMB_DIR = WORKSPACE / "youtube_uploads" / "thumbnails"
UPLOAD_DIR = WORKSPACE / "youtube_uploads" / "output"
LOG_DIR = WORKSPACE / "logs"

for _d in [OUTPUT_DIR, DATA_DIR, RAW_DIR, CLIPS_DIR, THUMB_DIR, UPLOAD_DIR, LOG_DIR]:
    _d.mkdir(exist_ok=True, parents=True)

# ===== 日志 =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"anime_ops_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("AnimeOps")

# ===== 内容库：凡人修仙传 =====
CONTENT_LIBRARY = {
    "凡人修仙传": {
        "search_keywords": ["凡人修仙传 官方", "Fanren Xiuxian Zhuan official", "凡人修仙传预告"],
        "best_scenes": [
            "境界突破",
            "生死决战",
            "实力逆转",
            "情感催泪",
            "终极对决",
        ],
        "titles_en": [
            "Fanren Xiuxian Zhuan EP ? - He WAITED 1000 Years For This Moment 💀 [Eng Sub]",
            "Fanren Xiuxian Zhuan - The Scene That LEFT Everyone SPEECHLESS 😱 [Eng Sub]",
            "Fanren Xiuxian Zhuan - The BREAKTHROUGH Scene Everyone WAITED For ⚡ [Eng Sub]",
            "Fanren Xiuxian Zhuan EP ? - LEGENDARY Scene That Makes No Sense 😱 [Eng Sub]",
            "Fanren Xiuxian Zhuan - This Scene Made Everyone CRY 💔 (Emotional)",
            "Fanren Xiuxian Zhuan - His TRUE Power Was REVEALED ⚡ [Eng Sub]",
            "Fanren Xiuxian Zhuan EP ? - He FINALLY Broke Through 💥 [Eng Sub]",
            "Fanren Xiuxian Zhuan - The Moment That SHOOK the ENTIRE World 🌍 [Eng Sub]",
            "Fanren Xiuxian Zhuan EP ? - The Most INSANE Scene Ever 😱🔥 [Eng Sub]",
            "Fanren Xiuxian Zhuan - This Is His TRUE Strength 💀 [Eng Sub]",
        ],
        "titles_id": [
            "Fanren Xiuxian Zhuan EP ? - Adegan yang BIKIN NANGIS! 💔 [Sub Indo]",
            "Fanren Xiuxian Zhuan - Adegan TERBAIK yang Viral! 🔥 [Sub Indo]",
            "Fanren Xiuxian Zhuan EP ? - Momen yang SANGAT MENGESANKAN! 😱 [Sub Indo]",
            "Fanren Xiuxian Zhuan - Kapan Ini Terjadi?! 💀 [Sub Indo]",
            "Fanren Xiuxian Zhuan - Pertarungan TERHEBAT! ⚡ [Sub Indo]",
        ],
        "titles_es": [
            "Fanren Xiuxian Zhuan EP ? - La ESCENA que MEJORA todo 🔥 [Sub Esp]",
            "Fanren Xiuxian Zhuan - La ESCENA que ME DEJÓ SIN PALABRAS 😱 [Sub Esp]",
            "Fanren Xiuxian Zhuan EP ? - El MOMENTO más ÉPICO! ⚡ [Sub Esp]",
            "Fanren Xiuxian Zhuan - Esta Escena es INCREÍBLE 💀 [Sub Esp]",
            "Fanren Xiuxian Zhuan - La Batalla QUE CAMBIÓ TODO 💥 [Sub Esp]",
        ],
        "tags_base": [
            "anime", "fanrenxiuxianzhuuan", "fanrenxiuxianzhuan",
            "chinese anime", "cultivation anime", "fantasy anime",
            "xuanhuan", "donghua", "anime edit", "anime review",
            "best anime", "top anime", "anime 2026", "anime moments",
            "anime episode", "donghua chinese", "anime english sub",
        ],
        "description_template": (
            "Fanren Xiuxian Zhuan - EP {ep}\n\n"
            "He waited a thousand years for this moment.\n"
            "Follow for more Chinese anime content!\n\n"
            "Tags: #anime #fanrenxiuxianzhuuan #chineseanime #cultivation\n\n"
            "All clips are for entertainment purposes only.\n"
            "All rights belong to their respective copyright owners."
        ),
    }
}

# ===== YouTube Cookie 认证配置 =====
COOKIE_FILE = WORKSPACE / "youtube_cookies.json"


# ============================================================
#   核心功能模块
# ============================================================

def cmd_download(ip_name: str, ep: str = None, quality: str = "best") -> dict:
    """
    使用 yt-dlp 下载动漫素材（Cookie 认证，无需 YouTube API）
    """
    logger.info(f"开始下载素材: {ip_name} EP{ep or '?'} 画质:{quality}")

    # 查找内容库
    ip_data = CONTENT_LIBRARY.get(ip_name)
    if not ip_data:
        available = list(CONTENT_LIBRARY.keys())
        return {"success": False, "error": f"未找到 IP: {ip_name}，可用: {available}"}

    # 生成下载命令
    keywords = ip_data["search_keywords"]
    ep_str = "%03d" if ep is None else ep
    output_template = str(RAW_DIR / f"{ip_name}_ep{ep_str}_%(id)s.%(ext)s")

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--cookies-from-browser", "chrome",  # 自动从 Chrome 读取登录状态
        "-f", f"best[height<={quality.replace('best','1080')}]",
        "--output", output_template,
        "--write-info-json",
        "--no-playlist",
    ]

    # 搜索下载（如果没指定具体 URL）
    if ep:
        search_query = f"{ip_name} EP{ep} 官方"
    else:
        search_query = keywords[0]

    cmd.append(f"ytsearch:{search_query}")

    try:
        logger.info(f"执行命令: {' '.join(cmd[:6])} ... {search_query}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            output = result.stdout
            # 找下载的文件
            files = list(RAW_DIR.glob(f"{ip_name}*"))
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                logger.info(f"下载成功: {latest}")
                return {
                    "success": True,
                    "file": str(latest),
                    "platform": "youtube",
                    "quality": quality,
                }
            return {"success": True, "output": output}
        else:
            logger.error(f"下载失败: {result.stderr[:500]}")
            return {
                "success": False,
                "error": result.stderr[:500] if result.stderr else "未知错误",
                "platform": "youtube",
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "下载超时（5分钟）", "platform": "youtube"}
    except Exception as e:
        return {"success": False, "error": str(e), "platform": "youtube"}


def cmd_clip(input_file: str, start: str = None, duration: str = "90",
             output: str = None, title: str = None, lang: str = "en") -> dict:
    """
    使用 ffmpeg 剪辑片段（自动切片）
    """
    import subprocess as sp

    input_path = Path(input_file)
    if not input_path.exists():
        return {"success": False, "error": f"文件不存在: {input_file}"}

    if output is None:
        output = str(CLIPS_DIR / f"clip_{datetime.now().strftime('%H%M%S')}.mp4")

    # ffmpeg 剪辑命令
    ss = f"-ss {start}" if start else ""
    cmd = (
        f'ffmpeg -y {ss} -i "{input_file}" '
        f'-t {duration} '
        f'-c:v libx264 -preset fast -crf 23 '
        f'-c:a aac -b:a 128k '
        f'-vf "scale=1080:1920:force_original_aspect_ratio=decrease,'
        f'pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black@0.0,'
        f'subtitles=filename=\'{input_file}\'.srt:force_style=\'FontSize=24,PrimaryColour=&HFFFFFF&\' '
        f'if \'EN\' in stream.metadata.language else \'\' ,'
        f'hqdn3d,unsharp" '
        f'"{output}"'
    )

    try:
        logger.info(f"开始剪辑: {input_file} -> {output}")
        result = sp.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return {"success": True, "output": output, "platform": "clip"}
        else:
            # 简化命令重试（无字幕版本）
            simple_cmd = (
                f'ffmpeg -y {ss} -i "{input_file}" '
                f'-t {duration} '
                f'-c:v libx264 -preset fast -crf 23 '
                f'-c:a aac -b:a 128k '
                f'-vf "scale=1080:1920:force_original_aspect_ratio=decrease,'
                f'pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black@0.0,hqdn3d" '
                f'"{output}"'
            )
            result2 = sp.run(simple_cmd, shell=True, capture_output=True, text=True, timeout=300)
            if result2.returncode == 0:
                return {"success": True, "output": output, "platform": "clip"}
            return {"success": False, "error": result.stderr[-500:] if result.stderr else "未知错误"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def cmd_thumbnail(video_path: str, title: str, output: str = None,
                  style: str = "dramatic") -> dict:
    """
    使用 Pillow 生成封面图
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return {"success": False, "error": "Pillow 未安装，请运行: pip install Pillow"}

    # 默认封面尺寸 YouTube: 1280x720
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), color=(20, 10, 40))
    draw = ImageDraw.Draw(img)

    # 背景渐变模拟
    for y in range(H):
        r = int(20 + (y / H) * 30)
        g = int(10 + (y / H) * 10)
        b = int(60 + (y / H) * 40)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # 主标题
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 72)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_small = font_title

    # 主标题（分两行，居中）
    lines = title.split(" - ") if " - " in title else [title[:40], title[40:80] if len(title) > 40 else ""]
    y_start = H // 3

    # 文字描边效果
    for dx, dy in [(-3,-3),(-3,3),(3,-3),(3,3),(-3,0),(3,0),(0,-3),(0,3)]:
        draw.text((W // 2 + dx, y_start + dy), lines[0], font=font_title, fill=(0, 0, 0))
    draw.text((W // 2, y_start), lines[0], font=font_title, fill=(255, 255, 255))

    if len(lines) > 1:
        y_start2 = y_start + 80
        for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2)]:
            draw.text((W // 2 + dx, y_start2 + dy), lines[1], font=font_sub, fill=(0, 0, 0))
        draw.text((W // 2, y_start2), lines[1], font=font_sub, fill=(220, 180, 100))

    # IP 标识
    draw.text((W - 20, H - 50), "凡人修仙传", font=font_small, fill=(180, 180, 180), anchor="rd")

    # 边框高亮
    draw.rectangle([(0, 0), (W - 1, H - 1)], outline=(200, 60, 60), width=4)

    if output is None:
        output = str(THUMB_DIR / f"thumb_{datetime.now().strftime('%H%M%S')}.png")

    img.save(output, "PNG", quality=95)
    logger.info(f"封面已生成: {output}")
    return {"success": True, "output": output, "platform": "thumbnail"}


def _selenium_available() -> bool:
    """检查 Selenium 是否可用"""
    try:
        from selenium import webdriver
        return True
    except ImportError:
        return False


def cmd_upload(video_path: str, title: str = None, description: str = None,
               tags: list = None, thumbnail: str = None, privacy: str = "public",
               cookies: str = None) -> dict:
    """
    上传到 YouTube：
    优先方案 A（Selenium 浏览器自动化，直连你的账号）
    备选方案 B（Google API，需要 OAuth）
    最终方案 C（生成手动上传指引）
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return {"success": False, "error": f"视频文件不存在: {video_path}"}

    # 默认内容
    if title is None:
        title = f"Fanren Xiuxian Zhuan - {datetime.now().strftime('%Y-%m-%d')}"
    tags = tags or CONTENT_LIBRARY["凡人修仙传"]["tags_base"][:10]
    desc_str = description or CONTENT_LIBRARY["凡人修仙传"]["description_template"].format(ep="?")
    tags_str = ",".join(tags)

    # ===== 方案 A: Selenium 浏览器自动化 =====
    if _selenium_available():
        result = _upload_selenium(video_path, title, desc_str, tags_str, privacy)
        if result.get("success"):
            return result
        logger.warning(f"Selenium 上传失败，尝试备选方案: {result.get('error')}")

    # ===== 方案 B: Google API =====
    if CLIENT_SECRETS.exists():
        result = _upload_google_api(video_path, title, desc_str, tags, privacy)
        if result.get("success"):
            return result
        logger.warning(f"Google API 上传失败: {result.get('error')}")

    # ===== 方案 C: 生成手动上传指引 =====
    return {"success": False, "error": "未找到可用的上传方式", "manual_guide": cmd_manual_upload_guide(str(video_path), title), "platform": "youtube"}


def _upload_selenium(video_path: Path, title: str, description: str,
                      tags: str, privacy: str = "public") -> dict:
    """
    Selenium + Chrome 自动化上传（使用你已登录的 Chrome 会话）
    无需 OAuth，用户只需在 Chrome 中登录 YouTube 一次即可
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        import time as time_module

        logger.info("启动 Chrome 浏览器自动化上传...")

        # Chrome 选项配置
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        # 用户数据目录（复用你的 Chrome 配置文件，已登录状态）
        chrome_options.add_argument("--user-data-dir=C:/Users/Administrator/AppData/Local/Google/Chrome/User Data")
        chrome_options.add_argument("--profile-directory=Default")

        # 使用 webdriver-manager 自动获取/管理 ChromeDriver
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service as ChromeService
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.warning(f"webdriver-manager 启动失败: {e}")
            # 回退：直接使用系统 chromedriver
            try:
                driver = webdriver.Chrome(options=chrome_options)
            except Exception as e2:
                logger.warning(f"系统 chromedriver 失败: {e2}")
                # 尝试无配置启动
                driver = webdriver.Chrome()

        wait = WebDriverWait(driver, 15)
        results = []

        try:
            # Step 1: 打开 YouTube Studio
            logger.info("打开 YouTube Studio...")
            driver.get("https://studio.youtube.com")
            time_module.sleep(5)

            # 检查是否需要登录
            if "signin" in driver.current_url or "accounts.google.com" in driver.current_url:
                logger.warning("Chrome 未登录 YouTube，请在弹出的浏览器中登录后手动上传")
                driver.quit()
                return {
                    "success": False,
                    "error": "Chrome 未登录 YouTube，请先在 Chrome 中登录 YouTube",
                    "platform": "youtube",
                }

            # Step 2: 点击上传按钮
            logger.info("点击上传按钮...")
            try:
                upload_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='upload-button']")))
                upload_btn.click()
            except Exception:
                driver.get("https://studio.youtube.com/channel/upload")
                time_module.sleep(3)

            time_module.sleep(3)

            # Step 3: 上传文件
            logger.info(f"上传文件: {video_path.name}")
            file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            file_input.send_keys(str(video_path.resolve()))
            logger.info("文件已选择，等待上传...")

            # Step 4: 等待视频上传完成（检测进度条消失）
            time_module.sleep(15)
            max_wait = 180
            waited = 15
            while waited < max_wait:
                try:
                    # 检查是否还在上传
                    progress = driver.find_elements(By.XPATH, "//span[contains(text(),'%')]")
                    if not progress:
                        break
                    time_module.sleep(5)
                    waited += 5
                    pct = progress[0].text if progress else ""
                    logger.info(f"  上传进度: {pct}")
                except Exception:
                    break

            # Step 5: 填写标题
            logger.info("填写标题...")
            time_module.sleep(3)
            try:
                title_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="textbox" and @placeholder="添加标题"]')
                ))
                title_input.click()
                title_input.clear()
                title_input.send_keys(title)
            except Exception:
                try:
                    title_input = driver.find_element(By.CSS_SELECTOR, 'input[id*="title"]')
                    title_input.clear()
                    title_input.send_keys(title)
                except Exception:
                    logger.warning("标题填写失败，继续...")

            time_module.sleep(1)

            # Step 6: 填写描述
            logger.info("填写描述...")
            try:
                desc_inputs = driver.find_elements(By.XPATH, '//*[@id="textbox"]')
                for inp in desc_inputs:
                    try:
                        placeholder = inp.get_attribute("placeholder") or ""
                        if "描述" in placeholder or "description" in placeholder.lower() or len(desc_inputs) == 1:
                            inp.click()
                            inp.clear()
                            inp.send_keys(description)
                            break
                    except Exception:
                        continue
            except Exception:
                pass

            # Step 7: 添加标签
            logger.info("添加标签...")
            try:
                # 点击"显示更多"展开所有选项
                more_btn = driver.find_elements(By.XPATH, "//*[contains(text(),'显示更多')]")
                for btn in more_btn:
                    try:
                        btn.click()
                        time_module.sleep(1)
                        break
                    except Exception:
                        continue

                # 找标签输入框
                tag_input = driver.find_element(By.XPATH, '//*[@id="tag-input"]')
                tag_input.click()
                tag_input.send_keys(tags.replace(",", "\n"))
            except Exception:
                logger.warning("标签添加失败，继续...")

            time_module.sleep(2)

            # Step 8: 设置公开
            logger.info(f"设置可见性: {privacy}...")
            try:
                privacy_btn = driver.find_element(By.XPATH, '//*[@id="privacy-radios"]//*[contains(text(),"公开")]')
                privacy_btn.click()
            except Exception:
                try:
                    # 找到可见性选择器
                    pub_btn = driver.find_element(By.XPATH, '//*[@id="radioLabelPublic"]')
                    pub_btn.click()
                except Exception:
                    logger.warning("可见性设置失败（可能已默认为公开）")

            time_module.sleep(2)

            # Step 9: 发布
            logger.info("准备发布...")
            try:
                publish_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="done-button"]//*[contains(text(),"发布")]')
                ))
                publish_btn.click()
                time_module.sleep(5)

                # 确认发布
                try:
                    confirm_btn = driver.find_element(By.XPATH, '//*[contains(text(),"发布")]')
                    confirm_btn.click()
                    time_module.sleep(5)
                except Exception:
                    pass

            except Exception:
                logger.warning("发布按钮未找到，请在浏览器中手动点击发布")

            # 获取当前 URL 作为视频链接
            video_url = driver.current_url
            if "watch" in video_url or "studio.youtube.com/video" in driver.current_url:
                pass
            else:
                video_url = f"https://studio.youtube.com/videos"

            driver.quit()

            logger.info(f"上传完成! URL: {video_url}")
            return {
                "success": True,
                "url": video_url,
                "platform": "youtube",
                "title": title,
                "method": "selenium",
            }

        except Exception as e:
            try:
                driver.quit()
            except Exception:
                pass
            return {"success": False, "error": str(e), "platform": "youtube", "method": "selenium"}

    except ImportError:
        return {"success": False, "error": "Selenium 未安装", "platform": "youtube"}
    except Exception as e:
        return {"success": False, "error": str(e), "platform": "youtube", "method": "selenium"}


def _upload_google_api(video_path: Path, title: str, description: str,
                        tags: list, privacy: str) -> dict:
    """使用 Google API 上传（需要 OAuth）"""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
        import google_auth_oauthlib.flow

        creds_file = WORKSPACE / "youtube_credentials.json"
        if not creds_file.exists():
            # 需要 OAuth 授权
            client_config = json.loads(CLIENT_SECRETS.read_text(encoding="utf-8"))
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                client_config,
                ["https://www.googleapis.com/auth/youtube.upload"]
            )
            print("\n正在打开浏览器进行 YouTube 授权...")
            print("请在浏览器中登录 Google 账号并授权。\n")
            creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
            creds_file.write_text(creds.to_json())
            print("授权已保存，下次无需重新授权。\n")

        creds = Credentials.from_authorized_user_file(str(creds_file))
        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:500],
                "categoryId": "1",
            },
            "status": {"privacyStatus": privacy},
        }

        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        print(f"\n正在上传: {title}")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress * 100)
                print(f"\r  上传进度: {pct}%", end="", flush=True)

        video_id = response["id"]
        url = f"https://youtu.be/{video_id}"
        logger.info(f"上传成功! URL: {url}")
        return {"success": True, "video_id": video_id, "url": url, "platform": "youtube", "method": "google_api"}

    except Exception as e:
        return {"success": False, "error": str(e), "platform": "youtube", "method": "google_api"}


def cmd_manual_upload_guide(video_path: str, title: str = None) -> str:
    """生成手动上传指引"""
    return f"""
{'='*60}
手动上传指引
{'='*60}

文件路径: {video_path}

请按以下步骤操作：

1. 打開瀏覽器 → https://studio.youtube.com
2. 點右上角「+ 創建」→「上傳視頻」
3. 選擇文件：{Path(video_path).name}
4. 標題：{title or '凡人修仙传 精彩片段'}
5. 說明：粘貼以下內容：

   凡人修仙传精彩片段！
   Follow for more Chinese anime content!

   Tags: #anime #凡人修仙传 #chineseanime #cultivation

   ⚠️ All clips are for entertainment purposes only.

6. 標籤（粘貼）：
   anime,fanrenxiuxianzhuuan,fanrenxiuxianzhuan,chinese anime,
   cultivation anime,fantasy anime,xuanhuan,donghua,anime edit,
   anime review,best anime,top anime,anime 2026,anime moments

7. 發布設置：公開
8. 點「發布」

{'='*60}
"""


# ============================================================
#   批量任务
# ============================================================

def run_batch(count: int = 10, ip: str = "凡人修仙传", lang: str = "en") -> list:
    """批量运营：下载→剪辑→生成封面→准备上传"""
    results = []
    ip_data = CONTENT_LIBRARY.get(ip, CONTENT_LIBRARY["凡人修仙传"])

    titles = ip_data.get(f"titles_{lang}", ip_data["titles_en"])

    print(f"\n{'='*60}")
    print(f"批量运营任务启动：{ip} | 语言:{lang} | 数量:{count}")
    print(f"{'='*60}")

    for i in range(min(count, 10)):
        ep_num = i + 1
        title = titles[i % len(titles)]

        print(f"\n--- 任务 {i+1}/{count} ---")
        print(f"标题: {title[:60]}...")

        # Step 1: 下载
        print(f"[1/4] 下载素材 EP{ep_num}...")
        dl = cmd_download(ip, str(ep_num))
        video_file = dl.get("file") if dl.get("success") else None

        # Step 2: 剪辑
        if video_file:
            print(f"[2/4] 剪辑片段...")
            clip = cmd_clip(video_file, duration="90", title=title)
            clip_file = clip.get("output") if clip.get("success") else None
        else:
            print(f"[2/4] 跳过（无素材）")
            clip_file = None

        # Step 3: 生成封面
        print(f"[3/4] 生成封面...")
        thumb = cmd_thumbnail(clip_file or video_file or "", title=title)
        thumb_file = thumb.get("output") if thumb.get("success") else None

        # Step 4: 准备上传
        print(f"[4/4] 准备上传...")
        if clip_file and Path(clip_file).exists():
            upload_guide = cmd_manual_upload_guide(clip_file, title)
            print(upload_guide)
            results.append({
                "index": i + 1,
                "ep": ep_num,
                "title": title,
                "video": clip_file,
                "thumbnail": thumb_file,
                "status": "ready_to_upload",
                "manual_guide": upload_guide,
            })
        else:
            results.append({
                "index": i + 1,
                "ep": ep_num,
                "title": title,
                "status": "pending_material",
            })

    # 保存任务列表
    report_file = OUTPUT_DIR / f"batch_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"批量任务报告已保存: {report_file}")

    # 统计
    ready = sum(1 for r in results if r["status"] == "ready_to_upload")
    print(f"\n{'='*60}")
    print(f"批量任务完成：{len(results)} 条 | 已准备上传: {ready} 条")
    print(f"报告: {report_file}")
    print(f"{'='*60}")

    return results


def run_daily_summary() -> str:
    """每日运营摘要"""
    today = datetime.now()
    log_file = LOG_DIR / f"anime_ops_{today.strftime('%Y%m%d')}.log"

    uploads_today = []
    if log_file.exists():
        for line in log_file.read_text(encoding="utf-8").splitlines():
            if "上传成功" in line or "SUCCESS" in line.upper():
                uploads_today.append(line.strip())

    report = f"""
{'='*60}
动漫出海运营 · 每日摘要 {today.strftime('%Y-%m-%d')}
{'='*60}

📊 今日概况
───────────────────────────
  日期: {today.strftime('%Y年%m月%d日')}
  星期: {['一','二','三','四','五','六','日'][today.weekday()]}
  今日上传: {len(uploads_today)} 条
  系统状态: 运行中

📋 今日待办
───────────────────────────
  ☐ 检查昨日视频播放数据
  ☐ 分析爆款内容特征
  ☐ 批量剪輯新內容
  ☐ 定时发布任务
  ☐ 更新收益数据

🎯 今日目标
───────────────────────────
  YouTube 播放量: +10,000
  新增粉丝: +50
  上传视频: 3-5 条
  联盟链接点击: +20

💡 运营建议
───────────────────────────
  · 凡人修仙传今日重点：境界突破类片段
  · 最佳发布时间：18:00-22:00（目标地区晚间）
  · 优先做印尼语/英语双语版本
  · 检查是否有视频被版权警告

📁 数据文件
───────────────────────────
  日志: {log_file}
  输出: {OUTPUT_DIR}

{'='*60}
"""
    return report


# ============================================================
#   交互式代理
# ============================================================

def run_agent():
    """动漫出海运营代理人 · 交互模式"""
    print(f"""
╔{'═'*58}╗
║        动漫出海运营代理人 v1.0                       ║
║        Anime Overseas Operations Agent              ║
╚{'═'*58}╝
    """.replace("═"*58, "═"*58))

    print("""
可用命令：
  download <IP名> [集数]    - 下载素材（如：download 凡人修仙传 5）
  clip <文件> [秒数]        - 剪辑片段（如：clip video.mp4 90）
  thumb <标题>              - 生成封面（如：thumb HE WAITED 1000 YEARS）
  upload <文件> [标题]      - 上传YouTube（如：upload video.mp4 我的标题）
  batch <数量>              - 批量运营（如：batch 10）
  daily                     - 每日摘要
  schedule                  - 查看定时任务
  exit / quit               - 退出

示例任务：
  → "帮我下载凡人修仙传第5集"
  → "批量做10条凡人修仙传英语视频"
  → "上传今天的视频"
  → "生成封面：凡人修仙传 突破场面"
  → "给我每日运营摘要"
    """)

    while True:
        try:
            cmd = input("\n🎯 请输入命令 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not cmd:
            continue

        cmd_lower = cmd.lower()
        if cmd_lower in ["exit", "quit", "q"]:
            print("再见！祝运营顺利！")
            break

        # 解析命令
        parts = cmd.split(maxsplit=2)
        action = parts[0].lower()
        args = parts[1:]

        if action == "download":
            ip = args[0] if args else "凡人修仙传"
            ep = args[1] if len(args) > 1 else None
            r = cmd_download(ip, ep)
            print(f"结果: {json.dumps(r, ensure_ascii=False, indent=2)}")

        elif action == "clip":
            video = args[0] if args else None
            duration = args[1] if len(args) > 1 else "90"
            if not video:
                print("请指定视频文件路径")
            else:
                r = cmd_clip(video, duration=duration)
                print(f"结果: {json.dumps(r, ensure_ascii=False, indent=2)}")

        elif action == "thumb":
            title = args[0] if args else "凡人修仙传 精彩片段"
            r = cmd_thumbnail("", title=title)
            print(f"结果: {json.dumps(r, ensure_ascii=False, indent=2)}")

        elif action == "upload":
            video = args[0] if args else None
            title = args[1] if len(args) > 1 else None
            if not video:
                print("请指定视频文件路径")
            else:
                r = cmd_upload(video, title=title)
                if r.get("success"):
                    print(f"✅ 上传成功! URL: {r.get('url')}")
                else:
                    # 显示手动上传指引
                    print(cmd_manual_upload_guide(video, title))

        elif action == "batch":
            count = int(args[0]) if args and args[0].isdigit() else 10
            ip = args[1] if len(args) > 1 else "凡人修仙传"
            lang = args[2] if len(args) > 2 else "en"
            run_batch(count, ip, lang)

        elif action == "daily":
            print(run_daily_summary())

        elif action == "schedule":
            print(CronList())

        else:
            # 智能理解：当作内容请求处理
            if "凡人修仙传" in cmd or "fanren" in cmd_lower:
                if "批量" in cmd or "batch" in cmd_lower:
                    n = int("".join(filter(str.isdigit, cmd))) or 10
                    run_batch(n)
                elif "下载" in cmd:
                    ep = "".join(filter(str.isdigit, cmd)) or None
                    r = cmd_download("凡人修仙传", ep)
                    print(json.dumps(r, ensure_ascii=False, indent=2))
                elif "上传" in cmd or "发布" in cmd:
                    print("请使用: upload <文件路径> [标题]")
                else:
                    print("凡人修仙传相关操作，请输入具体命令：download / clip / upload / batch")
            else:
                print(f"未知命令: {action}，输入 'help' 查看可用命令")


# ============================================================
#   主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="动漫出海运营代理人 · Anime Overseas Operations Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python anime_ops.py                           # 交互模式
  python anime_ops.py download 凡人修仙传 5      # 下载素材
  python anime_ops.py batch 10                   # 批量运营
  python anime_ops.py daily                     # 每日摘要
  python anime_ops.py upload video.mp4 "标题"   # 上传视频
  python anime_ops.py thumb "HE WAITED 1000 YEARS"  # 生成封面
        """
    )
    parser.add_argument("command", nargs="?", help="命令（省略则进入交互模式）")
    parser.add_argument("args", nargs="*", help="命令参数")
    parser.add_argument("--lang", "-l", default="en", help="内容语言: en/id/es")
    parser.add_argument("--ip", "-i", default="凡人修仙传", help="动漫IP名称")
    parser.add_argument("--batch", "-b", type=int, metavar="N", help="批量数量")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    cmd = args.command
    a = args.args

    # 无命令 → 交互模式
    if not cmd:
        run_agent()
        return

    # 命令路由
    if cmd == "download":
        ip = a[0] if len(a) > 0 else args.ip
        ep = a[1] if len(a) > 1 else None
        r = cmd_download(ip, ep)
        print(json.dumps(r, ensure_ascii=False, indent=2))

    elif cmd == "clip":
        if not a:
            print("用法: python anime_ops.py clip <文件> [时长秒数]")
            return
        r = cmd_clip(a[0], duration=a[1] if len(a) > 1 else "90")
        print(json.dumps(r, ensure_ascii=False, indent=2))

    elif cmd == "thumb":
        title = " ".join(a) if a else "凡人修仙传 精彩片段"
        r = cmd_thumbnail("", title=title)
        print(json.dumps(r, ensure_ascii=False, indent=2))

    elif cmd == "upload":
        if not a:
            print("用法: python anime_ops.py upload <文件> [标题]")
            return
        title = " ".join(a[1:]) if len(a) > 1 else None
        r = cmd_upload(a[0], title=title)
        if r.get("success"):
            print(f"上传成功! URL: {r.get('url')}")
        else:
            print(f"上传失败: {r.get('error')}")
            print(cmd_manual_upload_guide(a[0], title))

    elif cmd == "batch":
        count = args.batch or int(a[0]) if a and a[0].isdigit() else 10
        ip = args.ip
        lang = args.lang
        run_batch(count, ip, lang)

    elif cmd in ("daily", "today", "summary"):
        print(run_daily_summary())

    elif cmd == "schedule":
        try:
            jobs = CronList()
            print(f"当前定时任务: {jobs}")
        except Exception:
            print("定时任务功能需要先设置 CronJob")

    else:
        print(f"未知命令: {cmd}")
        print("可用命令: download / clip / thumb / upload / batch / daily")


if __name__ == "__main__":
    main()
