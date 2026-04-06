#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 自动提交脚本 - 每日定时同步到 GitHub
每天 03:00 和 15:00 自动执行
"""

import os
import subprocess
import sys
from datetime import datetime

# 项目根目录
PROJECT_DIR = r"d:\claude mini max 2.7"
LOG_FILE = os.path.join(os.path.dirname(__file__), "auto_commit.log")


def log(msg: str):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run(cmd: list, cwd: str = None) -> tuple:
    """执行命令"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def main():
    log("=" * 50)
    log("开始自动 Git 同步")

    # 切换到项目目录
    os.chdir(PROJECT_DIR)

    # 1. 检查 git 状态
    log("检查 Git 状态...")
    code, out, err = run(["git", "status", "--porcelain"])
    if code != 0:
        log(f"Git 状态检查失败: {err}")
        sys.exit(1)

    changes = out.strip()
    if not changes:
        log("没有文件变更，跳过提交")
        return

    # 2. 添加所有变更
    log("添加所有变更...")
    code, out, err = run(["git", "add", "-A"])
    if code != 0:
        log(f"Git add 失败: {err}")
        sys.exit(1)

    # 3. 获取变更文件数量
    code, out, _ = run(["git", "status", "--porcelain"])
    file_count = len([l for l in out.strip().split("\n") if l])

    # 4. 提交
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Auto-sync: {timestamp} ({file_count} files updated)"
    log(f"提交: {commit_msg}")
    code, out, err = run(["git", "commit", "-m", commit_msg])
    if code != 0:
        log(f"Git commit 失败: {err}")
        sys.exit(1)

    # 5. 推送到 GitHub
    log("推送到 GitHub...")
    code, out, err = run(["git", "push", "origin", "main"])
    if code != 0:
        log(f"Git push 失败: {err}")
        sys.exit(1)

    log(f"✅ 同步成功！{file_count} 个文件已更新到 GitHub")
    log("=" * 50)


if __name__ == "__main__":
    main()
