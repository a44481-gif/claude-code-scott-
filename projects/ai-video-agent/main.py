# AI 短视频运营 Agent
# 一站式自动化运营系统：禅心师姐 × 爪爪博士

__version__ = "1.0.0"
__author__ = "AI Video Agent"

from src.content.script_generator import ScriptGenerator
from src.video.digital_human import DigitalHumanCreator
from src.publish.platform_poster import PlatformPoster
from src.analytics.report_generator import ReportGenerator
from src.email.report_sender import ReportSender

class AIVideoAgent:
    """AI 短视频运营主类"""

    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.digital_human = DigitalHumanCreator()
        self.poster = PlatformPoster()
        self.report_gen = ReportGenerator()
        self.email_sender = ReportSender()
        self.stats = {
            "videos_created": 0,
            "videos_published": 0,
            "reports_sent": 0
        }

    def daily_task(self):
        """每日任务：生成脚本 → 制作视频 → 发布"""
        from datetime import datetime
        print(f"\n[{datetime.now()}] === 执行每日任务 ===")

        # 1. 生成今日脚本
        script = self.script_gen.generate_daily_script()
        print(f"✅ 脚本生成完成: {script['title']}")

        # 2. 制作数字人视频（如果配置了API）
        video_path = self.digital_human.create_video(script)
        if video_path:
            print(f"✅ 视频制作完成: {video_path}")
            self.stats["videos_created"] += 1

            # 3. 发布到平台（如果配置了API）
            results = self.poster.publish_video(video_path, script)
            if results:
                print(f"✅ 多平台发布完成")
                self.stats["videos_published"] += len(results)
        else:
            print("⏳ 数字人视频待配置API后自动生成")
            print(f"📝 脚本已生成，可手动制作视频")
            # 保存脚本供后续使用
            self.script_gen.save_script(script)

        return script

    def weekly_task(self):
        """每周任务：生成报告 → 发送邮件"""
        from datetime import datetime
        print(f"\n[{datetime.now()}] === 执行每周任务 ===")

        # 1. 收集数据
        data = self.report_gen.collect_weekly_data()

        # 2. 生成报告
        report_html = self.report_gen.generate_html_report(data)
        self.report_gen.save_report(report_html)
        print(f"✅ 周报已生成")

        # 3. 发送邮件
        if self.email_sender.send_report(report_html):
            self.stats["reports_sent"] += 1
            print(f"✅ 周报已发送至 h13751019800@163.com")
        else:
            print(f"❌ 邮件发送失败，请检查配置")

        return data

    def run(self, mode="daemon"):
        """启动定时任务"""
        import schedule, time
        from datetime import datetime

        print("=" * 50)
        print("🎬 AI 短视频运营 Agent 已启动")
        print(f"⏰ 启动时间: {datetime.now()}")
        print("=" * 50)
        print("\n📋 功能模块:")
        print("   1. 禅心师姐 - 佛学/正能量赛道")
        print("   2. 爪爪博士 - 宠物赛道")
        print("\n📧 报告发送至: h13751019800@163.com")
        print("\n💡 使用说明:")
        print("   python main.py --daily    # 执行每日任务")
        print("   python main.py --weekly   # 执行周报任务")
        print("   python main.py --daemon   # 启动定时守护进程")
        print("=" * 50)

        if mode == "daemon":
            # 设置定时任务
            schedule.every().day.at("06:00").do(self.daily_task)
            schedule.every().monday.at("09:00").do(self.weekly_task)

            print("\n🔄 定时任务已设置:")
            print("   • 每日 06:00 - 生成并发布视频")
            print("   • 每周一 09:00 - 生成报告并发送邮件")
            print("\n按 Ctrl+C 停止...\n")

            while True:
                schedule.run_pending()
                time.sleep(60)
        elif mode == "daily":
            self.daily_task()
        elif mode == "weekly":
            self.weekly_task()

        return self.stats


if __name__ == "__main__":
    import sys

    mode = "daemon"
    if len(sys.argv) > 1:
        mode = sys.argv[1].replace("--", "")

    agent = AIVideoAgent()
    agent.run(mode)
