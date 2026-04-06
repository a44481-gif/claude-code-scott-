"""
动漫出海 - 版权安全内容筛查器
anime_overseas/copyright_screener.py

功能：
1. 分析视频内容版权风险等级
2. 自动检测剪辑时长是否安全
3. 检查是否包含高风险元素（未授权日漫/完整剧集）
4. 生成版权合规报告
5. 推荐授权获取路径

用法:
    screener = CopyrightScreener()
    result = screener.analyze("video_path", "斗罗大陆")
    print(result["risk_level"])
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from anime_ops_config import LOG_DIR, OUTPUT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "copyright.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("CopyrightScreener")


# ============ 版权风险数据库 ============

RISK_DATABASE = {
    # 高风险IP（需要明确授权）
    "high_risk": [
        "ONE PIECE", "Naruto", "Attack on Titan", "Demon Slayer", "Jujutsu Kaisen",
        "My Hero Academia", "Dragon Ball", "Bleach", "Death Note", "Fullmetal Alchemist",
        "Spy x Family", "Chainsaw Man", "Blue Lock", "Oshi no Ko", "Frieren",
        # 日漫剧场版
        "鬼滅の刃", "呪術廻戦", "進撃の巨人", "僕のヒーローアカデミア",
        # 国漫（有版权保护）
        "斗罗大陆", "完美世界", "吞噬星空", "全职高手",
    ],
    # 中等风险（可做合理使用）
    "medium_risk": [
        "凡人修仙传", "斗破苍穹", "一念永恒", "元龙", "万界仙宗",
        "狐妖小红娘", "一人之下", "灵笼", "秦时明月", "天行九歌",
        "刺客伍六七", "时光代理人", "明日方舟", "原神",
    ],
    # 低风险（官方宣传物料）
    "low_risk": [
        "官方预告片", "Official Trailer", "官方宣传", "Official PV",
        "官方剪辑", "官方片段",
    ],
}

# 版权方联系方式（示例）
IP_CONTACTS = {
    "斗罗大陆": {
        "rights_holder": "阅文集团/腾讯动漫",
        "contact": "overseas@tencent.com",
        "available_licenses": ["东南亚非独家", "YouTube分成授权"],
        "estimated_cost": "$500-2000/月",
        "note": "可通过腾讯动漫国际部申请",
    },
    "凡人修仙传": {
        "rights_holder": "起点中文网/Wuxia World",
        "contact": "international@qidian.com",
        "available_licenses": ["全球非独家"],
        "estimated_cost": "$300-1500/月",
    },
    "狐妖小红娘": {
        "rights_holder": "腾讯动漫",
        "contact": "overseas@tencent.com",
        "available_licenses": ["全球非独家"],
        "estimated_cost": "$200-800/月",
    },
}


# ============ 版权筛查器 ============

class CopyrightScreener:
    """
    版权安全筛查器
    评估视频内容的版权风险等级
    """

    def __init__(self):
        self.max_safe_duration = 90  # 秒，二创安全时长上限
        self.max_coverage_ratio = 0.20  # 最大使用比例

    def analyze(
        self,
        video_path: str,
        ip_name: str = None,
        duration_seconds: float = None,
        content_type: str = "clip",  # clip/review/mashup/analysis
    ) -> dict:
        """
        分析视频版权风险

        Returns:
            {
                "risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
                "risk_score": 0-100,
                "issues": [...],
                "recommendations": [...],
                "safe_to_publish": bool,
                "compliance_tips": [...],
            }
        }
        """
        ip_name = ip_name or "未知IP"
        ip_risk_tier = self._classify_ip_risk(ip_name)
        duration_score = self._score_duration(duration_seconds, content_type)
        type_score = self._score_content_type(content_type, ip_risk_tier)

        total_score = (ip_risk_tier["score"] * 0.4 +
                       duration_score * 0.3 +
                       type_score * 0.3)

        issues = []
        recommendations = []

        # 评估问题
        if ip_risk_tier["level"] == "CRITICAL":
            issues.append(f"🚫 '{ip_name}' 属于高风险未授权内容")
            recommendations.append("建议获取官方授权后再发布，或改用官方宣传物料")

        if ip_risk_tier["level"] == "HIGH":
            issues.append(f"⚠️ '{ip_name}' 需要版权授权")
            if duration_seconds and duration_seconds > self.max_safe_duration:
                issues.append(f"  - 剪辑时长 {duration_seconds}s 超过安全阈值 {self.max_safe_duration}s")
                recommendations.append(f"将剪辑控制在 {self.max_safe_duration}s 以内")

        if content_type not in ["analysis", "review"]:
            issues.append("ℹ️ 非评论/解说类内容需额外注意合理使用边界")

        # 合规建议
        compliance_tips = self._get_compliance_tips(content_type, ip_risk_tier["level"])

        # 风险等级判定
        if total_score < 25:
            risk_level = "LOW"
            safe_to_publish = True
        elif total_score < 50:
            risk_level = "MEDIUM"
            safe_to_publish = True
            recommendations.append("发布时添加免责声明和原创评论")
        elif total_score < 75:
            risk_level = "HIGH"
            safe_to_publish = False
        else:
            risk_level = "CRITICAL"
            safe_to_publish = False

        result = {
            "ip_name": ip_name,
            "ip_risk_tier": ip_risk_tier["level"],
            "content_type": content_type,
            "duration_seconds": duration_seconds,
            "risk_level": risk_level,
            "risk_score": round(total_score, 1),
            "issues": issues,
            "recommendations": recommendations,
            "compliance_tips": compliance_tips,
            "safe_to_publish": safe_to_publish,
            "safe_duration": self.max_safe_duration,
            "analyzed_at": datetime.now().isoformat(),
        }

        logger.info(
            f"版权筛查: {ip_name} [{content_type}] "
            f"风险={risk_level}({total_score:.0f}) 安全={'✅' if safe_to_publish else '❌'}"
        )
        return result

    def _classify_ip_risk(self, ip_name: str) -> dict:
        """分类IP风险等级"""
        upper_name = ip_name.upper()

        for name in RISK_DATABASE["high_risk"]:
            if name.upper() in upper_name or upper_name in name.upper():
                return {"level": "HIGH", "score": 80, "tier": "high_risk"}

        for name in RISK_DATABASE["medium_risk"]:
            if name.upper() in upper_name or upper_name in name.upper():
                return {"level": "MEDIUM", "score": 50, "tier": "medium_risk"}

        for name in RISK_DATABASE["low_risk"]:
            if name.upper() in upper_name:
                return {"level": "LOW", "score": 10, "tier": "low_risk"}

        # 国漫默认中等风险
        return {"level": "MEDIUM", "score": 45, "tier": "default"}

    def _score_duration(self, duration: float, content_type: str) -> float:
        """根据时长评分"""
        if duration is None:
            return 30  # 未知时长，中等风险

        if content_type in ["analysis", "review"]:
            safe_limit = 180  # 评论类可以稍长
        else:
            safe_limit = self.max_safe_duration

        if duration <= safe_limit:
            return max(10, 30 - duration / 10)
        elif duration <= safe_limit * 2:
            return min(80, 50 + (duration - safe_limit))
        else:
            return 100

    def _score_content_type(self, content_type: str, ip_tier: dict) -> float:
        """根据内容类型评分"""
        type_scores = {
            "official_clip": 10,     # 官方片段，安全
            "analysis": 25,           # 评析，最安全
            "review": 30,             # review，转换性使用
            "mashup": 50,            # 混剪，风险中等
            "clip": 60,              # 普通剪辑片段
            "full_episode": 90,      # 完整剧集，高风险
            "compilation": 70,       # 汇总剪辑
        }
        return type_scores.get(content_type, 50)

    def _get_compliance_tips(self, content_type: str, ip_level: str) -> list[str]:
        """获取合规建议"""
        tips = []

        if ip_level in ["HIGH", "CRITICAL"]:
            tips.append("🚫 此IP需要明确授权才能商业使用")
            tips.append("建议联系版权方申请非独家海外授权")

        if content_type in ["clip", "mashup"]:
            tips.append("✅ 可尝试 '评论/评析' 方向：添加原创解说>50%")
            tips.append("✅ 时长控制在 60-90 秒内，降低被投诉风险")
            tips.append("✅ 在描述中添加原创评论和免责声明")

        if content_type == "official_clip":
            tips.append("✅ 官方宣传物料风险较低")
            tips.append("✅ 描述中注明来源和版权方")
            tips.append("ℹ️ 部分平台允许官方宣传片段分享")

        tips.extend([
            "ℹ️ 合理使用四大要素：目的、性质、占比、市场影响",
            "💡 转换性使用（加评论/解说）可大幅降低风险",
            "📋 建议保留创作过程记录，以备申诉时使用",
        ])
        return tips

    def get_license_info(self, ip_name: str) -> Optional[dict]:
        """获取IP授权信息"""
        for known_ip, info in IP_CONTACTS.items():
            if known_ip in ip_name or ip_name in known_ip:
                return {"ip": known_ip, **info}
        return None

    def batch_analyze(self, entries: list[dict]) -> list[dict]:
        """批量筛查"""
        return [self.analyze(**entry) for entry in entries]


# ============ 合规内容规划 ============

class SafeContentPlanner:
    """合规内容规划器"""

    @staticmethod
    def get_safe_content_ideas(
        target_region: str = "english",
        content_length: str = "short"  # short / medium / long
    ) -> list[dict]:
        """
        推荐低风险内容创作方向

        Returns:
            [
                {
                    "idea": "内容创意",
                    "type": "clip/review/analysis",
                    "risk": "LOW/MEDIUM",
                    "template": "模板标题",
                    "tags": ["标签1", ...],
                }, ...
            ]
        """
        short_duration = "30-60s"
        ideas = [
            {
                "idea": "动漫解说系列",
                "description": "针对每集做2-3分钟深度解说，含剧情分析+个人观点",
                "type": "analysis",
                "risk": "LOW",
                "duration": "3-5min",
                "platforms": ["YouTube"],
                "template": "{动漫名} EP{集数} 深度解析：{分析角度}",
                "tags": ["anime review", "anime analysis", "深度解说"],
            },
            {
                "idea": "热血战斗名场面合集",
                "description": "剪辑多个IP的同类精彩战斗场景，配热门BGM",
                "type": "mashup",
                "risk": "MEDIUM",
                "duration": short_duration,
                "platforms": ["YouTube Shorts", "TikTok"],
                "template": "最强{战斗类型}名场面合集！燃爆了🔥",
                "tags": ["best fight scenes", "anime compilation", "燃烧"],
            },
            {
                "idea": "催泪场景集锦",
                "description": "某IP的感人场景剪辑，配合情绪化标题",
                "type": "clip",
                "risk": "MEDIUM",
                "duration": short_duration,
                "platforms": ["YouTube Shorts", "TikTok", "Instagram Reels"],
                "template": "看哭了！{动漫名} 最催泪的{场景类型}💔",
                "tags": ["anime cry", "emotional anime", "催泪"],
            },
            {
                "idea": "动漫冷知识/梗百科",
                "description": "分享IP相关的幕后花絮、冷知识、人气排行",
                "type": "analysis",
                "risk": "LOW",
                "duration": "1-3min",
                "platforms": ["YouTube", "TikTok"],
                "template": "{动漫名} 冷知识：{具体知识点} 🤔",
                "tags": ["anime facts", "anime trivia", "冷知识"],
            },
            {
                "idea": "壁纸/头像推荐",
                "description": "推荐高清壁纸/头像，适合手办类带货",
                "type": "static",
                "risk": "LOW",
                "duration": "静态图",
                "platforms": ["Pinterest", "Instagram", "TikTok"],
                "template": "{动漫名} 超清壁纸 | {集数}期",
                "tags": ["anime wallpaper", "anime pfp", "壁纸"],
            },
            {
                "idea": "粉丝二创混剪",
                "description": "粉丝向CP混剪，需要标注粉丝作品来源",
                "type": "fanwork",
                "risk": "MEDIUM",
                "duration": short_duration,
                "platforms": ["TikTok", "Instagram"],
                "template": "{CP名} | {情绪主题} 💕",
                "tags": ["anime edit", "fan edit", "CP混剪"],
            },
        ]
        return ideas

    @staticmethod
    def get_forbidden_content() -> list[str]:
        """获取禁止内容清单"""
        return [
            "完整剧集（整集>20分钟）上传",
            "未经授权的日漫剧场版",
            "直接转载无原创内容",
            "敏感/血腥内容（无年龄标识）",
            "版权方明确禁止二次创作的内容",
            "使用盗版/泄露素材",
        ]


if __name__ == "__main__":
    print("=" * 60)
    print("动漫出海 · 版权安全筛查工具")
    print("=" * 60)

    screener = CopyrightScreener()

    # 测试案例
    test_cases = [
        {"ip_name": "斗罗大陆", "duration_seconds": 60, "content_type": "clip"},
        {"ip_name": "One Piece", "duration_seconds": 120, "content_type": "clip"},
        {"ip_name": "凡人修仙传", "duration_seconds": 45, "content_type": "analysis"},
        {"ip_name": "Naruto", "duration_seconds": 90, "content_type": "mashup"},
        {"ip_name": "官方预告片", "duration_seconds": 30, "content_type": "official_clip"},
    ]

    for case in test_cases:
        result = screener.analyze(**case)
        print(f"\n📋 筛查: {case['ip_name']} [{case['content_type']}] {case['duration_seconds']}s")
        print(f"   风险等级: {result['risk_level']} ({result['risk_score']}分)")
        print(f"   可发布: {'✅' if result['safe_to_publish'] else '❌'}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"   {issue}")
        if result["recommendations"]:
            print(f"   建议: {result['recommendations'][0]}")

    print("\n" + "=" * 60)
    print("合规内容创意推荐")
    print("=" * 60)
    planner = SafeContentPlanner()
    ideas = planner.get_safe_content_ideas("english")
    for i, idea in enumerate(ideas, 1):
        print(f"\n{i}. {idea['idea']}")
        print(f"   类型: {idea['type']} | 风险: {idea['risk']} | 时长: {idea['duration']}")
        print(f"   模板: {idea['template']}")
        print(f"   平台: {', '.join(idea['platforms'])}")
