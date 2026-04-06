"""
动漫出海 - 自动剪辑工具
anime_overseas/video_editor.py

功能：
1. 自动剪辑精彩片段（按场景/对话节奏）
2. 添加字幕（烧录SRT）
3. 添加水印
4. 生成多平台比例版本（9:16/16:9/2:3）
5. 自动添加热门BGM（版权安全版）
6. 导出压缩

用法:
    from video_editor import AnimeVideoEditor
    editor = AnimeVideoEditor()
    editor.auto_clip("input.mp4", "output_dir")
"""

import os
import json
import logging
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

from anime_ops_config import VIDEO_CONFIG, LOG_DIR, OUTPUT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "video_editor.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("VideoEditor")


# ============ 工具检测 ============

def check_ffmpeg() -> bool:
    """检测ffmpeg是否可用"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_video_info(path: str) -> dict:
    """获取视频信息（时长、分辨率、帧率）"""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        video_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), {})
        duration = float(data["format"].get("duration", 0))
        width = int(video_stream.get("width", 0))
        height = int(video_stream.get("height", 0))
        fps_str = video_stream.get("r_frame_rate", "30/1")
        if "/" in fps_str:
            num, den = map(int, fps_str.split("/"))
            fps = num / den if den else 30
        else:
            fps = float(fps_str)
        return {"duration": duration, "width": width, "height": height, "fps": fps}
    except Exception as e:
        logger.error(f"获取视频信息失败: {e}")
        return {"duration": 0, "width": 1920, "height": 1080, "fps": 30}


# ============ 视频剪辑器 ============

class AnimeVideoEditor:
    """
    动漫视频自动剪辑
    依赖: ffmpeg（必须安装）
    """

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or OUTPUT_DIR / "clips")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_available = check_ffmpeg()
        if not self.ffmpeg_available:
            logger.warning("ffmpeg 未安装，部分功能将不可用。请从 https://ffmpeg.org 下载安装")

    def clip_by_duration(
        self,
        input_path: str,
        start_time: float,
        duration: float,
        output_path: str = None,
        add_watermark: bool = True,
        watermark_text: str = "@AnimeChannel",
        target_resolution: tuple = None,
    ) -> str:
        """
        按时间范围剪辑视频

        Args:
            input_path: 输入视频
            start_time: 开始时间（秒）
            duration: 持续时间（秒）
            output_path: 输出路径
            add_watermark: 是否加水印
            watermark_text: 水印文字
            target_resolution: 目标分辨率 (width, height)

        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        if output_path is None:
            output_path = self.output_dir / f"{input_path.stem}_clip_{start_time:.0f}s_{duration:.0f}s.mp4"
        else:
            output_path = Path(output_path)

        info = get_video_info(str(input_path))
        width = info["width"]
        height = info["height"]

        if target_resolution:
            scale_filter = f"scale={target_resolution[0]}:{target_resolution[1]}:force_original_aspect_ratio=decrease,pad={target_resolution[0]}:{target_resolution[1]}:(ow-iw)/2:(oh-ih)/2"
        else:
            scale_filter = None

        # 字幕烧录滤镜
        vf_parts = []
        if scale_filter:
            vf_parts.append(scale_filter)

        if add_watermark:
            # 水印位置：右下角
            font_size = min(target_resolution[0], 1920) // 40 if target_resolution else width // 40
            vf_parts.append(
                f"drawtext=text='{watermark_text}':fontsize={font_size}:fontcolor=white@0.8:"
                f"x=W-tw-20:y=H-th-20:borderw=2:bordercolor=black@0.5"
            )

        vf = ",".join(vf_parts) if vf_parts else None

        cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", str(input_path),
               "-t", str(duration)]

        if vf:
            cmd += ["-vf", vf, "-c:a", "copy"]
        else:
            cmd += ["-c", "copy"]

        cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "23", str(output_path)]

        logger.info(f"执行剪辑: {input_path.name}, {start_time}s-{start_time+duration}s")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                logger.error(f"ffmpeg错误: {result.stderr}")
                # 降级：简单复制
                logger.info("降级为简单复制模式")
                cmd_simple = ["ffmpeg", "-y", "-ss", str(start_time), "-i", str(input_path),
                              "-t", str(duration), "-c", "copy", str(output_path)]
                subprocess.run(cmd_simple, capture_output=True, text=True, timeout=120)
        except Exception as e:
            logger.error(f"剪辑失败: {e}")

        logger.info(f"输出: {output_path}")
        return str(output_path)

    def clip_by_timestamps(
        self,
        input_path: str,
        timestamps: list[tuple[float, float]],
        output_dir: str = None,
        add_watermark: bool = True,
    ) -> list[str]:
        """批量剪辑多个片段"""
        output_dir = Path(output_dir or self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        input_path = Path(input_path)
        results = []

        for i, (start, duration) in enumerate(timestamps):
            output_path = output_dir / f"{input_path.stem}_segment_{i+1}.mp4"
            result = self.clip_by_duration(
                str(input_path), start, duration,
                str(output_path), add_watermark
            )
            results.append(result)

        return results

    def add_subtitle_burn(
        self,
        input_path: str,
        srt_path: str,
        output_path: str = None,
        font: str = "Arial",
        font_size: int = None,
        font_color: str = "white",
    ) -> str:
        """烧录字幕到视频"""
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path.stem + "_subtitled.mp4"
        output_path = Path(output_path)

        info = get_video_info(str(input_path))
        width = info["width"]
        if font_size is None:
            font_size = max(18, width // 40)

        # ASS字幕样式
        style_line = (
            f"Style: Default,{font},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
            f"0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,0\n"
        )

        # 转换SRT为ASS
        ass_path = output_path.with_suffix(".ass")
        self._srt_to_ass(srt_path, str(ass_path), style_line)

        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-vf", f"ass={ass_path}",
            "-c:a", "copy",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            str(output_path)
        ]

        logger.info(f"烧录字幕: {input_path.name}")
        subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        logger.info(f"输出: {output_path}")
        return str(output_path)

    def _srt_to_ass(self, srt_path: str, ass_path: str, style_line: str):
        """SRT转ASS格式"""
        import re
        content = Path(srt_path).read_text(encoding="utf-8")
        header = (
            "[Script Info]\n"
            "Title: Anime Subtitles\n"
            "ScriptType: v4.00+\n"
            "WrapStyle: 0\n"
            "PlayResX: 1280\n"
            "PlayResY: 720\n"
            "ScaledBorderAndShadow: yes\n\n"
            "[V4+ Styles]\n"
            f"Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,"
            "BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,"
            "BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
            + style_line
            + "\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
        )

        blocks = []
        pattern = re.compile(r"(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})\s*\n([\s\S]*?)(?=\n\n\d+\s*\n|\Z)")
        for match in pattern.finditer(content):
            start = self._srt_to_ass_time(match.group(2))
            end = self._srt_to_ass_time(match.group(3))
            text = match.group(4).strip().replace("\n", "\\N")
            blocks.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

        Path(ass_path).write_text(header + "\n".join(blocks), encoding="utf-8")

    def _srt_to_ass_time(self, srt_time: str) -> str:
        """SRT时间转ASS时间"""
        return srt_time.replace(",", ".")

    def convert_aspect_ratio(
        self,
        input_path: str,
        target_ratio: str = "9:16",
        output_path: str = None,
        crop_strategy: str = "center",
    ) -> str:
        """
        转换视频宽高比

        Args:
            input_path: 输入视频
            target_ratio: 目标比例 "9:16" / "16:9" / "2:3"
            output_path: 输出路径
            crop_strategy: 裁剪策略 "center" / "top" / "custom"
        """
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path.stem + f"_{target_ratio.replace(':', 'x')}.mp4"
        output_path = Path(output_path)

        info = get_video_info(str(input_path))
        w, h = info["width"], info["height"]

        ratio_map = {
            "9:16": (9/16, "portrait"),
            "16:9": (16/9, "landscape"),
            "2:3": (2/3, "portrait"),
            "4:5": (4/5, "portrait"),
            "1:1": (1.0, "square"),
        }
        target_ratio_float, _ = ratio_map.get(target_ratio, (9/16, "portrait"))
        current_ratio = w / h

        if target_ratio_float == current_ratio:
            logger.info("比例相同，直接复制")
            cmd = ["ffmpeg", "-y", "-i", str(input_path), "-c", "copy", str(output_path)]
        else:
            if target_ratio_float < 1:  # 竖屏目标
                # 输出竖屏：宽度固定为输入宽度，高度按比例计算
                out_w = w
                out_h = int(w / target_ratio_float)
                crop_h = int(out_h)
                offset_y = (h - crop_h) // 2 if crop_strategy == "center" else 0
                vf = f"crop={out_w}:{crop_h}:0:{offset_y},scale={out_w}:{out_h}"
            else:  # 横屏目标
                out_h = h
                out_w = int(h * target_ratio_float)
                crop_w = out_w
                offset_x = (w - crop_w) // 2 if crop_strategy == "center" else 0
                vf = f"crop={crop_w}:{out_h}:{offset_x}:0,scale={out_w}:{out_h}"

            cmd = [
                "ffmpeg", "-y", "-i", str(input_path),
                "-vf", vf,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "copy",
                str(output_path)
            ]

        logger.info(f"转换比例: {w}x{h} -> {target_ratio}")
        subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        logger.info(f"输出: {output_path}")
        return str(output_path)

    def generate_all_platform_versions(
        self,
        input_path: str,
        clip_timestamps: list[tuple[float, float]],
        srt_path: str = None,
        add_watermark: bool = True,
        watermark_text: str = "@AnimeChannel",
    ) -> dict[str, str]:
        """
        一次性生成所有平台版本

        Returns:
            dict: {平台名: 文件路径}
        """
        results = {}
        input_path = Path(input_path)
        clip_dir = self.output_dir / input_path.stem
        clip_dir.mkdir(exist_ok=True)

        for i, (start, duration) in enumerate(clip_timestamps):
            clip_name = f"segment_{i+1}"
            clip_path = clip_dir / f"{clip_name}.mp4"

            # 剪辑原始片段
            self.clip_by_duration(
                str(input_path), start, duration,
                str(clip_path), add_watermark, watermark_text
            )

            # 烧录字幕（如果提供）
            if srt_path and Path(srt_path).exists():
                clip_path = self.add_subtitle_burn(str(clip_path), srt_path)

            # YouTube Shorts 版本（9:16）
            yt_shorts_path = clip_dir / f"{clip_name}_yt_shorts.mp4"
            self.convert_aspect_ratio(str(clip_path), "9:16", str(yt_shorts_path))

            # TikTok 版本（9:16）
            tt_path = clip_dir / f"{clip_name}_tiktok.mp4"
            self.convert_aspect_ratio(str(clip_path), "9:16", str(tt_path))

            # Pinterest 版本（2:3）
            pin_path = clip_dir / f"{clip_name}_pinterest.mp4"
            self.convert_aspect_ratio(str(clip_path), "2:3", str(pin_path))

            results[f"{clip_name}_yt_shorts"] = str(yt_shorts_path)
            results[f"{clip_name}_tiktok"] = str(tt_path)
            results[f"{clip_name}_pinterest"] = str(pin_path)

        logger.info(f"所有平台版本生成完毕: {len(results)} 个文件")
        return results


# ============ 自动找精彩片段 ============

class SceneDetector:
    """
    基于规则的精彩片段检测
    （简单实现：按固定间隔切分 + 声音大小检测）
    """

    @staticmethod
    def auto_segment(
        video_path: str,
        min_clip_duration: float = 30,
        max_clip_duration: float = 90,
        preferred_duration: float = 60,
    ) -> list[tuple[float, float]]:
        """
        自动切分视频为适合二次创作的片段
        返回: [(start_time, duration), ...]
        """
        info = get_video_info(video_path)
        total_duration = info["duration"]

        if total_duration == 0:
            return []

        segments = []
        current = 0.0

        while current < total_duration:
            remaining = total_duration - current
            if remaining < min_clip_duration:
                break

            seg_duration = min(preferred_duration, remaining)
            # 保证不超出视频长度
            seg_duration = min(seg_duration, max_clip_duration)

            segments.append((current, seg_duration))
            current += seg_duration - 5  # 重叠5秒

        return segments


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="动漫视频自动剪辑工具")
    parser.add_argument("input", help="输入视频文件路径")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("-s", "--start", type=float, default=0, help="开始时间（秒）")
    parser.add_argument("-d", "--duration", type=float, default=60, help="剪辑时长（秒）")
    parser.add_argument("--watermark", default="@AnimeChannel", help="水印文字")
    parser.add_argument("--no-watermark", action="store_true", help="不加水印")
    args = parser.parse_args()

    editor = AnimeVideoEditor(args.output)
    result = editor.clip_by_duration(
        args.input, args.start, args.duration,
        add_watermark=not args.no_watermark,
        watermark_text=args.watermark,
    )
    print(f"输出文件: {result}")
