"""
动漫出海运营代理人 (Anime Ops Agent)
anime_overseas/agent.py

入口点：python agent.py
用法：
    python agent.py                      # 交互模式
    python agent.py download 凡人修仙传    # 下载素材
    python agent.py clip                  # 剪辑视频
    python agent.py thumb                 # 生成封面
    python agent.py upload                # 上传 YouTube
    python agent.py batch                 # 批量全流程
    python agent.py daily                 # 每日报告
    python agent.py revenue               # 收益报告
    python agent.py analytics             # 数据分析
"""

import sys
import io
import os
import json
import subprocess
from pathlib import Path

# UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)

WORKSPACE = Path(__file__).parent
os.chdir(WORKSPACE)

CONTACT = {
    "email": "scott365888@gmail.com",
    "wechat": "PTS9800",
}


def banner():
    print("""
╔══════════════════════════════════════════════════════╗
║        动漫出海运营代理人  Anime Ops Agent v1.0        ║
╠══════════════════════════════════════════════════════╣
║  IP: 凡人修仙传 (Fanren Xiuxian Zhuan)                ║
║  市场: 英语 | 印尼语 | 西班牙语 | 阿拉伯语              ║
║  平台: YouTube Shorts | TikTok | IG Reels             ║
║  收款: scott365888@gmail.com / 微信 PTS9800           ║
╚══════════════════════════════════════════════════════╝
""")


def cmd_download(ip: str = "凡人修仙传"):
    """下载素材"""
    from anime_ops import cmd_download as dl
    result = dl(ip)
    print(f"\n下载结果: {result}")
    return result


def cmd_clip():
    """剪辑视频"""
    from anime_ops import cmd_clip
    result = cmd_clip()
    print(f"\n剪辑结果: {result}")
    return result


def cmd_thumbnail(title: str = ""):
    """生成封面"""
    from anime_ops import cmd_thumbnail
    result = cmd_thumbnail(title)
    print(f"\n封面生成: {result}")
    return result


def cmd_translate(input_file: str = "", source: str = "zh", target: str = "en"):
    """翻译字幕"""
    from translate_automation import SrtTranslator
    translator = SrtTranslator()
    output = str(WORKSPACE / f"youtube_uploads/subtitles/{Path(input_file).stem}_{target}.srt")
    result = translator.translate_file(input_file, output, source, target)
    print(f"\n翻译完成: {result}")
    return result


def cmd_upload(video_path: str = ""):
    """上传 YouTube"""
    from anime_ops import cmd_upload_youtube
    if not video_path:
        clips = list((WORKSPACE / "youtube_uploads/clips").glob("*.mp4"))
        if clips:
            video_path = str(clips[0])
        else:
            print("错误: 没有找到已剪辑的视频")
            print("请先运行: python agent.py clip")
            return {"success": False, "error": "no video"}
    result = cmd_upload_youtube(video_path)
    return result


def cmd_batch():
    """完整批量流程: 下载→剪辑→封面→准备上传"""
    from anime_ops import cmd_download, cmd_clip
    print("\n" + "="*60)
    print("批量全流程开始")
    print("="*60)

    # 步骤1: 下载
    print("\n[1/4] 下载素材...")
    dl_result = cmd_download("凡人修仙传")
    print(f"  {dl_result}")

    # 步骤2: 剪辑
    print("\n[2/4] 剪辑视频...")
    clip_result = cmd_clip()
    print(f"  {clip_result}")

    # 步骤3: 封面
    print("\n[3/4] 生成封面...")
    from anime_ops import cmd_thumbnail
    thumb_result = cmd_thumbnail("Fanren Xiuxian Zhuan - The Moment Everyone WAITED For")
    print(f"  {thumb_result}")

    # 步骤4: 总结
    print("\n[4/4] 生成上传包...")
    clips = list((WORKSPACE / "youtube_uploads/clips").glob("*.mp4"))
    thumbs = list((WORKSPACE / "youtube_uploads/thumbnails").glob("cover_*.png"))
    raw = list((WORKSPACE / "youtube_uploads/raw").glob("*.mp4"))

    print(f"\n{'='*60}")
    print("批量完成! 本次生成:")
    print(f"  原始素材: {len(raw)} 个")
    print(f"  已剪辑片段: {len(clips)} 个")
    print(f"  封面图: {len(thumbs)} 张")
    print()
    print("下一步: python agent.py upload")
    print("        (或手动上传到 YouTube)")
    print(f"{'='*60}")

    return {
        "clips": [str(c) for c in clips],
        "thumbnails": [str(t) for t in thumbs],
    }


def cmd_daily():
    """每日报告"""
    print("\n" + "="*60)
    print("动漫出海运营 · 每日报告")
    print(f"日期: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}")
    print("="*60)

    # 资产
    from payment_agent import PaymentAgent
    agent = PaymentAgent()
    balance = agent.get_balance()
    print(f"\n💰 资产状况")
    print(f"   USD: ${balance['USD']:.2f}")
    print(f"   CNY: ¥{balance['CNY']:.2f}")

    # 文件统计
    raw = list((WORKSPACE / "youtube_uploads/raw").glob("*"))
    clips = list((WORKSPACE / "youtube_uploads/clips").glob("*.mp4"))
    thumbs = list((WORKSPACE / "youtube_uploads/thumbnails").glob("*.png"))
    print(f"\n📦 内容库存")
    print(f"   原始素材: {len(raw)} 个")
    print(f"   已剪辑: {len(clips)} 个")
    print(f"   封面: {len(thumbs)} 张")

    # 待办
    print(f"\n📋 今日待办")
    print(f"   □ 确认 YouTube OAuth 设置完成")
    print(f"   □ 上传第一个视频")
    print(f"   □ 申请亚马逊联盟账号")
    print(f"   □ 设置每日发布计划")
    print(f"   □ 申请 YouTube Partner Program")
    print(f"\n📞 联系方式: {CONTACT['email']} / {CONTACT['wechat']}")


def cmd_revenue():
    """收益报告"""
    from payment_agent import PaymentAgent
    agent = PaymentAgent()
    report = agent.generate_payment_report()
    print(report)
    print(f"\n📞 收款联系: {CONTACT['email']} / 微信 {CONTACT['wechat']}")


def cmd_analytics():
    """数据分析"""
    from analytics_dashboard import AnalyticsDashboard
    dash = AnalyticsDashboard()
    report = dash.generate_daily_report()
    print(report)


def interactive():
    """交互模式"""
    banner()
    print("\n可用命令:")
    print("  download  - 下载素材")
    print("  clip      - 剪辑视频")
    print("  thumb     - 生成封面")
    print("  translate - 翻译字幕")
    print("  upload    - 上传 YouTube")
    print("  batch     - 批量全流程")
    print("  daily     - 每日报告")
    print("  revenue   - 收益报告")
    print("  analytics - 数据分析")
    print("  help      - 显示帮助")
    print("  exit      - 退出")
    print()
    while True:
        try:
            cmd = input("anime-ops> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break
        if not cmd:
            continue
        if cmd in ("exit", "quit", "q"):
            print("再见!")
            break
        elif cmd in ("help", "h", "?"):
            print("\n帮助:")
            print("  输入命令名执行对应功能")
            print("  或直接输入 IP 名称下载素材")
            print("  示例: python agent.py batch")
        elif cmd == "download":
            ip = input("  IP名称 (默认凡人修仙传): ").strip() or "凡人修仙传"
            cmd_download(ip)
        elif cmd == "clip":
            cmd_clip()
        elif cmd == "thumb":
            title = input("  标题 (可选): ").strip()
            cmd_thumbnail(title)
        elif cmd == "translate":
            inp = input("  字幕文件路径: ").strip()
            src = input("  源语言 (默认zh): ").strip() or "zh"
            tgt = input("  目标语言 (默认en): ").strip() or "en"
            if inp:
                cmd_translate(inp, src, tgt)
        elif cmd == "upload":
            path = input("  视频路径 (可选,默认第一个剪辑): ").strip()
            cmd_upload(path)
        elif cmd == "batch":
            cmd_batch()
        elif cmd == "daily":
            cmd_daily()
        elif cmd == "revenue":
            cmd_revenue()
        elif cmd == "analytics":
            cmd_analytics()
        else:
            print(f"未知命令: {cmd}")
            print("输入 help 查看可用命令")


def main():
    args = sys.argv[1:]

    if not args:
        interactive()
        return

    cmd = args[0].lower()

    if cmd == "download":
        ip = args[1] if len(args) > 1 else "凡人修仙传"
        cmd_download(ip)
    elif cmd == "clip":
        cmd_clip()
    elif cmd == "thumb":
        title = args[1] if len(args) > 1 else ""
        cmd_thumbnail(title)
    elif cmd == "translate":
        inp = args[1] if len(args) > 1 else ""
        src = args[2] if len(args) > 2 else "zh"
        tgt = args[3] if len(args) > 3 else "en"
        cmd_translate(inp, src, tgt)
    elif cmd == "upload":
        path = args[1] if len(args) > 1 else ""
        cmd_upload(path)
    elif cmd == "batch":
        cmd_batch()
    elif cmd == "daily":
        cmd_daily()
    elif cmd == "revenue":
        cmd_revenue()
    elif cmd == "analytics":
        cmd_analytics()
    elif cmd in ("help", "-h", "--help"):
        print(__doc__)
    else:
        print(f"未知命令: {cmd}")
        print("用法: python agent.py [download|clip|thumb|upload|batch|daily|revenue|analytics]")
        sys.exit(1)


if __name__ == "__main__":
    main()
