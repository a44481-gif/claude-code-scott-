# -*- coding: utf-8 -*-
"""
會議管理工具 - 安排和追蹤會議
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class MeetingManager:
    """會議管理系統"""

    def __init__(self, db_path="meetings.json"):
        self.db_path = db_path
        self.meetings = self._load()

    def _load(self) -> List[Dict]:
        """載入數據"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save(self):
        """保存數據"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.meetings, f, ensure_ascii=False, indent=2)

    def schedule_meeting(self, title: str, date: str, time: str,
                        duration: int = 60, attendees: List[str] = None,
                        location: str = "", notes: str = "") -> Dict:
        """安排會議"""
        meeting = {
            "id": len(self.meetings) + 1,
            "title": title,
            "date": date,
            "time": time,
            "duration": duration,  # 分鐘
            "attendees": attendees or [],
            "location": location,
            "notes": notes,
            "status": "scheduled",  # scheduled, completed, cancelled
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.meetings.append(meeting)
        self._save()
        print(f"[OK] Meeting scheduled: {title}")
        return meeting

    def get_upcoming(self, days: int = 7) -> List[Dict]:
        """獲取即將到來的會議"""
        upcoming = []
        today = datetime.now().date()

        for meeting in self.meetings:
            if meeting["status"] != "scheduled":
                continue

            try:
                meet_date = datetime.strptime(meeting["date"], "%Y-%m-%d").date()
                if today <= meet_date <= today + timedelta(days=days):
                    upcoming.append(meeting)
            except:
                continue

        return sorted(upcoming, key=lambda x: x["date"])

    def complete_meeting(self, meeting_id: int, summary: str = "") -> bool:
        """完成會議"""
        for meeting in self.meetings:
            if meeting["id"] == meeting_id:
                meeting["status"] = "completed"
                meeting["summary"] = summary
                meeting["updated_at"] = datetime.now().isoformat()
                self._save()
                print(f"[OK] Meeting completed: {meeting['title']}")
                return True
        return False

    def cancel_meeting(self, meeting_id: int, reason: str = "") -> bool:
        """取消會議"""
        for meeting in self.meetings:
            if meeting["id"] == meeting_id:
                meeting["status"] = "cancelled"
                meeting["cancel_reason"] = reason
                meeting["updated_at"] = datetime.now().isoformat()
                self._save()
                print(f"[OK] Meeting cancelled: {meeting['title']}")
                return True
        return False

    def get_stats(self) -> Dict:
        """獲取統計"""
        total = len(self.meetings)
        by_status = {}

        for m in self.meetings:
            status = m["status"]
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_meetings": total,
            "by_status": by_status,
            "upcoming": len(self.get_upcoming())
        }

    def generate_agenda(self, date: str = None) -> str:
        """生成議程"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        day_meetings = [m for m in self.get_upcoming(30) if m["date"] == date]

        if not day_meetings:
            return f"{date}: No meetings scheduled"

        agenda = []
        agenda.append(f"Agenda for {date}")
        agenda.append("=" * 50)

        for m in day_meetings:
            agenda.append(f"\n[{m['time']}] {m['title']}")
            agenda.append(f"  Duration: {m['duration']} minutes")
            if m.get('attendees'):
                agenda.append(f"  Attendees: {', '.join(m['attendees'])}")
            if m.get('location'):
                agenda.append(f"  Location: {m['location']}")
            if m.get('notes'):
                agenda.append(f"  Notes: {m['notes']}")

        return '\n'.join(agenda)

    def print_summary(self):
        """打印摘要"""
        stats = self.get_stats()
        upcoming = self.get_upcoming()

        print("\n" + "=" * 50)
        print("       Meeting Summary")
        print("=" * 50)
        print(f"Total Meetings: {stats['total_meetings']}")
        print(f"Upcoming (7 days): {stats['upcoming']}")
        print("\nUpcoming Meetings:")
        for m in upcoming[:5]:
            print(f"  - [{m['date']} {m['time']}] {m['title']}")
        print("=" * 50)


def quick_schedule(title: str, date: str, time: str, duration: int = 60) -> Dict:
    """快速安排會議"""
    manager = MeetingManager()
    return manager.schedule_meeting(title, date, time, duration)


if __name__ == "__main__":
    import sys

    manager = MeetingManager()

    if len(sys.argv) < 2:
        manager.print_summary()
    else:
        cmd = sys.argv[1]

        if cmd == "schedule":
            if len(sys.argv) > 4:
                title = sys.argv[2]
                date = sys.argv[3]
                time = sys.argv[4]
                duration = int(sys.argv[5]) if len(sys.argv) > 5 else 60
                manager.schedule_meeting(title, date, time, duration)
            else:
                print("Usage: python meeting_manager.py schedule <title> <date> <time> [duration]")

        elif cmd == "list":
            meetings = manager.get_upcoming()
            for m in meetings:
                print(f"  [{m['date']} {m['time']}] {m['title']}")

        elif cmd == "agenda":
            date = sys.argv[2] if len(sys.argv) > 2 else None
            print(manager.generate_agenda(date))

        elif cmd == "complete":
            if len(sys.argv) > 2:
                manager.complete_meeting(int(sys.argv[2]))

        elif cmd == "cancel":
            if len(sys.argv) > 2:
                manager.cancel_meeting(int(sys.argv[2]))

        else:
            print("Commands: schedule | list | agenda | complete | cancel")
