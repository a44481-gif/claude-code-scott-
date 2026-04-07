# -*- coding: utf-8 -*-
"""
標籤管理工具 - 整理和分類所有文件、項目
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


class TagManager:
    """標籤管理系統"""

    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.db_file = self.base_dir / ".claude" / "tags_db.json"
        self.tags = self._load()

    def _load(self) -> Dict:
        """載入數據"""
        if self.db_file.exists():
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"files": {}, "tags": {}}

    def _save(self):
        """保存數據"""
        self.db_file.parent.mkdir(exist_ok=True)
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.tags, f, ensure_ascii=False, indent=2)

    def add_tag(self, file_path: str, tags: List[str]):
        """為文件添加標籤"""
        abs_path = str(Path(file_path).resolve())

        if abs_path not in self.tags["files"]:
            self.tags["files"][abs_path] = {
                "relative_path": str(Path(file_path).relative_to(self.base_dir)),
                "tags": [],
                "added_at": datetime.now().isoformat()
            }

        for tag in tags:
            if tag not in self.tags["files"][abs_path]["tags"]:
                self.tags["files"][abs_path]["tags"].append(tag)

            if tag not in self.tags["tags"]:
                self.tags["tags"][tag] = {"count": 0, "files": []}

            if abs_path not in self.tags["tags"][tag]["files"]:
                self.tags["tags"][tag]["count"] += 1
                self.tags["tags"][tag]["files"].append(abs_path)

        self._save()
        print(f"[OK] Tagged: {Path(file_path).name} with {tags}")

    def remove_tag(self, file_path: str, tags: List[str]):
        """移除標籤"""
        abs_path = str(Path(file_path).resolve())

        if abs_path in self.tags["files"]:
            for tag in tags:
                if tag in self.tags["files"][abs_path]["tags"]:
                    self.tags["files"][abs_path]["tags"].remove(tag)

                if tag in self.tags["tags"]:
                    if abs_path in self.tags["tags"][tag]["files"]:
                        self.tags["tags"][tag]["files"].remove(abs_path)
                        self.tags["tags"][tag]["count"] -= 1

            self._save()
            print(f"[OK] Tags removed from: {Path(file_path).name}")

    def search_by_tag(self, tag: str) -> List[str]:
        """按標籤搜索"""
        if tag in self.tags["tags"]:
            return self.tags["tags"][tag]["files"]
        return []

    def search_by_tags(self, tags: List[str], match_all: bool = False) -> List[str]:
        """按多個標籤搜索"""
        if not tags:
            return list(self.tags["files"].keys())

        results = []
        for file_path, data in self.tags["files"].items():
            file_tags = data["tags"]

            if match_all:
                if all(tag in file_tags for tag in tags):
                    results.append(file_path)
            else:
                if any(tag in file_tags for tag in tags):
                    results.append(file_path)

        return results

    def get_all_tags(self) -> Dict:
        """獲取所有標籤及計數"""
        return self.tags["tags"]

    def auto_tag_by_extension(self):
        """根據擴展名自動標籤"""
        extension_map = {
            ".pptx": ["ppt", "演示", "報告"],
            ".xlsx": ["excel", "數據", "表格"],
            ".pdf": ["pdf", "文檔"],
            ".json": ["json", "數據"],
            ".py": ["python", "腳本"],
            ".md": ["文檔", "說明"],
            ".txt": ["文本", "記錄"]
        }

        count = 0
        for ext, tags in extension_map.items():
            for file in self.base_dir.rglob(f"*{ext}"):
                abs_path = str(file.resolve())
                if abs_path not in self.tags["files"]:
                    self.add_tag(str(file), tags)
                    count += 1

        print(f"[OK] Auto-tagged {count} files")
        return count

    def generate_tag_report(self) -> str:
        """生成標籤報告"""
        report = []
        report.append("=" * 50)
        report.append("       Tag Management Report")
        report.append("=" * 50)
        report.append(f"Total Files: {len(self.tags['files'])}")
        report.append(f"Total Tags: {len(self.tags['tags'])}")
        report.append("")

        report.append("[Tag Statistics]")
        sorted_tags = sorted(self.tags["tags"].items(),
                           key=lambda x: x[1]["count"],
                           reverse=True)
        for tag, data in sorted_tags[:20]:
            report.append(f"  {tag}: {data['count']} files")

        return "\n".join(report)

    def print_report(self):
        """打印報告"""
        print(self.generate_tag_report())


def tag_files(directory: str, pattern: str = "*", tags: List[str] = None):
    """批量標籤文件"""
    manager = TagManager()

    if tags is None:
        tags = ["待整理"]

    count = 0
    for file in Path(directory).rglob(pattern):
        if file.is_file():
            manager.add_tag(str(file), tags)
            count += 1

    print(f"[OK] Tagged {count} files")
    return count


if __name__ == "__main__":
    import sys

    manager = TagManager()

    if len(sys.argv) < 2:
        manager.print_report()
    else:
        cmd = sys.argv[1]

        if cmd == "add":
            if len(sys.argv) > 3:
                file_path = sys.argv[2]
                tags = sys.argv[3].split(',')
                manager.add_tag(file_path, tags)
            else:
                print("Usage: python tag_manager.py add <file> <tag1,tag2,...>")

        elif cmd == "search":
            if len(sys.argv) > 2:
                results = manager.search_by_tag(sys.argv[2])
                print(f"Found {len(results)} files:")
                for f in results:
                    print(f"  - {Path(f).name}")

        elif cmd == "list":
            tags = manager.get_all_tags()
            print(f"Total tags: {len(tags)}")
            for tag, data in sorted(tags.items(), key=lambda x: x[1]['count'], reverse=True):
                print(f"  {tag}: {data['count']} files")

        elif cmd == "auto":
            manager.auto_tag_by_extension()

        elif cmd == "report":
            manager.print_report()

        else:
            print("Commands: add | search | list | auto | report")
