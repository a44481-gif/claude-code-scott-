"""
动漫出海运营配置中心
anime_overseas/anime_ops_config.py

用法: from anime_ops_config import *
"""

import os
from pathlib import Path

# ============ 路径配置 ============
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

for d in [DATA_DIR, ASSETS_DIR, OUTPUT_DIR, LOG_DIR]:
    d.mkdir(exist_ok=True)

# ============ 平台配置 ============
PLATFORMS = {
    "youtube": {
        "name": "YouTube Shorts",
        "priority": 1,
        "变现方式": ["广告分成", "商单", "频道会员"],
        "起号门槛": "1000订阅 + 4000小时 或 1000万Shorts播放",
        "CPM范围": "$4-15/千播放",
        "最低提现": "$100",
        "官网": "https://studio.youtube.com",
    },
    "tiktok": {
        "name": "TikTok",
        "priority": 2,
        "变现方式": ["Creator Fund", "商单", "带货佣金"],
        "起号门槛": "10000粉丝",
        "CPM范围": "$0.02-0.05/千播放",
        "最低提现": "$50",
        "官网": "https://www.tiktok.com/business",
    },
    "instagram": {
        "name": "Instagram Reels",
        "priority": 3,
        "变现方式": ["商单", "品牌合作", "带货"],
        "起号门槛": "1000粉丝",
        "CPM范围": "$2-10/千播放",
        "最低提现": "$25",
        "官网": "https://business.instagram.com",
    },
    "facebook": {
        "name": "Facebook Reels",
        "priority": 4,
        "变现方式": ["广告分成", "品牌合作"],
        "起号门槛": "10000粉丝",
        "CPM范围": "$1-5/千播放",
        "最低提现": "$25",
        "官网": "https://www.facebook.com/business",
    },
    "pinterest": {
        "name": "Pinterest",
        "priority": 5,
        "变现方式": ["联盟带货", "广告"],
        "起号门槛": "500粉丝",
        "CPM范围": "$0.5-3/千播放",
        "最低提现": "$10",
        "官网": "https://business.pinterest.com",
    },
}

# ============ 地区配置 ============
REGIONS = {
    "english": {
        "name": "英语区（欧美）",
        "languages": ["en"],
        "target_countries": ["US", "GB", "CA", "AU", "NZ"],
        "platform_priority": ["YouTube", "TikTok", "Instagram"],
        "currency": "USD",
        "cpm_base": 8,
        "cultural_tips": "喜欢快节奏、解说型内容，弹幕文化浓厚",
        "禁忌": "避免政治话题，避免过度血腥",
    },
    "southeast_asia": {
        "name": "东南亚",
        "languages": ["id", "vi", "th", "tl", "ms"],
        "target_countries": ["ID", "VN", "TH", "PH", "MY", "SG"],
        "platform_priority": ["TikTok", "YouTube", "Facebook"],
        "currency": "USD",
        "cpm_base": 2,
        "cultural_tips": "印尼/越南/泰国对仙侠/玄幻接受度高，菲律宾英语好",
        "禁忌": "泰国禁止亵渎皇室，避免提及宗教争议",
    },
    "middle_east": {
        "name": "中东",
        "languages": ["ar"],
        "target_countries": ["SA", "AE", "QA", "KW", "EG"],
        "platform_priority": ["YouTube", "TikTok", "Instagram"],
        "currency": "USD",
        "cpm_base": 4,
        "cultural_tips": "高ARPU，华人账号少，动漫解说稀缺",
        "禁忌": "避免以色列相关内容，禁止酒精/猪肉内容",
    },
    "latin_america": {
        "name": "拉丁美洲",
        "languages": ["es", "pt"],
        "target_countries": ["BR", "MX", "CO", "AR", "CL", "PE"],
        "platform_priority": ["YouTube", "TikTok"],
        "currency": "USD",
        "cpm_base": 2,
        "cultural_tips": "巴西葡语，其他西语，对热血漫/少女漫接受度高",
        "禁忌": "避免政治敏感话题",
    },
    "korea_japan": {
        "name": "日韩",
        "languages": ["ko", "ja"],
        "target_countries": ["KR", "JP"],
        "platform_priority": ["YouTube", "TikTok"],
        "currency": "USD",
        "cpm_base": 5,
        "cultural_tips": "本土内容竞争激烈，需差异化（中文动漫解说）",
        "禁忌": "严格版权保护，需要明确授权",
    },
}

# ============ 内容选品配置 ============
CONTENT_GENRES = {
    "xuanhuan": {
        "name": "玄幻/仙侠",
        "examples": ["斗罗大陆", "凡人修仙传", "完美世界", "斗破苍穹"],
        "best_regions": ["southeast_asia", "middle_east"],
        "tags_en": ["xuanhuan", "fantasy anime", "cultivation anime", "Chinese anime"],
        "tags_local": {
            "id": ["anime xuanhuan", "donghua fantasi"],
            "vi": ["anime tu tiên", "hoạt hình trung quốc"],
            "ar": ["أنمي صيني", "خيال صيني"],
            "es": ["anime de fantasía chino", "donghua"],
        },
        "变现潜力": "高",
        "合规建议": "优先拿授权，或使用<90秒解说+原创评论",
    },
    "urban_fantasy": {
        "name": "都市异能/爽文",
        "examples": ["全球高武", "万族之劫", "夜的命名术"],
        "best_regions": ["southeast_asia", "latin_america"],
        "tags_en": ["urban fantasy anime", "system anime", "Chinese web novel"],
        "变现潜力": "极高",
        "合规建议": "漫改短剧剪辑+解说最安全",
    },
    "action_battle": {
        "name": "热血战斗",
        "examples": ["一人之下", "狐妖小红娘", "刺客伍六七"],
        "best_regions": ["english", "southeast_asia", "latin_america"],
        "tags_en": ["action anime", "fight scene", "battle anime", "Chinese anime"],
        "变现潜力": "高",
        "合规建议": "战斗场景混剪需加原创解说",
    },
    "romance": {
        "name": "少女/恋爱",
        "examples": ["偷偷藏不住", "春日将晚", " Fam》, etc."],
        "best_regions": ["southeast_asia", "korea_japan", "english"],
        "tags_en": ["romance anime", "love story", "shoujo anime", "Chinese romance"],
        "变现潜力": "中",
        "合规建议": "甜宠片段自带传播属性，注意尺度",
    },
    "short_drama": {
        "name": "短剧漫改",
        "examples": ["霸总系列", "甜宠系列", "复仇系列"],
        "best_regions": ["southeast_asia", "middle_east", "latin_america"],
        "tags_en": ["short drama", "romance drama", "Chinese drama", "web drama"],
        "变现潜力": "极高",
        "合规建议": "短剧内容注意版权，找正规平台合作",
    },
}

# ============ 标题模板 ============
TITLE_TEMPLATES = {
    "en": [
        "{anime} EP {ep} - The Scene That BROKE the Internet 🔥",
        "This {anime} Scene Made Everyone CRY ({ep}) 💔",
        "Top 10 {anime} Moments That Gave Us CHILLS ⚡",
        "{anime} - The Most INSANE Scene Ever (EP {ep})",
        "Why Everyone is Talking About {anime} Right Now",
        "{anime} EP {ep} | {emotion_word} 🔥 [Eng Sub]",
        "I Can't Stop Rewatching This Scene in {anime} 💔",
    ],
    "id": [
        "{anime} EP {ep} - Adegan TERBAIK yang Viral! 🔥",
        "Adegan {anime} Ini BIKIN NANGIS Semua Orang 💔",
        "Top 10 Momen {anime} yang MEMBUNGKAM! ⚡",
        "{anime} EP {ep} - Scene yang GAK ADA DUanya!",
        "Mengapa Semua Orang Bicara Tentang {anime} Sekarang",
    ],
    "vi": [
        "{anime} EP {ep} - Cảnh Hay Nhất Đang Gây Sốt! 🔥",
        "Cảnh {anime} Này Khiến Ai Cũng KHÓC 💔",
        "Top 10 Khoảnh Khắc {anime} Gây Sốt ⚡",
        "{anime} EP {ep} - Cảnh Không Thể Tin Được!",
    ],
    "th": [
        "{anime} EP {ep} - ฉากสุดมันส์ที่กำลังไวรัล! 🔥",
        "ฉาก {anime} นี้ทำเอาทุกคนร้องไห้ 💔",
        "Top 10 ความประทับใจจาก {anime} ⚡",
    ],
    "ar": [
        "{anime} الحلقة {ep} - المشهد الذي صدمنا جميعًا! 🔥",
        "مشهد {anime} هذا جعل الجميع يبكي 💔",
        "أفضل 10 لحظات من {anime} أثارت ضجة! ⚡",
    ],
    "es": [
        "{anime} EP {ep} - La ESCENA que MEJOR TODO 🔥",
        "Esta escena de {anime} ME IMPACTÓ 💔",
        "Top 10 momentos de {anime} que lo CAMBIARON TODO ⚡",
        "{anime} EP {ep} - El MEJOR momento del anime 🔥",
    ],
    "pt": [
        "{anime} EP {ep} - A CENA que MUDOU TUDO! 🔥",
        "Essa cena de {anime} fez TODOS CHORAREM 💔",
        "Top 10 momentos de {anime} que EXPLODIRAM na internet ⚡",
    ],
}

# ============ 热门标签 ============
TRENDING_TAGS = {
    "en": [
        "anime", "animeedit", "animereview", "animeclips", "animefan",
        "bestanime", "topanime", "anime2026", "animemoments",
        "animeart", "animeneko", "manga", "donghua", "chineseanime",
    ],
    "id": [
        "anime", "animeedit", "animeterpopuler", "animeindonesia",
        "animelucu", "donghua", "animechina", "animeterbaru2026",
    ],
    "vi": [
        "anime", "animeviet", "hoathinh", "hoathinhtrungquoc",
        "donghua", "anime2026", "animehay", "animevip",
    ],
    "th": [
        "อนิเมะ", "อนิเมะไทย", "อนิเมะญี่ปุ่น", "อนิเมะจีน",
        "donghua", "อนิเมะ2026", "อนิเมะซับไทย",
    ],
    "ar": [
        "أنمي", "أنمي عربي", "أنمي ياباني", "أنمي صيني",
        "دو هوا", "أنمي2026", "أنمي_جديد", "أنمي_عربي",
    ],
    "es": [
        "anime", "animeespañol", "animelatino", "animegratis",
        "donghua", "anime2026", "animegratis", "manga",
    ],
    "pt": [
        "anime", "animesubpt", "animesbrasil", "donghua",
        "anime2026", "animegratis", "mangabr",
    ],
}

# ============ 联盟平台配置 ============
AFFILIATE_PLATFORMS = {
    "amazon": {
        "name": "Amazon Associates",
        "url": "https://affiliate-program.amazon.com",
        "commission": "1-10%",
        "适用类目": ["动漫周边", "手办", "服饰", "图书"],
        "注册要求": "有效网站或社媒账号",
    },
    "temumall": {
        "name": "Temu Affiliate",
        "url": "https://affiliate.temu.com",
        "commission": "5-20%",
        "适用类目": ["动漫周边", "潮流服饰", "家居"],
        "注册要求": "社媒账号即可",
    },
    "aliexpress": {
        "name": "AliExpress Partners",
        "url": "https://portals.aliexpress.com",
        "commission": "5-15%",
        "适用类目": ["动漫周边", "cosplay装备", "手办"],
        "注册要求": "免费注册",
    },
    "gumroad": {
        "name": "Gumroad",
        "url": "https://gumroad.com",
        "commission": "10%",
        "适用类目": ["数字壁纸", "头像包", "虚拟商品", "教程"],
        "注册要求": "邮箱即可",
    },
}

# ============ 变现参数 ============
MONETIZATION = {
    "youtube_cpm": 6,           # 默认CPM $6/千播放
    "youtube_cpm_range": (4, 15),
    "tiktok_cpm": 0.03,        # $0.03/千播放
    "instagram_cpm": 3,
    "facebook_cpm": 1.5,
    "pinterest_cpm": 1,
    "品牌商单起步价": 100,     # 美元/条
    "品牌商单成熟价": 500,     # 美元/条
    "配音服务单价": 80,        # 美元/条
    "字幕本地化": 40,          # 美元/条
    "版权代理佣金比例": 0.20,  # 20-30%
}

# ============ 邮件通知配置 ============
EMAIL_CONFIG = {
    "enabled": True,
    "daily_report_recipients": [
        "your@email.com",
    ],
    "weekly_report_recipients": [
        "your@email.com",
    ],
    "alert_thresholds": {
        "播放量暴跌": 0.3,      # 当播放量低于上篇的30%时告警
        "新爆款": 50000,        # 单视频播放超5万标记
        "新收益": 50,           # 日收益超$50通知
    },
}

# ============ 翻译API配置 ============
TRANSLATION = {
    "provider": "deepl",  # deepl / openai / google / libre
    "deepl_api_key": os.getenv("DEEPL_API_KEY", ""),
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "openai_model": "gpt-4o-mini",
    "openai_cost_per_1k_chars": 0.00015,  # GPT-4o-mini 成本
    "fallback_provider": "google",
    "cache_translations": True,
    "auto_detect_language": True,
}

# ============ 视频制作参数 ============
VIDEO_CONFIG = {
    "aspect_ratios": {
        "youtube_shorts": (9, 16),
        "tiktok": (9, 16),
        "instagram_reels": (9, 16),
        "youtube_main": (16, 9),
        "pinterest": (2, 3),
    },
    "resolutions": {
        "1080p": (1080, 1920),
        "720p": (720, 1280),
    },
    "fps": 30,
    "max_clip_duration": 90,  # 秒，二创安全边界
    "watermark_position": "bottom_right",
    "watermark_text": "@YourChannel",
}

# ============ 代理版权方列表（示例）===========
LICENSED_IP_SOURCES = [
    {
        "name": "Bilibili International",
        "contact": "international@bilibili.com",
        "available_ips": ["B站全部国漫漫作"],
        "合作模式": "非独家海外授权",
        "佣金比例": "20-30%",
    },
    {
        "name": "腾讯动漫国际",
        "contact": "overseas@tencent.com",
        "available_ips": ["斗罗大陆", "斗破苍穹", "一人之下"],
        "合作模式": "非独家授权",
        "佣金比例": "15-25%",
    },
    {
        "name": "快看漫画",
        "contact": "global@kuaikanwc.com",
        "available_ips": ["偷偷藏不住", "养敌为患"],
        "合作模式": "分成合作",
        "佣金比例": "20-35%",
    },
    {
        "name": "Webnovel Comics",
        "contact": "comics@webnovel.com",
        "available_ips": ["修仙类", "都市类IP"],
        "合作模式": "内容授权+分成",
        "佣金比例": "25-40%",
    },
]

# ============ 常用表情映射 ============
EMOJI_MAP = {
    "en": {"fire": "🔥", "cry": "💔", "shock": "😱", "laugh": "😂", "cool": "😎", "love": "❤️", "star": "⭐"},
    "id": {"fire": "🔥", "cry": "😭", "shock": "😱", "laugh": "😂", "cool": "😎", "love": "❤️", "star": "⭐"},
    "vi": {"fire": "🔥", "cry": "😭", "shock": "😱", "laugh": "😂", "cool": "😎", "love": "❤️", "star": "⭐"},
    "th": {"fire": "🔥", "cry": "😭", "shock": "😱", "laugh": "😂", "cool": "😎", "love": "❤️", "star": "⭐"},
    "ar": {"fire": "🔥", "cry": "😭", "shock": "😱", "laugh": "😂", "cool": "😎", "love": "❤️", "star": "⭐"},
    "es": {"fire": "🔥", "cry": "💔", "shock": "😱", "laugh": "😂", "cool": "😎", "love": "❤️", "star": "⭐"},
    "pt": {"fire": "🔥", "cry": "💔", "shock": "😱", "laugh": "😂", "cool": "😎", "love": "❤️", "star": "⭐"},
}

# ============ 情绪词库 ============
EMOTION_WORDS = {
    "en": ["Gave Us CHILLS", "Left Us SPEECHLESS", "SHOCKED Everyone", "MADE US CRY", "BROKE the Internet", "Went VIRAL"],
    "id": ["Bikin MERINDING", "Bikin NANGIS", "MEMBUNGKAM", "VIRAL", "GILA", "LUAR BIASA"],
    "vi": ["Khiến ta RUNG ĐỘNG", "Khiến ta KHÓC", "SỮNG SỐT", "GÂY SỐT", "QUÁ ĐỈNH", "VÔ ĐỊCH"],
    "th": ["ทำเอาสะดุด", "ทำเอาตกใจ", "ปังมาก", "ไวรัลสุด", "ฮือฮา", "สุดที่รัก"],
    "ar": ["أبكى الجميع", "صدمنا", "مجنون", "لا يُصدق", "انتشر بسرعة", "مذهل"],
    "es": ["Nos DEJÓ LOCOS", "NOS HIZO LLORAR", "NOS VOLVIMOS LOCOS", "SE HIZO VIRAL", "INCREÍBLE", "ESCANDALOSO"],
    "pt": ["Nos DEIXOU SEM PALAVRAS", "NOS FEZ CHORAR", "NOS SURPREENDEU", "FICOU VIRAL", "INCRÍVEL", "ABSURDO"],
}

if __name__ == "__main__":
    print("=" * 60)
    print("动漫出海运营配置中心 v1.0")
    print("=" * 60)
    print(f"配置目录: {BASE_DIR}")
    print(f"平台数量: {len(PLATFORMS)}")
    print(f"地区数量: {len(REGIONS)}")
    print(f"内容类型: {len(CONTENT_GENRES)}")
    print(f"联盟平台: {len(AFFILIATE_PLATFORMS)}")
    print("=" * 60)
    print("支持的语言:", list(TITLE_TEMPLATES.keys()))
    print("支持地区:", {k: v['name'] for k, v in REGIONS.items()})
