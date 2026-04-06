"""
动漫出海 - AI封面生成器
anime_overseas/thumbnail_generator.py

功能：
1. 基于模板批量生成封面
2. 支持多语言大标题
3. 自动排版、配色
4. 支持 YouTube/TikTok/Pinterest 多尺寸
5. 内置多种爆款封面模板

用法:
    from thumbnail_generator import ThumbnailGenerator, TemplateType
    gen = ThumbnailGenerator()
    gen.generate("output.png", title="震撼来袭", template=TemplateType.SHOCKING)
"""

import logging
from pathlib import Path
from typing import Optional

from anime_ops_config import LOG_DIR, OUTPUT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "thumbnail.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("ThumbnailGenerator")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow 未安装，请运行: pip install Pillow")


# ============ 封面模板类型 ============

class TemplateType:
    SHOCKING = "shocking"       # 震撼型：红色底+白字+大表情
    EMOTIONAL = "emotional"     # 情感型：深色底+柔和配色
    ACTION = "action"          # 战斗型：橙红色底+动态效果
    ROMANCE = "romance"         # 甜宠型：粉色渐变+爱心
    NEWS = "news"               # 资讯型：深蓝底+科技感
    RANKING = "ranking"        # 排行型：黑色底+金色数字


# ============ 配色方案 ============

COLOR_PALETTES = {
    TemplateType.SHOCKING: {
        "bg": (220, 30, 30),        # 红色
        "text": (255, 255, 255),    # 白色
        "accent": (255, 200, 0),   # 金色
        "shadow": (0, 0, 0, 180),
    },
    TemplateType.EMOTIONAL: {
        "bg": (20, 20, 40),         # 深蓝紫
        "text": (255, 220, 180),   # 暖白
        "accent": (255, 100, 150), # 粉红
        "shadow": (0, 0, 0, 200),
    },
    TemplateType.ACTION: {
        "bg": (255, 100, 20),       # 橙红
        "text": (255, 255, 255),
        "accent": (255, 255, 0),   # 黄色
        "shadow": (0, 0, 0, 180),
    },
    TemplateType.ROMANCE: {
        "bg": (255, 150, 180),     # 粉色
        "text": (255, 255, 255),
        "accent": (255, 80, 120),
        "shadow": (0, 0, 0, 150),
    },
    TemplateType.NEWS: {
        "bg": (10, 20, 60),         # 深蓝
        "text": (255, 255, 255),
        "accent": (0, 180, 255),   # 亮蓝
        "shadow": (0, 0, 0, 200),
    },
    TemplateType.RANKING: {
        "bg": (10, 10, 10),         # 黑色
        "text": (255, 215, 0),     # 金色
        "accent": (255, 100, 0),   # 橙色
        "shadow": (0, 0, 0, 220),
    },
}

# ============ 爆款封面元素 ============

EMOTION_ICONS = {
    TemplateType.SHOCKING: ["🔥", "😱", "💔", "⚡"],
    TemplateType.EMOTIONAL: ["💔", "😭", "❤️", "✨"],
    TemplateType.ACTION: ["⚡", "💥", "🔥", "⚔️"],
    TemplateType.ROMANCE: ["❤️", "💕", "✨", "💖"],
    TemplateType.NEWS: ["📢", "🎯", "📊", "🔔"],
    TemplateType.RANKING: ["🏆", "👑", "⭐", "1️⃣"],
}

FONT_FALLBACK_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",   # 黑体
    "C:/Windows/Fonts/simsun.ttc",   # 宋体
    "C:/Windows/Fonts/arial.ttf",   # Arial
    "C:/Windows/Fonts/seguisym.ttf", # Segoe UI
]


def find_available_font() -> Optional[ImageFont.FreeTypeFont]:
    """查找系统中可用的字体"""
    if not PIL_AVAILABLE:
        return None
    for path in FONT_FALLBACK_PATHS:
        try:
            return ImageFont.truetype(path, 40)
        except:
            continue
    return ImageFont.load_default()


# ============ 封面生成器 ============

class ThumbnailGenerator:
    """
    动漫封面生成器
    依赖: Pillow (pip install Pillow)
    """

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or OUTPUT_DIR / "thumbnails")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.font = find_available_font()
        self.font_large = self._scale_font(80)
        self.font_medium = self._scale_font(50)
        self.font_small = self._scale_font(30)

    def _scale_font(self, base_size: int):
        if PIL_AVAILABLE and self.font:
            try:
                return ImageFont.truetype(self.font.path, base_size)
            except:
                pass
        return None

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """#RRGGBB -> (R, G, B)"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def generate(
        self,
        output_path: str,
        title: str,
        subtitle: str = None,
        template: str = TemplateType.SHOCKING,
        size: tuple = (1280, 720),  # YouTube 16:9
        background_color: str = None,
        text_color: str = None,
        emoji: str = None,
        add_border: bool = True,
        add_glow: bool = True,
    ) -> str:
        """
        生成封面图

        Args:
            output_path: 输出文件路径
            title: 主标题
            subtitle: 副标题
            template: 模板类型
            size: 图片尺寸 (width, height)
            background_color: 背景色（覆盖模板）
            text_color: 文字色（覆盖模板）
            emoji: 表情符号（覆盖模板默认）
            add_border: 是否添加边框
            add_glow: 是否添加发光效果

        Returns:
            输出文件路径
        """
        if not PIL_AVAILABLE:
            logger.error("Pillow 未安装，无法生成封面")
            return ""

        output_path = Path(output_path)
        w, h = size

        # 获取配色
        palette = COLOR_PALETTES.get(template, COLOR_PALETTES[TemplateType.SHOCKING])
        bg = self._hex_to_rgb(background_color) if background_color else palette["bg"]
        fg = self._hex_to_rgb(text_color) if text_color else palette["text"]
        accent = palette["accent"]
        shadow = palette["shadow"]

        # 创建图像
        img = Image.new("RGB", (w, h), bg)
        draw = ImageDraw.Draw(img)

        # 添加渐变背景效果
        for i in range(h // 3):
            alpha = int(80 * (1 - i / (h // 3)))
            overlay_color = tuple(min(255, c + 30) for c in bg)
            draw.rectangle([(0, i * 3), (w, i * 3 + 3)], fill=overlay_color)

        # 边框
        if add_border:
            border_color = accent
            border_w = max(4, w // 200)
            draw.rectangle([0, 0, w-1, h-1], outline=border_color, width=border_w)

        # 主标题
        font = self.font_large or find_available_font()
        title_y = h // 2 - (font.size if font else 40) // 2

        if add_glow:
            # 阴影/发光效果
            glow_offset = max(2, w // 300)
            for ox, oy in [(-glow_offset, -glow_offset), (glow_offset, glow_offset),
                            (-glow_offset, glow_offset), (glow_offset, -glow_offset)]:
                draw.text((w//2 + ox, title_y + oy), title, font=font,
                          fill=(0, 0, 0, 150), anchor="mm")

        draw.text((w // 2, title_y), title, font=font, fill=fg, anchor="mm")

        # 副标题
        if subtitle:
            sub_font = self.font_medium or find_available_font()
            sub_y = title_y + (font.size if font else 80) + 10
            draw.text((w // 2, sub_y), subtitle, font=sub_font, fill=accent, anchor="mm")

        # 表情
        emoji_char = emoji or EMOTION_ICONS.get(template, EMOTION_ICONS[TemplateType.SHOCKING])[0]
        emoji_font_size = max(40, w // 15)
        try:
            emoji_font = ImageFont.truetype("C:/Windows/Fonts/seguisym.ttf", emoji_font_size)
        except:
            emoji_font = None

        # 右上角表情
        emoji_x = w - emoji_font_size - 20
        emoji_y = emoji_font_size // 2 + 10
        draw.text((emoji_x, emoji_y), emoji_char, font=emoji_font, fill=accent, anchor="mm")

        # 底部装饰线
        line_y = h - 30
        draw.rectangle([(50, line_y), (w - 50, line_y + 4)], fill=accent)

        # 保存
        img.save(str(output_path), "PNG", quality=95)
        logger.info(f"封面生成: {output_path}")
        return str(output_path)

    def generate_all_sizes(
        self,
        title: str,
        subtitle: str = None,
        template: str = TemplateType.SHOCKING,
        output_prefix: str = None,
    ) -> dict[str, str]:
        """
        一次性生成所有平台尺寸

        Returns:
            dict: {尺寸名: 文件路径}
        """
        results = {}
        output_prefix = output_prefix or title[:10].replace(" ", "_")

        sizes = {
            "youtube_main": (1280, 720),
            "youtube_shorts": (720, 1280),
            "tiktok": (720, 1280),
            "instagram": (1080, 1350),
            "pinterest": (1000, 1500),
        }

        for name, (w, h) in sizes.items():
            output_path = self.output_dir / f"{output_prefix}_{name}.png"
            self.generate(
                str(output_path), title, subtitle,
                template=template, size=(w, h)
            )
            results[name] = str(output_path)

        logger.info(f"全部 {len(results)} 种尺寸生成完毕")
        return results

    def batch_generate(
        self,
        entries: list[dict],
        template: str = TemplateType.SHOCKING,
    ) -> list[str]:
        """
        批量生成封面

        Args:
            entries: [{"title": "...", "subtitle": "...", "output": "..."}, ...]
        """
        results = []
        for i, entry in enumerate(entries):
            output_path = entry.get("output") or f"thumb_{i+1}.png"
            result = self.generate(
                output_path,
                title=entry["title"],
                subtitle=entry.get("subtitle"),
                template=template,
                emoji=entry.get("emoji"),
            )
            results.append(result)
        return results


# ============ 爆款封面模板函数 ============

def make_shocking_thumbnail(title: str, subtitle: str = None, output: str = None) -> str:
    """震撼型封面（最通用）"""
    gen = ThumbnailGenerator()
    return gen.generate(output or "shocking_thumb.png", title, subtitle, TemplateType.SHOCKING)


def make_emotional_thumbnail(title: str, subtitle: str = None, output: str = None) -> str:
    """情感型封面（用于催泪/感人场景）"""
    gen = ThumbnailGenerator()
    return gen.generate(output or "emotional_thumb.png", title, subtitle, TemplateType.EMOTIONAL)


def make_action_thumbnail(title: str, subtitle: str = None, output: str = None) -> str:
    """战斗型封面（用于战斗/高潮场景）"""
    gen = ThumbnailGenerator()
    return gen.generate(output or "action_thumb.png", title, subtitle, TemplateType.ACTION)


def make_ranking_thumbnail(rank: int, title: str, output: str = None) -> str:
    """排行型封面"""
    gen = ThumbnailGenerator()
    return gen.generate(
        output or f"rank{rank}_thumb.png",
        f"#{rank} {title}",
        template=TemplateType.RANKING,
        emoji=["👑", "⭐", "🎖️", "🏅", "🏅"][min(rank-1, 4)]
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="动漫封面生成工具")
    parser.add_argument("-t", "--title", required=True, help="主标题")
    parser.add_argument("-s", "--subtitle", help="副标题")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--template", default="shocking",
                        choices=["shocking", "emotional", "action", "romance", "news", "ranking"])
    parser.add_argument("-W", "--width", type=int, default=1280, help="宽度")
    parser.add_argument("--height", type=int, default=720, help="高度")
    args = parser.parse_args()

    gen = ThumbnailGenerator()
    result = gen.generate(
        args.output or "thumbnail.png",
        args.title, args.subtitle,
        template=args.template,
        size=(args.width, args.height)
    )
    print(f"封面已生成: {result}")
