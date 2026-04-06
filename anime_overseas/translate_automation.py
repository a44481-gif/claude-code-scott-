"""
动漫出海 - 批量字幕翻译自动化脚本
anime_overseas/translate_automation.py

功能：
1. 批量翻译字幕文件（SRT格式）
2. 支持多语言（英/印尼/越/泰/阿/西/葡）
3. 翻译缓存，避免重复翻译
4. 字幕本地化（时间轴保持）
5. 翻译质量分级（快速/标准/专业）

用法:
    from translate_automation import Translator
    t = Translator(target_lang="id")
    t.translate_srt("input.srt", "output_id.srt")
"""

import re
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# 可选依赖检查
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import deepl
    DEEPL_AVAILABLE = True
except ImportError:
    DEEPL_AVAILABLE = False

try:
    from googletrans import Translator as GoogleTranslator
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from anime_ops_config import TRANSLATION, LOG_DIR, OUTPUT_DIR

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "translate.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("Translator")


# ============ SRT 解析工具 ============

def parse_srt(content: str) -> list[dict]:
    """解析SRT字幕文件"""
    blocks = []
    pattern = re.compile(r"(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})\s*\n([\s\S]*?)(?=\n\n\d+\s*\n|\Z)")
    for match in pattern.finditer(content):
        blocks.append({
            "index": int(match.group(1)),
            "start": match.group(2),
            "end": match.group(3),
            "text": match.group(4).strip(),
        })
    return blocks


def build_srt(blocks: list[dict]) -> str:
    """重建SRT字幕文件"""
    lines = []
    for block in blocks:
        lines.append(str(block["index"]))
        lines.append(f"{block['start']} --> {block['end']}")
        lines.append(block["text"])
        lines.append("")
    return "\n".join(lines)


# ============ 翻译引擎 ============

class TranslationEngine:
    def __init__(self, provider: str = None, api_key: str = None):
        self.provider = provider or TRANSLATION["provider"]
        self.api_key = api_key
        self._init_client()

    def _init_client(self):
        if self.provider == "openai" and OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI 翻译引擎已初始化")
        elif self.provider == "deepl" and DEEPL_AVAILABLE and self.api_key:
            self.client = deepl.Translator(self.api_key)
            logger.info("DeepL 翻译引擎已初始化")
        elif self.provider == "google" or GOOGLE_AVAILABLE:
            self.client = GoogleTranslator()
            logger.info("Google Translate 翻译引擎已初始化")
        else:
            self.client = None
            logger.warning("未配置翻译引擎，将使用占位翻译")

    def translate(self, text: str, target_lang: str, source_lang: str = "zh") -> str:
        """翻译单段文本"""
        if not text.strip():
            return text
        if self.client is None:
            return f"[{target_lang}] {text}"

        try:
            if self.provider == "openai":
                return self._translate_openai(text, target_lang, source_lang)
            elif self.provider == "deepl":
                return self._translate_deepl(text, target_lang, source_lang)
            else:
                return self._translate_google(text, target_lang, source_lang)
        except Exception as e:
            logger.error(f"翻译失败: {e}, 原文: {text[:50]}")
            return f"[ERR:{target_lang}] {text}"

    def _translate_openai(self, text: str, target_lang: str, source_lang: str) -> str:
        lang_map = {"en": "English", "id": "Indonesian", "vi": "Vietnamese",
                    "th": "Thai", "ar": "Arabic", "es": "Spanish", "pt": "Portuguese"}
        lang_name = lang_map.get(target_lang, target_lang)

        system_prompt = f"""You are a professional anime subtitle translator.
Translate the following Chinese subtitle text to {lang_name}.
Rules:
- Keep it natural and conversational
- Use appropriate slang for the target language
- Keep any sound effects (like 哈哈哈, 啊啊啊) as-is
- Keep any on-screen text as-is
- Preserve the original emotion and tone
- If it's dialogue, keep it natural; if it's narration, keep it formal
- Keep any exclamation marks and emphasis
Return ONLY the translated text, nothing else."""

        response = self.client.chat.completions.create(
            model=TRANSLATION["openai_model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()

    def _translate_deepl(self, text: str, target_lang: str, source_lang: str) -> str:
        lang_code_map = {
            "en": "EN-US", "id": "ID", "vi": "VI", "th": "TH",
            "ar": "AR", "es": "ES", "pt": "PT-BR"
        }
        target = lang_code_map.get(target_lang, "EN-US")
        result = self.client.translate_text(text, target_lang=target, source_lang="ZH")
        return result.text

    def _translate_google(self, text: str, target_lang: str, source_lang: str) -> str:
        return self.client.translate(text, src="zh-cn", dest=target_lang).text


# ============ 字幕翻译器 ============

class SubtitleTranslator:
    """批量字幕翻译"""

    def __init__(self, target_lang: str, provider: str = None, api_key: str = None,
                 quality: str = "standard"):
        self.target_lang = target_lang
        self.engine = TranslationEngine(provider, api_key)
        self.quality = quality
        self.cache_file = OUTPUT_DIR / f"translation_cache_{target_lang}.json"
        self.cache = self._load_cache()
        self.stats = {"total": 0, "cached": 0, "translated": 0, "errors": 0}

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except:
                return {}
        return {}

    def _save_cache(self):
        try:
            self.cache_file.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"缓存保存失败: {e}")

    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(f"{self.target_lang}:{text}".encode()).hexdigest()

    def _translate_line(self, text: str, source_lang: str = "zh") -> str:
        if not text.strip():
            return text

        cache_key = self._get_cache_key(text)
        if cache_key in self.cache:
            self.stats["cached"] += 1
            return self.cache[cache_key]

        self.stats["total"] += 1
        result = self.engine.translate(text, self.target_lang, source_lang)
        self.cache[cache_key] = result
        self.stats["translated"] += 1

        if self.stats["translated"] % 20 == 0:
            self._save_cache()
            logger.info(f"已翻译 {self.stats['translated']} 条，进度保存")

        return result

    def translate_srt(self, input_path: str, output_path: str = None,
                      source_lang: str = "zh") -> str:
        """翻译SRT字幕文件"""
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path.stem + f"_{self.target_lang}.srt"
        output_path = Path(output_path)

        logger.info(f"开始翻译字幕: {input_path} -> {output_path}")
        logger.info(f"目标语言: {self.target_lang}, 质量等级: {self.quality}")

        content = input_path.read_text(encoding="utf-8")
        blocks = parse_srt(content)

        for block in blocks:
            original_text = block["text"]
            # 处理多行字幕
            lines = original_text.split("\n")
            translated_lines = [self._translate_line(line, source_lang) for line in lines]
            block["text"] = "\n".join(translated_lines)

            if self.stats["total"] % 10 == 0:
                time.sleep(0.1)  # 防止API限流

        output_content = build_srt(blocks)
        output_path.write_text(output_content, encoding="utf-8")

        self._save_cache()
        logger.info(f"翻译完成! 总计: {len(blocks)} 条, 缓存命中: {self.stats['cached']}, 新翻译: {self.stats['translated']}")
        return str(output_path)

    def batch_translate(self, input_dir: str, output_dir: str = None,
                        extensions: tuple = (".srt", ".vtt", ".txt")) -> list[str]:
        """批量翻译目录下所有字幕文件"""
        input_dir = Path(input_dir)
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        else:
            output_dir = input_dir

        results = []
        for ext in extensions:
            for file in input_dir.glob(f"*{ext}"):
                output_path = output_dir / f"{file.stem}_{self.target_lang}{file.suffix}"
                try:
                    result = self.translate_srt(str(file), str(output_path))
                    results.append(result)
                except Exception as e:
                    logger.error(f"翻译失败 {file}: {e}")

        return results


# ============ 字幕本地化增强 ============

class SubtitleLocalizer:
    """字幕本地化增强：添加名称标注、术语表、语速调整"""

    def __init__(self, target_lang: str):
        self.target_lang = target_lang
        # 动漫术语表
        self.term_glossary = self._build_glossary()

    def _build_glossary(self) -> dict:
        glossaries = {
            "en": {
                "斗罗大陆": "Douluo Dalu (Soul Land)",
                "魂师": "Soul Master",
                "魂环": "Soul Ring",
                "魂骨": "Soul Bone",
                "武魂": "Martial Soul",
                "斗破苍穹": "Battle Through the Heavens",
                "斗气": "Battle Qi",
                "萧炎": "Xiao Yan",
                "筑基": "Foundation Building",
                "金丹": "Golden Core",
                "元婴": "Yuan Ying",
                "凡人修仙传": "A Record of a Mortal's Journey to Immortality",
                "修仙": "Cultivation",
                "修仙者": "Cultivator",
            },
            "id": {
                "斗罗大陆": "Douluo Dalu (Tanah Jiwa)",
                "斗破苍穹": "Battle Through the Heavens",
                "凡人修仙传": "Kisah Pendeta Abadi",
                "修仙": "Kultivasi",
                "魂师": "Guru Jiwa",
            },
            "es": {
                "斗罗大陆": "Douluo Dalu (Tierra de Almas)",
                "斗破苍穹": "Batalla a Través de los Cielos",
                "凡人修仙传": "Viaje Inmortal",
                "修仙": "Cultivación",
            },
        }
        return glossaries.get(self.target_lang, {})

    def apply_glossary(self, text: str) -> str:
        """应用术语表"""
        for cn, local in self.term_glossary.items():
            if cn in text:
                text = text.replace(cn, f"{cn} ({local})")
        return text

    def add_title_card(self, blocks: list[dict], title: str, start_time: str = "00:00:00,000") -> list[dict]:
        """在字幕开头添加标题卡"""
        title_card = {
            "index": 0,
            "start": start_time,
            "end": "00:00:05,000",
            "text": title
        }
        return [title_card] + blocks

    def add_ending_card(self, blocks: list[dict], text: str, duration: int = 5) -> list[dict]:
        """在字幕末尾添加结尾卡（订阅引导等）"""
        last_block = blocks[-1]
        end_time = self._add_seconds(last_block["end"], duration)
        ending_card = {
            "index": len(blocks) + 1,
            "start": last_block["end"],
            "end": end_time,
            "text": text
        }
        return blocks + [ending_card]

    def _add_seconds(self, time_str: str, seconds: int) -> str:
        """给时间字符串加秒数"""
        match = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", time_str)
        if not match:
            return time_str
        h, m, s, ms = map(int, match.groups())
        total_ms = h * 3600000 + m * 60000 + s * 1000 + ms + seconds * 1000
        new_h = total_ms // 3600000
        total_ms %= 3600000
        new_m = total_ms // 60000
        total_ms %= 60000
        new_s = total_ms // 1000
        new_ms = total_ms %  1000
        return f"{new_h:02d}:{new_m:02d}:{new_s:02d},{new_ms:03d}"


# ============ 主函数 ============

def translate_and_localize(
    input_srt: str,
    target_lang: str,
    anime_name: str,
    channel_name: str = "@YourChannel",
    output_path: str = None,
    add_subscription_prompt: bool = True,
    quality: str = "standard",
) -> str:
    """
    一站式字幕翻译+本地化

    Args:
        input_srt: 输入字幕文件路径
        target_lang: 目标语言代码
        anime_name: 动漫名称（用于术语表）
        channel_name: 频道名（用于结尾引导）
        output_path: 输出路径（None则自动生成）
        add_subscription_prompt: 是否添加订阅引导
        quality: 翻译质量（fast/standard/professional）

    Returns:
        输出文件路径
    """
    translator = SubtitleTranslator(target_lang, quality=quality)
    localizer = SubtitleLocalizer(target_lang)

    # 1. 翻译
    output_file = output_path or str(OUTPUT_DIR / f"{Path(input_srt).stem}_{target_lang}.srt")
    translator.translate_srt(input_srt, output_file)

    # 2. 读取翻译结果并增强
    blocks = parse_srt(Path(output_file).read_text(encoding="utf-8"))

    # 应用术语表
    for block in blocks:
        block["text"] = localizer.apply_glossary(block["text"])

    # 添加标题卡
    subscription_texts = {
        "en": "SUBSCRIBE for More Anime! 🔔",
        "id": "SUBSCRIBE untuk Anime Lainnya! 🔔",
        "vi": "ĐĂNG KÝ để xem thêm Anime! 🔔",
        "th": "SUBSCRIBE เพื่อดูอนิเมะอื่นๆ! 🔔",
        "ar": "اشترك لمشاهدة المزيد! 🔔",
        "es": "¡SUSCRÍBETE para más Anime! 🔔",
        "pt": "INSCREVA-SE para mais Anime! 🔔",
    }
    sub_text = subscription_texts.get(target_lang, subscription_texts["en"])

    blocks = localizer.add_title_card(blocks, anime_name)
    if add_subscription_prompt:
        blocks = localizer.add_ending_card(blocks, sub_text)

    # 3. 保存
    output_content = build_srt(blocks)
    Path(output_file).write_text(output_content, encoding="utf-8")

    logger.info(f"本地化完成: {output_file}")
    logger.info(f"统计 - 缓存: {translator.stats['cached']}, 新翻译: {translator.stats['translated']}")
    return output_file


# ============ 成本估算 ============

def estimate_translation_cost(char_count: int, provider: str = "openai") -> dict:
    """估算翻译成本"""
    if provider == "openai":
        cost_per_char = TRANSLATION["openai_cost_per_1k_chars"] / 1000
        cost = char_count * cost_per_char
    else:
        cost = 0  # DeepL/Google按用量计费

    return {
        "字符数": char_count,
        "提供商": provider,
        "预估成本（美元）": round(cost, 4),
        "参考报价（美元/千字）": 15 if provider == "openai" else 20,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="动漫字幕翻译工具")
    parser.add_argument("input", help="输入SRT文件路径")
    parser.add_argument("-l", "--lang", default="en", choices=["en", "id", "vi", "th", "ar", "es", "pt"],
                        help="目标语言")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-q", "--quality", default="standard", choices=["fast", "standard", "professional"])
    args = parser.parse_args()

    result = translate_and_localize(
        args.input, args.lang, "Anime",
        output_path=args.output, quality=args.quality
    )
    print(f"\n输出文件: {result}")
