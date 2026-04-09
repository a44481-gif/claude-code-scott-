#!/usr/bin/env python3
"""
GlobalOPS · 数据迁移脚本
将 manhua-system 的 batch_60_sets.json 内容迁移到 PostgreSQL
"""

import json
import sys
import os
from pathlib import Path

# 添加 python_engine 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "python_engine"))

from src.db_client import DBClient

MANHUA_CONTENT = Path(__file__).parent.parent.parent / "manhua-system" / "content" / "batch_60_sets.json"

def load_legacy_content():
    if not MANHUA_CONTENT.exists():
        print(f"❌ 源文件不存在: {MANHUA_CONTENT}")
        return []

    with open(MANHUA_CONTENT, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 兼容不同格式
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "contents" in data:
        return data["contents"]
    if isinstance(data, dict) and "sets" in data:
        return data["sets"]
    print(f"❌ 未知 JSON 格式，keys: {list(data.keys())}")
    return []


def detect_theme(content: dict) -> str:
    """从内容推断题材"""
    topic = content.get("topic", "") or content.get("标题", "") or content.get("title", "")
    themes = ["龙王", "逆袭", "虐渣", "重生", "神医", "系统"]
    for t in themes:
        if t in topic or t in content.get("theme_type", ""):
            return t
    return "龙王"


def migrate():
    print(f"\n🔄 开始迁移数据...")
    print(f"   源文件: {MANHUA_CONTENT}")

    items = load_legacy_content()
    if not items:
        print("⚠️  没有找到可迁移的内容")
        return

    print(f"   发现 {len(items)} 条内容")

    db = DBClient()
    migrated = 0
    skipped = 0

    for item in items:
        try:
            # 提取字段（兼容多种格式）
            topic = item.get("topic") or item.get("标题") or item.get("title", "未知")
            theme = detect_theme(item)
            title = item.get("title") or item.get("标题") or item.get("caption", "")
            caption = item.get("caption") or item.get("文案") or item.get("description", "")
            tags = item.get("tags") or item.get("标签", [])
            cta = item.get("cta") or item.get("cta_text", "❤️ Like + Follow for Part 2")
            script = item.get("script") or item.get("脚本", "")

            content_id = f"mig_{item.get('id', migrated+1):04d}"

            db.insert_content({
                "content_id": content_id,
                "theme_type": theme,
                "topic": topic,
                "title": str(title),
                "caption": str(caption),
                "script_6panel": json.dumps({"原始": script}, ensure_ascii=False),
                "tags": tags if isinstance(tags, list) else [str(t) for t in str(tags).split(",")],
                "cta_text": str(cta),
                "target_lang": "en",
                "target_region": "southeast_asia",
                "status": "pending",
                "copyright_risk": "medium",
                "priority": 5,
            })
            migrated += 1
            print(f"  ✅ {content_id} [{theme}] {topic[:30]}...")

        except Exception as e:
            skipped += 1
            print(f"  ❌ 跳过: {e}")

    db.close()
    print(f"\n✅ 迁移完成！迁移: {migrated} | 跳过: {skipped}")


if __name__ == "__main__":
    migrate()
