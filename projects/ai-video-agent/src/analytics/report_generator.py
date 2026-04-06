# AI 短视频运营 Agent - 数据分析报告模块

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

class ReportGenerator:
    """运营数据报告生成器"""

    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.load_config()
        self.setup_paths()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}

    def setup_paths(self):
        """设置路径"""
        self.reports_dir = Path("outputs/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def collect_weekly_data(self):
        """收集本周数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # 模拟数据（实际项目中从各平台API获取）
        data = {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "days": 7
            },
            "platforms": self.get_platform_data(),
            "content": self.get_content_data(),
            "insights": self.generate_insights(),
            "top_videos": self.get_top_videos(),
            "follower_growth": self.get_follower_growth(),
            "engagement_stats": self.get_engagement_stats()
        }

        return data

    def get_platform_data(self):
        """获取各平台数据"""
        return {
            "douyin": {
                "name": "抖音",
                "posts": 7,
                "views": 45678,
                "likes": 3892,
                "comments": 456,
                "shares": 234,
                "followers": 1234,
                "followers_change": 156,
                "engagement_rate": 8.5,
                "avg_watch_time": 28.5
            },
            "tiktok": {
                "name": "TikTok",
                "posts": 7,
                "views": 34567,
                "likes": 2890,
                "comments": 345,
                "shares": 567,
                "followers": 890,
                "followers_change": 89,
                "engagement_rate": 9.2,
                "avg_watch_time": 32.1
            },
            "youtube": {
                "name": "YouTube Shorts",
                "posts": 5,
                "views": 23456,
                "likes": 1567,
                "comments": 234,
                "shares": 123,
                "followers": 567,
                "followers_change": 45,
                "engagement_rate": 6.7,
                "avg_watch_time": 25.3
            },
            "instagram": {
                "name": "Instagram Reels",
                "posts": 3,
                "views": 12345,
                "likes": 890,
                "comments": 123,
                "shares": 67,
                "followers": 345,
                "followers_change": 23,
                "engagement_rate": 7.2,
                "avg_watch_time": 20.5
            }
        }

    def get_content_data(self):
        """获取内容数据"""
        return [
            {"id": "SP-001", "ip": "禅心师姐", "type": "早安禅语", "views": 15670, "likes": 1234, "platform": "抖音"},
            {"id": "SP-002", "ip": "禅心师姐", "type": "知识科普", "views": 12345, "likes": 987, "platform": "抖音"},
            {"id": "SP-003", "ip": "爪爪博士", "type": "行为解读", "views": 9876, "likes": 765, "platform": "TikTok"},
            {"id": "SP-004", "ip": "爪爪博士", "type": "搞笑集锦", "views": 18765, "likes": 1567, "platform": "TikTok"},
            {"id": "SP-005", "ip": "禅心师姐", "type": "故事分享", "views": 11234, "likes": 890, "platform": "YouTube"},
        ]

    def get_top_videos(self):
        """获取本周爆款视频"""
        return [
            {
                "rank": 1,
                "title": "狗狗舔你不是在撒娇！是在告诉你这5件事",
                "ip": "爪爪博士",
                "platform": "TikTok",
                "views": 18765,
                "likes": 1567,
                "engagement_rate": 10.5,
                "key_factors": ["高互动话题", "实用知识点", "可爱画面"]
            },
            {
                "rank": 2,
                "title": "早安｜当下，才是最好的答案",
                "ip": "禅心师姐",
                "platform": "抖音",
                "views": 15670,
                "likes": 1234,
                "engagement_rate": 9.8,
                "key_factors": ["黄金时段发布", "温暖治愈风格", "精准标签"]
            },
            {
                "rank": 3,
                "title": "痛苦的根源，逃不出这3个字",
                "ip": "禅心师姐",
                "platform": "抖音",
                "views": 12345,
                "likes": 987,
                "engagement_rate": 8.9,
                "key_factors": ["数字钩子", "情感共鸣", "收藏率高"]
            }
        ]

    def generate_insights(self):
        """生成数据洞察"""
        return [
            {
                "type": "positive",
                "title": "宠物内容表现亮眼",
                "description": "爪爪博士的搞笑集锦内容表现最佳，互动率达到10.5%，说明宠物赛道用户活跃度高。",
                "recommendation": "建议增加宠物搞笑内容的发布频率。"
            },
            {
                "type": "positive",
                "title": "早安系列稳定输出",
                "description": "禅心师姐的早安禅语系列保持稳定增长，平均播放量超过15000。",
                "recommendation": "继续保持每日早安更新，建立用户习惯。"
            },
            {
                "type": "info",
                "title": "TikTok 分享率最高",
                "description": "TikTok 平台的分享率达到1.64%，说明内容具有传播潜力。",
                "recommendation": "优化内容结构，增加反转和彩蛋元素。"
            },
            {
                "type": "warning",
                "title": "YouTube 表现相对较弱",
                "description": "YouTube Shorts 的平均观看时长较短(25.3秒)，完播率偏低。",
                "recommendation": "优化视频开头3秒吸引力，调整内容节奏。"
            }
        ]

    def get_follower_growth(self):
        """获取粉丝增长数据"""
        return {
            "total": 3036,
            "change": 313,
            "change_rate": 11.5,
            "platforms": {
                "douyin": {"current": 1234, "new": 156},
                "tiktok": {"current": 890, "new": 89},
                "youtube": {"current": 567, "new": 45},
                "instagram": {"current": 345, "new": 23}
            }
        }

    def get_engagement_stats(self):
        """获取互动统计"""
        total_views = 45678 + 34567 + 23456 + 12345
        total_likes = 3892 + 2890 + 1567 + 890
        total_comments = 456 + 345 + 234 + 123

        return {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "overall_engagement_rate": round(total_likes / total_views * 100, 2),
            "avg_comments_per_video": round(total_comments / 22, 1),
            "viral_rate": 0.14  # 14%的视频成为爆款
        }

    def generate_html_report(self, data):
        """生成 HTML 报告"""
        period = data["period"]

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI短视频运营报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 16px 16px 0 0; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 14px; }}
        .content {{ background: white; padding: 30px; border-radius: 0 0 16px 16px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .stat-card {{ padding: 20px; border-radius: 12px; text-align: center; color: white; }}
        .stat-card.blue {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .stat-card.green {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-card.orange {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.purple {{ background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%); }}
        .stat-value {{ font-size: 32px; font-weight: bold; }}
        .stat-label {{ font-size: 12px; opacity: 0.9; margin-top: 5px; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #667eea; font-size: 18px; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 15px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f5f7fa; font-weight: 600; }}
        .platform-badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; color: white; }}
        .douyin {{ background: #fe2c55; }}
        .tiktok {{ background: #000; }}
        .youtube {{ background: #ff0000; }}
        .instagram {{ background: linear-gradient(45deg, #f09433, #e6683c, #dc2743); }}
        .insight-box {{ background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .insight-box.positive {{ background: #e8f5e9; }}
        .insight-box.warning {{ background: #fff3e0; }}
        .insight-title {{ font-weight: bold; margin-bottom: 5px; }}
        .insight-desc {{ font-size: 14px; color: #666; }}
        .insight-rec {{ font-size: 13px; color: #1976d2; margin-top: 8px; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px; }}
        .top-video {{ background: linear-gradient(135deg, #fef9d7 0%, #dcedc1 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #11998e; margin: 15px 0; }}
        .top-video h4 {{ margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 AI 短视频运营报告</h1>
            <p>禅心师姐 × 爪爪博士 · 出海运营数据周报</p>
            <p>{period['start']} 至 {period['end']}</p>
        </div>

        <div class="content">
            <!-- 数据总览 -->
            <div class="section">
                <h2>📈 一、数据总览</h2>
                <div class="stats-grid">
                    <div class="stat-card blue">
                        <div class="stat-value">{data['engagement_stats']['total_views']:,}</div>
                        <div class="stat-label">总播放量</div>
                    </div>
                    <div class="stat-card green">
                        <div class="stat-value">{data['engagement_stats']['total_likes']:,}</div>
                        <div class="stat-label">总点赞</div>
                    </div>
                    <div class="stat-card orange">
                        <div class="stat-value">+{data['follower_growth']['change']}</div>
                        <div class="stat-label">新增粉丝</div>
                    </div>
                    <div class="stat-card purple">
                        <div class="stat-value">{data['engagement_stats']['overall_engagement_rate']}%</div>
                        <div class="stat-label">互动率</div>
                    </div>
                </div>
            </div>

            <!-- 各平台表现 -->
            <div class="section">
                <h2>🌐 二、各平台表现</h2>
                <table>
                    <thead>
                        <tr>
                            <th>平台</th>
                            <th>发布</th>
                            <th>播放</th>
                            <th>点赞</th>
                            <th>评论</th>
                            <th>粉丝增长</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self.generate_platform_rows(data['platforms'])}
                    </tbody>
                </table>
            </div>

            <!-- 本周爆款 -->
            <div class="section">
                <h2>🔥 三、本周爆款 TOP 3</h2>
                {self.generate_top_videos_html(data['top_videos'])}
            </div>

            <!-- 数据洞察 -->
            <div class="section">
                <h2>💡 四、数据洞察与建议</h2>
                {self.generate_insights_html(data['insights'])}
            </div>

            <!-- 下周计划 -->
            <div class="section">
                <h2>📅 五、下周发布计划</h2>
                <table>
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>IP</th>
                            <th>内容类型</th>
                            <th>发布时间</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>周一</td><td>禅心师姐</td><td>早安禅语</td><td>06:00</td></tr>
                        <tr><td>周二</td><td>爪爪博士</td><td>行为解读</td><td>12:30</td></tr>
                        <tr><td>周三</td><td>禅心师姐</td><td>冥想引导</td><td>22:30</td></tr>
                        <tr><td>周四</td><td>爪爪博士</td><td>情感治愈</td><td>21:00</td></tr>
                        <tr><td>周五</td><td>禅心师姐</td><td>故事分享</td><td>21:00</td></tr>
                        <tr><td>周六</td><td>爪爪博士</td><td>搞笑集锦</td><td>18:00</td></tr>
                        <tr><td>周日</td><td>禅心师姐</td><td>日常修行</td><td>10:00</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="footer">
                <p>📧 本报告由 AI 短视频运营系统自动生成</p>
                <p>📅 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <p>📮 报告将发送至：h13751019800@163.com</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        return html

    def generate_platform_rows(self, platforms):
        """生成平台数据行"""
        rows = ""
        for platform, stats in platforms.items():
            badge_class = platform
            rows += f"""
                        <tr>
                            <td><span class="platform-badge {badge_class}">{stats['name']}</span></td>
                            <td>{stats['posts']}</td>
                            <td>{stats['views']:,}</td>
                            <td>{stats['likes']:,}</td>
                            <td>{stats['comments']:,}</td>
                            <td style="color: #11998e;">+{stats['followers_change']}</td>
                        </tr>
            """
        return rows

    def generate_top_videos_html(self, top_videos):
        """生成爆款视频 HTML"""
        html = ""
        for video in top_videos:
            html += f"""
                <div class="top-video">
                    <h4>🏆 第{video['rank']}名：{video['title']}</h4>
                    <p><span class="platform-badge {video['platform']}">{video['platform']}</span>
                    播放 {video['views']:,} | 点赞 {video['likes']:,} | 互动率 {video['engagement_rate']}%</p>
                    <p style="margin-top: 8px;"><strong>爆款要素：</strong>{' · '.join(video['key_factors'])}</p>
                </div>
            """
        return html

    def generate_insights_html(self, insights):
        """生成洞察 HTML"""
        html = ""
        for insight in insights:
            box_class = insight['type']
            icon = "✅" if box_class == "positive" else ("⚠️" if box_class == "warning" else "ℹ️")
            html += f"""
                <div class="insight-box {box_class}">
                    <div class="insight-title">{icon} {insight['title']}</div>
                    <div class="insight-desc">{insight['description']}</div>
                    <div class="insight-rec">💡 {insight['recommendation']}</div>
                </div>
            """
        return html

    def save_report(self, html_content):
        """保存报告"""
        filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📄 报告已保存: {filepath}")
        return str(filepath)

    def generate_and_save(self):
        """生成并保存报告"""
        data = self.collect_weekly_data()
        html = self.generate_html_report(data)
        filepath = self.save_report(html)
        return filepath, html


if __name__ == "__main__":
    # 测试报告生成
    generator = ReportGenerator()

    print("=" * 50)
    print("📊 数据报告生成器 - 测试")
    print("=" * 50)

    # 生成报告
    filepath, html = generator.generate_and_save()
    print(f"\n✅ 报告已生成: {filepath}")
    print(f"📄 报告长度: {len(html)} 字符")
