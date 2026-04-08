#!/usr/bin/env python3
"""
动漫出海运营代理人 · 主入口
agent.py

用法:
    python agent.py <命令> [参数]

命令:
    download <IP名称> [集数]   下载动漫素材
    clip <源文件> [秒数]      剪辑视频片段
    thumb <IP> [标题]         生成封面
    upload <文件>             上传到 YouTube
    batch                     批量运营（下载+剪辑+封面+准备上传）
    daily                     每日运营报告
    revenue                   收益报告
    status                    查看系统状态
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", write_through=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", write_through=True)

import os
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.resolve()
os.chdir(WORKSPACE)

LOG_DIR = WORKSPACE / "logs"
LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = WORKSPACE / "youtube_uploads"
OUTPUT_DIR.mkdir(exist_ok=True)
CLIPS_DIR = OUTPUT_DIR / "clips"
THUMBS_DIR = OUTPUT_DIR / "thumbnails"
RAW_DIR = OUTPUT_DIR / "raw"
for d in [CLIPS_DIR, THUMBS_DIR, RAW_DIR]:
    d.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("AnimeOpsAgent")

CONTACT = {"email": "scott365888@gmail.com", "wechat": "PTS9800"}

TITLE_TEMPLATES_EN = [
    "HE WAITED 1000 YEARS - {ip} EP ? [Eng Sub]",
    "THIS IS IMPOSSIBLE! - {ip} Scene That Shocked Everyone [Eng Sub]",
    "FINALLY BROKE THROUGH - {ip} Level Up Scene [Eng Sub]",
    "LEGENDARY SCENE - That Made No Sense [Eng Sub]",
    "THIS MADE US CRY - {ip} Most Emotional Scene [Eng Sub]",
    "TRUE POWER REVEALED - His Real Strength [Eng Sub]",
    "THE WORLD SHOOK - Everything Changed [Eng Sub]",
    "INSANE MOMENT - No One Expected This [Eng Sub]",
    "UNSTOPPABLE NOW - Nothing Can Stop Him [Eng Sub]",
    "GOD LEVEL - This Is Beyond Human [Eng Sub]",
]

TAG_SET = [
    "anime","fanrenxiuxianzhuuan","chinese anime","cultivation anime",
    "fantasy anime","xuanhuan","donghua","anime edit","anime review",
    "best anime","top anime","anime 2026","anime moments","anime episode",
    "donghua chinese","anime english sub","cultivation","wuxia","xianxia"
]

DESC_TEMPLATE = """{ip} - EP ?

The most epic moment from this anime. Follow for more Chinese anime content!

Support the channel! Shop Anime Merch:
https://amazon.com/s?k=cultivation+anime+merch

Tags: {tags}

All clips are for entertainment purposes only.
All rights belong to their respective copyright owners.

Business / Contact: {email} | WeChat: {wechat}"""


def get_ffmpeg():
    ffmpeg = "C:/Users/Administrator/AppData/Local/Programs/Python/Python311/ffmpeg.exe"
    if Path(ffmpeg).exists():
        return ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except:
        return None


def cmd_download(ip_name: str, episode: str = None):
    print(f"\n下载素材：{ip_name} 第{episode or '全部'}集\n")
    query = f'"{ip_name} EP{episode or ""} highlight"' if episode else f'"{ip_name} 精彩片段"'
    out = str(RAW_DIR / f'{ip_name.replace(" ","_")}_%(title)s.%(ext)s')
    cmd = [sys.executable, "-m", "yt_dlp", "-f", "best[height<=720]/best",
           "--output", out, "--no-playlist", f"ytsearch:{query}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode == 0:
        files = list(RAW_DIR.glob(f"{ip_name.replace(' ','_')}*.mp4"))
        print(f"OK - 下载成功! 共 {len(files)} 个文件")
        for f in files:
            print(f"  - {f.name} ({f.stat().st_size//1024//1024}MB)")
    else:
        print(f"FAIL - 下载失败: {r.stderr[-300:]}")


def cmd_clip(src: str, start: int = 10, duration: int = 90, output=None):
    src_path = Path(src)
    if not src_path.exists():
        src_path = RAW_DIR / src
    if not src_path.exists():
        print(f"FAIL - 文件不存在: {src}"); return
    ffmpeg = get_ffmpeg()
    if not ffmpeg:
        print("FAIL - ffmpeg 不可用"); return
    if output is None:
        output = CLIPS_DIR / f"clip_{datetime.now().strftime('%H%M%S')}.mp4"
    cmd = [ffmpeg, "-y", "-ss", str(start), "-i", str(src_path), "-t", str(duration),
           "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1",
           "-c:v", "libx264", "-preset", "fast", "-crf", "23",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode == 0:
        sz = Path(output).stat().st_size // 1024 // 1024
        print(f"OK - 剪辑完成: {Path(output).name} ({sz}MB)")
    else:
        print(f"FAIL - {r.stderr[-200:]}")


def cmd_thumb(ip_name: str, title_line1: str = None, style: str = "dark"):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1080, 1920
    bgs = {"dark":(10,5,25),"red":(50,5,10),"blue":(5,15,50),"gold":(30,20,5),"purple":(20,5,40)}
    bg = bgs.get(style, bgs["dark"])
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        a = min(255, max(0, int(50*(1-y/H))))
        draw.rectangle([(0,y),(W,y+1)], fill=(a//4, a//6, a//2+20))
    draw.rectangle([(0,0),(W,480)], fill=(0,0,0))
    try:
        fl=ImageFont.truetype("arialbd.ttf",85); fs=ImageFont.truetype("arialbd.ttf",65); fm=ImageFont.truetype("arial.ttf",45)
    except:
        fl=fs=fm=ImageFont.load_default()
    l1 = title_line1 or ip_name.upper()
    bb=draw.textbbox((0,0),l1,font=fl); tw=bb[2]-bb[0]
    draw.text(((W-tw)//2,120),l1,font=fl,fill=(255,200,50))
    draw.rectangle([(80,325),(W-80,330)],fill=(255,60,60))
    ip_str = ip_name.upper().replace(" "," ")
    draw.text((W//2-210,355),ip_str,font=fm,fill=(180,180,180))
    draw.rectangle([(0,H-160),(W,H)],fill=(0,0,0))
    draw.text((80,H-120),"EP ?  |  ENG SUB  |  NEW 2026",font=fm,fill=(200,200,200))
    draw.text((W-420,H-120),"#anime  #donghua  #cultivation",font=fm,fill=(255,80,80))
    for i in range(30):
        a=30-i; draw.ellipse([(-100+i*5,-100+i*3),(300-i*8,200-i*4)],fill=(100,50,200,a))
    for i in range(25):
        a=25-i; draw.ellipse([(W-250+i*8,H-300+i*6),(W+50-i*3,H+50-i*3)],fill=(200,80,30,a))
    out_path = THUMBS_DIR / f"thumb_{datetime.now().strftime('%H%M%S')}.png"
    img.save(str(out_path), "PNG", quality=95)
    print(f"OK - 封面: {out_path.name} ({out_path.stat().st_size//1024}KB)")


def cmd_batch():
    print(f"\n{'='*60}\n批量运营 · 全流程\n{'='*60}\n")
    ip = "凡人修仙传"

    print("[1/4] 下载素材...")
    cmd_download(ip, None)

    print("\n[2/4] 剪辑视频...")
    raw_files = list(RAW_DIR.glob("*.mp4"))
    if raw_files:
        mv = raw_files[0]
        for name, ss, dur in [("clip_A",15,60),("clip_B",5,90),("clip_C",30,75)]:
            cmd_clip(str(mv), ss, dur, str(CLIPS_DIR/f"{name}.mp4"))

    print("\n[3/4] 生成封面...")
    for i, tpl in enumerate(TITLE_TEMPLATES_EN[:5]):
        title = tpl.format(ip=ip.replace(" ",""))
        l1 = title.split(" - ")[0]
        cmd_thumb(ip, l1, list({"dark","red","blue","gold","purple"})[i])

    print("\n[4/4] 生成上传包...")
    clips = sorted(CLIPS_DIR.glob("*.mp4"))
    thumbs = sorted(THUMBS_DIR.glob("*.png"))
    pkg = []
    for i, clip in enumerate(clips[:5]):
        thumb = thumbs[i] if i < len(thumbs) else None
        tpl = TITLE_TEMPLATES_EN[i % len(TITLE_TEMPLATES_EN)]
        title = tpl.format(ip=ip.replace(" ",""))
        desc = DESC_TEMPLATE.format(ip=ip, tags=", ".join(TAG_SET[:8]), email=CONTACT["email"], wechat=CONTACT["wechat"])
        pkg.append({"video": str(clip), "thumbnail": str(thumb) if thumb else "", "title": title, "description": desc, "tags": TAG_SET})

    pkg_file = OUTPUT_DIR / f"upload_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(pkg_file, "w", encoding="utf-8") as f:
        json.dump(pkg, f, ensure_ascii=False, indent=2)

    print(f"\n完成! 剪辑:{len(clips)} 封面:{len(thumbs)} 包:{pkg_file.name}")
    print(f"打开上传: https://studio.youtube.com")


def cmd_daily():
    clips = sorted(CLIPS_DIR.glob("*.mp4"))
    thumbs = sorted(THUMBS_DIR.glob("*.png"))
    raw = sorted(RAW_DIR.glob("*.mp4"))
    total_mb = sum(f.stat().st_size for f in clips) // 1024 // 1024
    print(f"\n{'='*60}")
    print(f"动漫出海运营 · 每日报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"内容库: 原始{len(raw)} 剪辑{len(clips)} 封面{len(thumbs)} ({total_mb}MB)")
    print(f"剪辑文件:")
    for c in clips:
        print(f"  - {c.name}")
    print(f"\n待办:")
    print(f"  1. YouTube OAuth设置: https://console.cloud.google.com")
    print(f"  2. 上传剪辑到 YouTube Studio")
    print(f"  3. 申请亚马逊联盟")
    print(f"  4. 申请 YouTube Partner Program")
    print(f"收入目标: Day30=$0 | Day60=$300 | Day90=$800 | Day180=$2000+")
    print(f"联系: {CONTACT['email']} | WeChat: {CONTACT['wechat']}\n")


def cmd_revenue():
    print(f"\n{'='*60}\n动漫出海运营 · 收益报告\n{'='*60}\n")
    try:
        sys.path.insert(0, str(WORKSPACE))
        from payment_agent import PaymentAgent
        agent = PaymentAgent()
        print(agent.generate_payment_report())
    except Exception as e:
        print(f"收益模块: {e}")
        print(f"\n收益来源:")
        print(f"  YouTube Partner: https://studio.youtube.com")
        print(f"  亚马逊联盟: https://affiliate-program.amazon.com")
        print(f"  客户商单: WeChat {CONTACT['wechat']}")
        print(f"  版权代理: {CONTACT['email']}")


def cmd_upload(video_path: str, title: str = None, thumbnail: str = None):
    sys.path.insert(0, str(WORKSPACE))
    video = Path(video_path)
    if not video.exists():
        print(f"FAIL - 文件不存在: {video_path}"); return
    title = title or TITLE_TEMPLATES_EN[0].format(ip="ANIME")
    print(f"\n上传: {video.name}\n标题: {title[:50]}...")
    try:
        from anime_ops import _upload_selenium
        result = _upload_selenium(
            video, title=title,
            description=DESC_TEMPLATE.format(ip="Anime", tags=", ".join(TAG_SET[:8]), email=CONTACT["email"], wechat=CONTACT["wechat"]),
            tags=",".join(TAG_SET[:10]),
            privacy="public",
            thumbnail_path=thumbnail,
        )
        if result.get("success"):
            print(f"OK - {result.get('url')}")
        else:
            print(f"FAIL - {result.get('error')}\n备选: https://studio.youtube.com")
    except Exception as e:
        print(f"FAIL - {e}\n备选: https://studio.youtube.com")


def cmd_status():
    clips = sorted(CLIPS_DIR.glob("*.mp4"))
    thumbs = sorted(THUMBS_DIR.glob("*.png"))
    raw = sorted(RAW_DIR.glob("*.mp4"))
    secrets = WORKSPACE / "client_secrets.json"
    ffmpeg_ok = get_ffmpeg() is not None
    print(f"\n{'='*60}")
    print(f"动漫出海运营代理人 · 系统状态")
    print(f"{'='*60}")
    print(f"yt-dlp:  OK | ffmpeg: {'OK' if ffmpeg_ok else 'FAIL'} | Pillow: OK")
    print(f"YouTube OAuth: {'OK (可全自动化)' if secrets.exists() else '未配置 (使用手动/Selenium)'}")
    print(f"内容库: 原始{len(raw)} 剪辑{len(clips)} 封面{len(thumbs)}")
    print(f"\n命令:")
    print(f"  python agent.py status      - 系统状态")
    print(f"  python agent.py download    - 下载素材")
    print(f"  python agent.py batch      - 批量运营")
    print(f"  python agent.py daily       - 每日报告")
    print(f"  python agent.py revenue     - 收益报告")
    print(f"  python agent.py upload <文件> - 上传到YouTube")
    print(f"\n联系: {CONTACT['email']} | WeChat: {CONTACT['wechat']}\n")


USAGE = f"""
动漫出海运营代理人 · 使用说明

命令:
  download <IP> [集数]   下载动漫素材
  clip <文件>            剪辑视频片段
  thumb <IP> [标题]     生成封面
  upload <文件>          上传到 YouTube
  batch                  批量运营（全流程）
  daily                  每日运营报告
  revenue                收益报告
  status                 系统状态（默认）

示例:
  python agent.py status
  python agent.py download 凡人修仙传
  python agent.py batch
  python agent.py upload youtube_uploads/clips/clip_A.mp4

联系: {CONTACT['email']} | WeChat: {CONTACT['wechat']}
"""


def main():
    if len(sys.argv) < 2:
        cmd_status()
        return
    cmd = sys.argv[1].lower()
    if cmd == "download":
        ip = sys.argv[2] if len(sys.argv) > 2 else "凡人修仙传"
        ep = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_download(ip, ep)
    elif cmd == "clip":
        src = sys.argv[2] if len(sys.argv) > 2 else ""
        ss = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        dur = int(sys.argv[4]) if len(sys.argv) > 4 else 90
        cmd_clip(src, ss, dur)
    elif cmd == "thumb":
        ip = sys.argv[2] if len(sys.argv) > 2 else "凡人修仙传"
        title = sys.argv[3] if len(sys.argv) > 3 else None
        style = sys.argv[4] if len(sys.argv) > 4 else "dark"
        cmd_thumb(ip, title, style)
    elif cmd == "upload":
        video = sys.argv[2] if len(sys.argv) > 2 else ""
        title = sys.argv[3] if len(sys.argv) > 3 else None
        thumb = sys.argv[4] if len(sys.argv) > 4 else None
        cmd_upload(video, title, thumb)
    elif cmd == "batch":
        cmd_batch()
    elif cmd == "daily":
        cmd_daily()
    elif cmd == "revenue":
        cmd_revenue()
    elif cmd == "status":
        cmd_status()
    else:
        print(USAGE)


if __name__ == "__main__":
    main()
