#!/usr/bin/env python3
"""
动漫出海运营代理人 · Skill Agent
anime_overseas/anime-ops-skill/agent.py

这个文件是 Anime Ops Agent 的核心逻辑。
被 skill.json 引用，当用户说 "/anime-ops" 时调用此 Agent。
"""

import sys
import io
import json
import re
from pathlib import Path
from datetime import datetime

# UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

AGENT_DIR = Path(__file__).parent
WORKSPACE = AGENT_DIR.parent
sys.path.insert(0, str(WORKSPACE))

# ===== 内容库 =====
IP_LIB = {
    "凡人修仙传": {
        "en_titles": [
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
        "id_titles": [
            "Fanren Xiuxian Zhuan - Adegan yang BIKIN NANGIS! 💔 [Sub Indo]",
            "Fanren Xiuxian Zhuan - Adegan TERBAIK yang Viral! 🔥 [Sub Indo]",
            "Fanren Xiuxian Zhuan - Momen yang SANGAT MENGESANKAN! 😱 [Sub Indo]",
            "Fanren Xiuxian Zhuan - Kapan Ini Terjadi?! 💀 [Sub Indo]",
            "Fanren Xiuxian Zhuan - Pertarungan TERHEBAT! ⚡ [Sub Indo]",
        ],
        "es_titles": [
            "Fanren Xiuxian Zhuan - La ESCENA que MEJORA todo 🔥 [Sub Esp]",
            "Fanren Xiuxian Zhuan - La ESCENA que ME DEJO SIN PALABRAS 😱 [Sub Esp]",
            "Fanren Xiuxian Zhuan - El MOMENTO mas EPICO! ⚡ [Sub Esp]",
            "Fanren Xiuxian Zhuan - Esta Escena es INCREIBLE 💀 [Sub Esp]",
            "Fanren Xiuxian Zhuan - La Batalla QUE CAMBIO TODO 💥 [Sub Esp]",
        ],
        "tags": [
            "anime", "fanrenxiuxianzhuuan", "fanrenxiuxianzhuan",
            "chinese anime", "cultivation anime", "fantasy anime",
            "xuanhuan", "donghua", "anime edit", "anime review",
            "best anime", "top anime", "anime 2026", "anime moments",
            "anime episode", "donghua chinese", "anime english sub",
        ],
        "description": (
            "Fanren Xiuxian Zhuan - EP ?\n\n"
            "He waited a thousand years for this moment.\n"
            "Follow for more Chinese anime content!\n\n"
            "Tags: #anime #fanrenxiuxianzhuuan #chineseanime #cultivation\n\n"
            "All clips are for entertainment purposes only.\n"
            "All rights belong to their respective copyright owners."
        ),
    }
}

BANNER = """
╔══════════════════════════════════════════════════════════╗
║         动漫出海运营代理人  v1.0                         ║
║         Anime Overseas Operations Agent                  ║
║         凡人修仙传 · 全球分发                            ║
╚══════════════════════════════════════════════════════════╝
"""


def intent_classify(user_input: str) -> str:
    """智能识别用户意图"""
    inp = user_input.lower()
    if any(k in inp for k in ["运营", "op", "operate", "开始", "start"]):
        return "start_ops"
    if any(k in inp for k in ["下载", "download", "down"]):
        return "download"
    if any(k in inp for k in ["上传", "upload", "发布", "post", "pub"]):
        return "upload"
    if any(k in inp for k in ["批量", "batch", "10", "n条", "多条"]):
        return "batch"
    if any(k in inp for k in ["封面", "thumb", "cover", "圖面"]):
        return "thumbnail"
    if any(k in inp for k in ["数据", "analytics", "分析", "stat", "播放"]):
        return "analytics"
    if any(k in inp for k in ["收益", "revenue", "收入", "赚钱", "钱"]):
        return "revenue"
    if any(k in inp for k in ["每日", "daily", "摘要", "summary", "日报"]):
        return "daily"
    if any(k in inp for k in ["帮助", "help", "教", "怎么", "怎么做"]):
        return "help"
    if any(k in inp for k in ["凡人修仙", "fanren"]):
        return "fanren"
    return "general"


def cmd_start_ops(ip: str = "凡人修仙传", lang: str = "en", count: int = 5) -> str:
    """启动运营"""
    from anime_ops import run_batch, cmd_thumbnail, cmd_download, cmd_clip

    ip_data = IP_LIB.get(ip, IP_LIB["凡人修仙传"])
    titles_key = f"{lang}_titles" if f"{lang}_titles" in ip_data else "en_titles"
    titles = ip_data[titles_key]

    result = f"""
{'='*60}
动漫出海运营 · 启动报告
{'='*60}

IP: {ip}
语言: {lang}
目标数量: {count} 条

"""

    for i in range(min(count, 10)):
        title = titles[i % len(titles)]
        result += f"\n[视频 {i+1}] {title[:60]}...\n"
        result += "  状态: 已排入任务队列\n"

    result += f"""
{'='*60}
下一步操作：
{'='*60}

1. 下载素材：
   python anime_ops.py download {ip} 1

2. 批量运营（下载+剪辑+生成封面）：
   python anime_ops.py batch {count}

3. 生成封面：
   python anime_ops.py thumb "凡人修仙传 HE WAITED 1000 YEARS"

4. 上传视频：
   python anime_ops.py upload <视频文件> "<标题>"

5. 查看每日摘要：
   python anime_ops.py daily

{'='*60}
"""
    return result


def cmd_download(ip: str, ep: str = None) -> dict:
    """下载素材"""
    from anime_ops import cmd_download as _dl
    return _dl(ip, ep)


def cmd_upload(video: str, title: str = None, lang: str = "en") -> dict:
    """上传视频"""
    from anime_ops import cmd_upload as _up
    return _up(video, title=title)


def cmd_batch(count: int = 10, ip: str = "凡人修仙传", lang: str = "en") -> list:
    """批量运营"""
    from anime_ops import run_batch as _batch
    return _batch(count, ip, lang)


def cmd_thumbnail(title: str) -> dict:
    """生成封面"""
    from anime_ops import cmd_thumbnail as _thumb
    return _thumb("", title=title)


def cmd_daily() -> str:
    """每日摘要"""
    from anime_ops import run_daily_summary
    return run_daily_summary()


def cmd_revenue() -> str:
    """收益报告"""
    from anime_ops import WORKSPACE
    from payment_agent import PaymentAgent

    agent = PaymentAgent(str(WORKSPACE))
    return agent.generate_payment_report()


def cmd_analytics(platform: str = "youtube") -> str:
    """数据分析"""
    return f"""
{'='*60}
动漫出海运营 · 数据分析报告
{'='*60}
日期: {datetime.now().strftime('%Y-%m-%d')}

📊 YouTube 频道分析
───────────────────
  播放量趋势: 请在 YouTube Studio 查看
  爆款视频: 境界突破类片段表现最佳
  建议: 优先发布 HE WAITED 1000 YEARS 类标题

📊 TikTok 分析
──────────────
  完播率: 目标 >40%
  建议: 前3秒必须有震撼画面

📊 收益预测
──────────
  YouTube CPM: $4-8/千播放
  1000订阅 + 4000观看小时 = 开通创收
  预计达标时间: 持续日更 4-6 周

💡 优化建议
──────────
  1. 发现爆款立即批量复制同类型
  2. 每天分析后台数据，淘汰低效内容
  3. 集中发布时间：18:00-22:00（目标地区晚间）
  4. 每周至少发布 15 条新内容

{'='*60}
"""


def cmd_help() -> str:
    """帮助信息"""
    return f"""
{BANNER}

可用命令：
  download [IP] [集数]    - 下载素材
  upload <文件> [标题]    - 上传 YouTube
  batch [数量]            - 批量运营
  thumb <标题>            - 生成封面
  daily                   - 每日摘要
  analytics               - 数据分析
  revenue                 - 收益报告
  help                    - 显示此帮助

快捷任务示例：
  "帮我下载凡人修仙传第5集"
  "批量做10条凡人修仙传英语视频"
  "上传今天的视频"
  "生成封面：凡人修仙传 突破场面"
  "给我每日运营摘要"
  "分析昨天的数据"
  "查看收益"
  "运营凡人修仙传账号"

当前配置：
  默认IP: 凡人修仙传
  默认语言: 英语(en) / 印尼语(id) / 西班牙语(es)
  目标平台: YouTube Shorts / TikTok / Instagram Reels

文件位置：
  {AGENT_DIR.parent}
"""


# ===== Agent 主入口 =====

def run(prompt: str) -> str:
    """
    Anime Ops Agent 的主入口。
    被 skill.json 的 prompt 调用。
    """
    # Don't print to stdout here - return instead for caller
    intent = intent_classify(prompt)
    ip = "凡人修仙传"
    lang = "en"
    count = 10

    # 提取参数
    for l in ["en", "id", "es", "zh"]:
        if l in prompt.lower():
            lang = l

    for i in range(1, 51):
        if str(i) in prompt:
            count = i

    # 意图路由
    if intent == "start_ops":
        return cmd_start_ops(ip, lang, count)

    elif intent == "download":
        ep = None
        import re
        m = re.search(r"第?\s*(\d+)\s*集", prompt)
        if m:
            ep = m.group(1)
        r = cmd_download(ip, ep)
        return json.dumps(r, ensure_ascii=False, indent=2)

    elif intent == "upload":
        import re
        m = re.search(r"upload\s+(.+?)(?:\s+[\"']|\s+|$)", prompt)
        video = m.group(1).strip() if m else None
        if not video:
            return "请指定视频文件路径，如: upload video.mp4"
        title_match = re.search(r"[\"'](.+?)[\"']", prompt)
        title = title_match.group(1) if title_match else None
        r = cmd_upload(video, title, lang)
        return json.dumps(r, ensure_ascii=False, indent=2)

    elif intent == "batch":
        r = cmd_batch(count, ip, lang)
        return f"批量任务已启动，共 {len(r)} 条"

    elif intent == "thumbnail":
        import re
        m = re.search(r"[\"'](.+?)[\"']", prompt)
        title = m.group(1) if m else "凡人修仙传 精彩片段"
        r = cmd_thumbnail(title)
        return json.dumps(r, ensure_ascii=False, indent=2)

    elif intent == "daily":
        return cmd_daily()

    elif intent == "analytics":
        return cmd_analytics()

    elif intent == "revenue":
        return cmd_revenue()

    elif intent == "help":
        return cmd_help()

    else:
        return (
            f"我理解你的请求是：「{prompt}」\n\n"
            f"当前支持的运营操作：\n"
            f"  · 下载素材：download 凡人修仙传 第5集\n"
            f"  · 批量运营：batch 10（做10条视频）\n"
            f"  · 上传视频：upload video.mp4 \"标题\"\n"
            f"  · 生成封面：thumb \"HE WAITED 1000 YEARS\"\n"
            f"  · 每日摘要：daily\n"
            f"  · 数据分析：analytics\n"
            f"  · 收益报告：revenue\n\n"
            f"输入 help 查看所有命令。"
        )


if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not user_input:
        print(cmd_help())
    else:
        print(run(user_input))
