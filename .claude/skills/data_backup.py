# -*- coding: utf-8 -*-
"""
數據備份工具 - 自動備份重要文件到多個位置
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class DataBackup:
    """數據備份工具"""

    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # 備份配置
        self.config_file = self.backup_dir / "backup_config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """載入配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默認配置
        return {
            "include_patterns": ["*.pptx", "*.xlsx", "*.json", "*.md"],
            "exclude_patterns": ["node_modules", "__pycache__", ".git"],
            "backup_history": []
        }

    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def backup_file(self, file_path: str, description: str = "") -> str:
        """備份單個文件"""
        src = Path(file_path)
        if not src.exists():
            print(f"[ERROR] File not found: {file_path}")
            return None

        # 生成備份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{src.stem}_{timestamp}{src.suffix}"
        backup_path = self.backup_dir / backup_name

        # 複製文件
        shutil.copy2(src, backup_path)

        # 記錄歷史
        record = {
            "original": str(src),
            "backup": str(backup_path),
            "description": description,
            "timestamp": timestamp,
            "size": os.path.getsize(src)
        }
        self.config["backup_history"].append(record)
        self._save_config()

        print(f"[OK] Backed up: {src.name} -> {backup_path.name}")
        return str(backup_path)

    def backup_directory(self, dir_path: str, pattern: str = "*.pptx") -> str:
        """備份目錄中符合規則的文件"""
        directory = Path(dir_path)
        if not directory.exists():
            print(f"[ERROR] Directory not found: {dir_path}")
            return None

        # 生成zip文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_name = f"{directory.name}_backup_{timestamp}.zip"
        zip_path = self.backup_dir / zip_name

        # 創建zip
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            count = 0
            for pattern in self.config["include_patterns"]:
                for file in directory.rglob(pattern):
                    # 檢查是否在排除名單
                    if any(ex in str(file) for ex in self.config["exclude_patterns"]):
                        continue
                    zipf.write(file, file.relative_to(directory))
                    count += 1

        print(f"[OK] Directory backup: {count} files -> {zip_path.name}")
        return str(zip_path)

    def restore_file(self, backup_name: str, restore_path: str = None) -> bool:
        """恢復文件"""
        backup_file = self.backup_dir / backup_name
        if not backup_file.exists():
            print(f"[ERROR] Backup not found: {backup_name}")
            return False

        if restore_path is None:
            restore_path = backup_name.split('_')[0] + Path(backup_name).suffix

        shutil.copy2(backup_file, restore_path)
        print(f"[OK] Restored: {backup_name} -> {restore_path}")
        return True

    def list_backups(self) -> List[Dict]:
        """列出所有備份"""
        backups = []
        for f in sorted(self.backup_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file():
                backups.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
        return backups

    def get_backup_stats(self) -> Dict:
        """獲取備份統計"""
        backups = self.list_backups()
        total_size = sum(b["size"] for b in backups)

        return {
            "total_backups": len(backups),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "latest_backup": backups[0]["modified"] if backups else None
        }

    def print_status(self):
        """打印狀態"""
        stats = self.get_backup_stats()
        backups = self.list_backups()

        print("\n" + "=" * 50)
        print("       Backup Status")
        print("=" * 50)
        print(f"Total Backups: {stats['total_backups']}")
        print(f"Total Size: {stats['total_size_mb']} MB")
        print(f"Latest Backup: {stats['latest_backup'] or 'None'}")
        print("\nRecent Backups:")
        for b in backups[:10]:
            size_kb = round(b["size"] / 1024, 1)
            print(f"  - {b['name']} ({size_kb} KB)")
        print("=" * 50)


def quick_backup(file_or_dir: str, description: str = "") -> str:
    """快速備份"""
    backup = DataBackup()

    path = Path(file_or_dir)
    if path.is_file():
        return backup.backup_file(file_or_dir, description)
    elif path.is_dir():
        return backup.backup_directory(file_or_dir)
    else:
        print(f"[ERROR] Invalid path: {file_or_dir}")
        return None


if __name__ == "__main__":
    import sys

    backup_tool = DataBackup()

    if len(sys.argv) < 2:
        backup_tool.print_status()
    else:
        cmd = sys.argv[1]

        if cmd == "backup":
            if len(sys.argv) > 2:
                quick_backup(sys.argv[2])
            else:
                print("Usage: python data_backup.py backup <file_or_dir>")

        elif cmd == "list":
            backups = backup_tool.list_backups()
            for b in backups:
                print(f"  {b['name']}")

        elif cmd == "status":
            backup_tool.print_status()

        elif cmd == "restore":
            if len(sys.argv) > 2:
                backup_tool.restore_file(sys.argv[2])
            else:
                print("Usage: python data_backup.py restore <backup_name>")

        else:
            print("Commands: backup | list | status | restore")
