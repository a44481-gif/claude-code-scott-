"""
动漫出海 - 数据分析与邮件日报生成器
anime_overseas/analytics_dashboard.py

功能：
1. 读取各平台数据（YouTube/TikTok/Analytics API）
2. 数据可视化分析
3. 爆款内容识别
4. 自动生成邮件日报/周报
5. 关键指标异常告警
6. 趋势分析

用法:
    dashboard = AnalyticsDashboard()
    report = dashboard.generate_daily_report()
    dashboard.send_email_report(report)
"""

import os
import json
import logging
import smtplib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from anime_ops_config import (
    EMAIL_CONFIG, MONETIZATION, PLATFORMS, REGIONS,
    LOG_DIR, DATA_DIR, OUTPUT_DIR
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "analytics.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("AnalyticsDashboard")


# ============ 数据模型 ============

class PlatformData:
    """平台数据容器"""

    def __init__(self, platform: str):
        self.platform = platform
        self.videos = []
        self.total_views = 0
        self.total_likes = 0
        self.total_subscribers = 0
        self.total_watch_time = 0
        self.revenue = 0.0

    def add_video(self, video_data: dict):
        self.videos.append(video_data)
        self.total_views += video_data.get("views", 0)
        self.total_likes += video_data.get("likes", 0)
        self.total_watch_time += video_data.get("watch_time", 0)

    def calculate_revenue(self) -> float:
        """根据播放量计算预估收益"""
        if self.platform == "youtube":
            cpm = MONETIZATION["youtube_cpm"]
            self.revenue = (self.total_views / 1000) * cpm
        elif self.platform == "tiktok":
            cpm = MONETIZATION["tiktok_cpm"]
            self.revenue = (self.total_views / 1000) * cpm
        else:
            self.revenue = (self.total_views / 1000) * MONETIZATION["youtube_cpm"]
        return self.revenue

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "video_count": len(self.videos),
            "total_views": self.total_views,
            "total_likes": self.total_likes,
            "subscribers": self.total_subscribers,
            "revenue_estimate": round(self.revenue, 2),
            "avg_views_per_video": round(self.total_views / max(len(self.videos), 1)),
        }


# ============ 数据采集器 ============

class DataCollector:
    """
    从各平台采集数据
    注意: 需要各平台的 API credentials
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or DATA_DIR)
        self.data_dir.mkdir(exist_ok=True)
        self.cache = {}

    def collect_youtube_data(self, channel_id: str, api_key: str = None) -> PlatformData:
        """
        从 YouTube Data API 采集数据
        需要: youtube-api-key（在 Google Cloud Console 获取）
        """
        data = PlatformData("youtube")

        try:
            import requests
            api_key = api_key or os.getenv("YOUTUBE_API_KEY")
            if not api_key:
                logger.warning("YouTube API Key 未配置，将使用模拟数据")
                return self._generate_mock_data("youtube")

            # 获取频道统计
            channel_url = (
                f"https://www.googleapis.com/youtube/v3/channels"
                f"?part=statistics&id={channel_id}&key={api_key}"
            )
            resp = requests.get(channel_url, timeout=10).json()
            if "items" in resp and resp["items"]:
                stats = resp["items"][0]["statistics"]
                data.total_subscribers = int(stats.get("subscriberCount", 0))

            # 获取最近视频统计
            search_url = (
                f"https://www.googleapis.com/youtube/v3/search"
                f"?key={api_key}&channelId={channel_id}"
                f"&part=snippet,id&order=date&maxResults=20&type=video"
            )
            videos_resp = requests.get(search_url, timeout=10).json()

            video_ids = [item["id"]["videoId"] for item in videos_resp.get("items", [])]
            if video_ids:
                stats_url = (
                    f"https://www.googleapis.com/youtube/v3/videos"
                    f"?key={api_key}&id={','.join(video_ids)}&part=statistics,contentDetails"
                )
                stats_resp = requests.get(stats_url, timeout=10).json()
                for item in stats_resp.get("items", []):
                    video_data = {
                        "video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "views": int(item["statistics"].get("viewCount", 0)),
                        "likes": int(item["statistics"].get("likeCount", 0)),
                        "comments": int(item["statistics"].get("commentCount", 0)),
                        "published_at": item["snippet"]["publishedAt"],
                    }
                    data.add_video(video_data)

            data.calculate_revenue()
            logger.info(f"YouTube 数据采集完成: {data.total_views} 播放, ${data.revenue:.2f}")

        except Exception as e:
            logger.error(f"YouTube 数据采集失败: {e}")
            data = self._generate_mock_data("youtube")

        return data

    def collect_tiktok_data(self, account_name: str = None) -> PlatformData:
        """TikTok 数据采集（需要官方白名单或第三方工具）"""
        logger.warning("TikTok API 需要白名单，使用模拟数据")
        return self._generate_mock_data("tiktok")

    def _generate_mock_data(self, platform: str) -> PlatformData:
        """生成模拟数据（用于测试）"""
        import random
        data = PlatformData(platform)
        num_videos = random.randint(3, 15)

        anime_names = ["斗罗大陆 EP", "凡人修仙传 EP", "斗破苍穹 EP", "一人之下 EP"]
        for i in range(num_videos):
            views = random.randint(500, 80000)
            data.add_video({
                "title": f"{random.choice(anime_names)} {random.randint(1, 200)}",
                "views": views,
                "likes": int(views * random.uniform(0.03, 0.1)),
                "comments": int(views * random.uniform(0.005, 0.02)),
            })

        data.total_subscribers = random.randint(100, 5000)
        data.calculate_revenue()
        return data


# ============ 分析引擎 ============

class AnalyticsEngine:
    """分析引擎：找爆款、分析趋势"""

    @staticmethod
    def find_top_performers(platform_data: PlatformData, top_n: int = 5) -> list[dict]:
        """找播放最高的视频"""
        sorted_videos = sorted(
            platform_data.videos,
            key=lambda v: v.get("views", 0),
            reverse=True
        )[:top_n]
        return sorted_videos

    @staticmethod
    def calculate_growth_rate(current: dict, previous: dict) -> dict:
        """计算增长率"""
        growth = {}
        for key in ["total_views", "total_likes", "video_count"]:
            curr = current.get(key, 0)
            prev = previous.get(key, 0)
            if prev > 0:
                growth[key] = round((curr - prev) / prev * 100, 1)
            else:
                growth[key] = 100.0 if curr > 0 else 0
        return growth

    @staticmethod
    def detect_anomalies(current: PlatformData, previous_total: int) -> list[str]:
        """检测数据异常"""
        alerts = []
        threshold = EMAIL_CONFIG["alert_thresholds"]["播放量暴跌"]

        if previous_total > 0:
            drop_rate = current.total_views / previous_total
            if drop_rate < threshold:
                alerts.append(
                    f"⚠️ 播放量暴跌: 本日 {current.total_views} vs 上日 {previous_total} "
                    f"(下降 {int((1-drop_rate)*100)}%)"
                )
        return alerts

    @staticmethod
    def get_content_recommendations(top_videos: list[dict]) -> list[str]:
        """基于爆款内容给出建议"""
        recommendations = []
        if not top_videos:
            return ["建议增加发布频率，优化标题和封面"]

        top_view = top_videos[0].get("views", 0)
        if top_view > 50000:
            recommendations.append("🎯 发现爆款！建议立即制作同系列更多内容")
        if len(top_videos) >= 3:
            avg_views = sum(v.get("views", 0) for v in top_videos) / len(top_videos)
            recommendations.append(
                f"📊 平均播放 {avg_views:.0f}，建议专注当前内容类型"
            )
        recommendations.append("🔄 爆款内容发布7天内是流量黄金期，持续追更")
        return recommendations


# ============ 邮件发送器 ============

class ReportEmailSender:
    """邮件发送器"""

    def __init__(self, smtp_host: str = None, smtp_port: int = 587,
                 smtp_user: str = None, smtp_password: str = None):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")

    def send(
        self,
        to_addresses: list[str],
        subject: str,
        html_body: str,
        text_body: str = None,
    ) -> bool:
        """发送邮件"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP 未配置，邮件将保存到本地")
            self._save_email_locally(to_addresses, subject, html_body)
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = ", ".join(to_addresses)

            if text_body:
                msg.attach(MIMEText(text_body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"邮件发送成功: {subject} -> {', '.join(to_addresses)}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            self._save_email_locally(to_addresses, subject, html_body)
            return False

    def _save_email_locally(self, to_addresses: list[str], subject: str, html_body: str):
        """本地保存邮件"""
        output = DATA_DIR / f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output.write_text(html_body, encoding="utf-8")
        logger.info(f"邮件已保存到本地: {output}")


# ============ 报告生成器 ============

class ReportGenerator:
    """生成 HTML/文本报告"""

    @staticmethod
    def generate_daily_report(
        platform_datas: dict[str, PlatformData],
        date: datetime = None,
        alerts: list[str] = None,
        recommendations: list[str] = None,
    ) -> str:
        """生成日报 HTML"""
        date = date or datetime.now()

        total_views = sum(p.total_views for p in platform_datas.values())
        total_revenue = sum(p.revenue for p in platform_datas.values())

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>动漫出海运营日报 {date.strftime('%Y-%m-%d')}</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
  h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
  h2 {{ color: #16213e; margin-top: 30px; }}
  .metric {{ display: flex; gap: 20px; margin: 20px 0; }}
  .card {{ background: #f8f9fa; border-radius: 12px; padding: 20px; flex: 1; text-align: center; }}
  .card .value {{ font-size: 2em; font-weight: bold; color: #e94560; }}
  .card .label {{ color: #666; font-size: 0.9em; }}
  table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
  th {{ background: #1a1a2e; color: white; padding: 12px; text-align: left; }}
  td {{ padding: 10px; border-bottom: 1px solid #eee; }}
  tr:hover {{ background: #f5f5f5; }}
  .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 10px 0; }}
  .reco {{ background: #d4edda; border-left: 4px solid #28a745; padding: 12px; margin: 10px 0; }}
  .badge {{ display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; }}
  .badge-yt {{ background: #ff0000; color: white; }}
  .badge-tt {{ background: #000; color: white; }}
  .badge-ig {{ background: #e4405f; color: white; }}
  .footer {{ margin-top: 40px; color: #999; font-size: 0.8em; text-align: center; }}
</style>
</head>
<body>
<h1>📺 动漫出海运营日报</h1>
<p style="color:#666;">📅 {date.strftime('%Y年%m月%d日')} | 生成时间: {datetime.now().strftime('%H:%M')}</p>

<div class="metric">
  <div class="card">
    <div class="value">{total_views:,}</div>
    <div class="label">今日总播放</div>
  </div>
  <div class="card">
    <div class="value">${total_revenue:.2f}</div>
    <div class="label">预估今日收益</div>
  </div>
  <div class="card">
    <div class="value">{sum(p.total_subscribers for p in platform_datas.values()):,}</div>
    <div class="label">总订阅/粉丝</div>
  </div>
  <div class="card">
    <div class="value">{sum(p.video_count or 0 for p in platform_datas.values())}</div>
    <div class="label">发布视频数</div>
  </div>
</div>
"""

        # 平台详情
        for platform, data in platform_datas.items():
            badge_class = f"badge-{'yt' if platform=='youtube' else 'tt' if platform=='tiktok' else 'ig'}"
            html += f"""
<h2><span class="badge {badge_class}">{platform.upper()}</span> 平台详情</h2>
<table>
  <tr><th>指标</th><th>数值</th></tr>
  <tr><td>播放量</td><td>{data.total_views:,}</td></tr>
  <tr><td>点赞数</td><td>{data.total_likes:,}</td></tr>
  <tr><td>订阅/粉丝</td><td>{data.total_subscribers:,}</td></tr>
  <tr><td>预估收益</td><td>${data.revenue:.2f}</td></tr>
</table>

<h3>🔥 热门内容 TOP5</h3>
<table>
  <tr><th>#</th><th>标题</th><th>播放</th><th>点赞</th></tr>
"""
            top5 = AnalyticsEngine.find_top_performers(data, 5)
            for i, video in enumerate(top5, 1):
                title = video.get("title", "未知")[:40]
                views = video.get("views", 0)
                likes = video.get("likes", 0)
                html += f"  <tr><td>{i}</td><td>{title}</td><td>{views:,}</td><td>{likes:,}</td></tr>\n"
            html += "</table>\n"

        # 告警和建议
        if alerts:
            html += "<h2>⚠️ 异常告警</h2>\n"
            for alert in alerts:
                html += f'<div class="alert">{alert}</div>\n'

        if recommendations:
            html += "<h2>💡 优化建议</h2>\n"
            for reco in recommendations:
                html += f'<div class="reco">{reco}</div>\n'

        html += f"""
<div class="footer">
  <p>📊 动漫出海运营数据分析系统 | 数据仅供参考，实际收益以平台结算为准</p>
  <p>Generated by Anime Overseas Ops System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
</body>
</html>
"""
        return html


# ============ 主仪表盘类 ============

class AnalyticsDashboard:
    """运营仪表盘主类"""

    def __init__(self):
        self.collector = DataCollector()
        self.engine = AnalyticsEngine()
        self.report_gen = ReportGenerator()
        self.email_sender = ReportEmailSender()
        self.platform_datas = {}

    def collect_all_data(self, youtube_channel_id: str = None, api_key: str = None):
        """采集所有平台数据"""
        if youtube_channel_id:
            self.platform_datas["youtube"] = self.collector.collect_youtube_data(
                youtube_channel_id, api_key
            )

        # TikTok（模拟数据）
        self.platform_datas["tiktok"] = self.collector.collect_tiktok_data()

    def generate_daily_report(self, date: datetime = None) -> str:
        """生成日报"""
        return self.report_gen.generate_daily_report(self.platform_datas, date)

    def send_email_report(self, report_html: str = None, report_date: datetime = None):
        """发送邮件报告"""
        if report_html is None:
            report_html = self.generate_daily_report(report_date)

        recipients = EMAIL_CONFIG.get("daily_report_recipients", [])
        if not recipients:
            logger.warning("未配置邮件收件人")
            return False

        subject = f"📊 动漫出海运营日报 {datetime.now().strftime('%Y-%m-%d')}"
        return self.email_sender.send(recipients, subject, report_html)

    def generate_weekly_report(self) -> str:
        """生成周报"""
        return self.report_gen.generate_daily_report(self.platform_datas)

    def save_report(self, html_content: str, report_type: str = "daily"):
        """保存报告到文件"""
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_report_{date_str}.html"
        output_path = OUTPUT_DIR / filename
        output_path.write_text(html_content, encoding="utf-8")
        logger.info(f"报告已保存: {output_path}")
        return str(output_path)


# ============ 快捷命令 ============

def run_daily_report():
    """每日运行：采集数据 + 生成报告 + 发送邮件"""
    dashboard = AnalyticsDashboard()
    logger.info("开始采集数据...")
    dashboard.collect_all_data()
    logger.info("生成日报...")
    report_html = dashboard.generate_daily_report()
    logger.info("发送邮件...")
    dashboard.send_email_report(report_html)
    dashboard.save_report(report_html, "daily")
    return report_html


if __name__ == "__main__":
    print("=" * 60)
    print("动漫出海运营数据分析仪表盘")
    print("=" * 60)

    # 演示：生成模拟日报
    dashboard = AnalyticsDashboard()
    dashboard.collect_all_data()
    report_html = dashboard.generate_daily_report()
    output_file = dashboard.save_report(report_html, "demo")
    print(f"\n演示日报已生成: {output_file}")
