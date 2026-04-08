"""
动漫出海运营 · 定時自動化腳本
anime_overseas/scheduler_ops.py

設置 Windows 定時任務，全天候自動化運營

用法:
    python scheduler_ops.py setup    # 設置定時任務
    python scheduler_ops.py status   # 查看任務狀態
    python scheduler_ops.py stop     # 停止所有任務
    python scheduler_ops.py run-now  # 立即運行一次
"""

import sys
import io
import subprocess
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)

WORKSPACE = Path(__file__).parent
AGENT_PY = WORKSPACE / "agent.py"
TASK_NAME = "AnimeOpsDaily"
LOG_DIR = WORKSPACE / "logs"
LOG_DIR.mkdir(exist_ok=True)

TASKS = [
    {
        "name": "AnimeOps_Daily_Report",
        "schedule": "daily 09:00",
        "command": f'python "{AGENT_PY}" daily',
        "description": "每日運營報告 + 待辦清單"
    },
    {
        "name": "AnimeOps_Batch_Morning",
        "schedule": "daily 08:00",
        "command": f'python "{AGENT_PY}" batch',
        "description": "早上8點：下載+剪輯+封面，準備當天內容"
    },
    {
        "name": "AnimeOps_Batch_Evening",
        "schedule": "daily 19:00",
        "command": f'python "{AGENT_PY}" batch',
        "description": "晚上7點：第二次批量準備"
    },
    {
        "name": "AnimeOps_Revenue_Weekly",
        "schedule": "weekly Monday 10:00",
        "command": f'python "{AGENT_PY}" revenue',
        "description": "每週一：收益報告"
    },
]


def get_log(name: str) -> str:
    return str(LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log")


AGENT_PY = WORKSPACE / "agent.py"
TASK_NAME = "AnimeOpsDaily"
LOG_DIR = WORKSPACE / "logs"
LOG_DIR.mkdir(exist_ok=True)

def get_log(name: str) -> str:
    return str(LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

def _quote(s):
    return f'"{s}"'

def cmd_setup():
    """設置定時任務"""
    print("設置動漫出海運營定時任務...\n")

    for task in TASKS:
        name = task["name"]
        desc = task["description"]
        sched_type, sched_time = task["schedule"].split(" ", 1)
        py_path = sys.executable

        log_str = _quote(get_log(name))
        del log_str  # not used in task runner

        if sched_type == "daily":
            trigger = f"/sc DAILY /st {sched_time}"
        elif sched_type == "weekly":
            day, time = sched_time.split(" ")
            trigger = f"/sc WEEKLY /d {day} /st {time}"
        else:
            trigger = "/sc DAILY /st 09:00"

        py_arg = '"' + str(AGENT_PY) + '"'
        create_cmd = (
            f'schtasks /create /tn "{name}" {trigger} '
            f'/tr "cmd /c {py_path} {py_arg} daily" '
            f'/f /rl HIGHEST'
        )

        r = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)

        if r.returncode == 0:
            print(f"  [OK] {name}")
            print(f"       時間: {task['schedule']}")
            print(f"       任務: {desc}")
        else:
            print(f"  [FAIL] {name}: {r.stderr.strip()[:100] or r.stdout.strip()[:100]}")
        print()

    print("=" * 60)
    print("定時任務設置完成！")
    print("查看任務狀態: python scheduler_ops.py status")
    print("停止任務: python scheduler_ops.py stop")


def cmd_status():
    """查看任務狀態"""
    print("\n動漫出海運營 · 任務狀態")
    print("=" * 60)

    for task in TASKS:
        name = task["name"]
        r = subprocess.run(
            f'schtasks /query /tn "{name}"',
            shell=True, capture_output=True, text=True
        )
        status = "已設置" if r.returncode == 0 else "未設置"
        print(f"  {name}: {status}")
        print(f"    {task['schedule']} | {task['description']}")

    print()
    # 內容庫存
    clips = list((WORKSPACE / "youtube_uploads/clips").glob("*.mp4"))
    thumbs = list((WORKSPACE / "youtube_uploads/thumbnails").glob("cover_*.png"))
    print(f"內容庫存: {len(clips)} 個視頻剪輯 | {len(thumbs)} 張封面")
    print()


def cmd_stop():
    """停止所有任務"""
    print("停止所有定時任務...")
    for task in TASKS:
        name = task["name"]
        r = subprocess.run(
            f'schtasks /delete /tn "{name}" /f',
            shell=True, capture_output=True
        )
        status = "已停止" if r.returncode == 0 else f"失敗({r.returncode})"
        print(f"  {name}: {status}")


def cmd_run_now():
    """立即運行一次"""
    print("立即運行動漫出海運營代理...\n")
    r = subprocess.run(
        [sys.executable, str(AGENT_PY), "batch"],
        cwd=str(WORKSPACE)
    )
    print(f"\n完成，返回碼: {r.returncode}")


def main():
    args = sys.argv[1:]
    cmd = args[0].lower() if args else "status"

    if cmd == "setup":
        cmd_setup()
    elif cmd == "status":
        cmd_status()
    elif cmd == "stop":
        cmd_stop()
    elif cmd == "run-now":
        cmd_run_now()
    elif cmd == "run":
        cmd_run_now()
    else:
        print(f"用法: python scheduler_ops.py [setup|status|stop|run-now]")


if __name__ == "__main__":
    main()
