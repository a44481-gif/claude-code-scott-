# -*- coding: utf-8 -*-
"""
技能優化追蹤系統
記錄技能使用情況、收集反饋、持續改進
"""

import json
import os
from datetime import datetime
from pathlib import Path


class SkillOptimizer:
    """技能優化器"""

    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.skills_dir = self.base_dir / ".claude" / "skills"
        self.tracker_file = self.base_dir / ".claude" / "skills" / "skill_tracker.json"
        self.feedback_file = self.base_dir / ".claude" / "skills" / "skill_feedback.json"
        self.improvements_file = self.base_dir / ".claude" / "skills" / "skill_improvements.json"

        self.load_data()

    def load_data(self):
        """載入追蹤數據"""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r', encoding='utf-8') as f:
                self.tracker = json.load(f)
        else:
            self.tracker = {"usage": {}, "last_used": {}, "success_rate": {}}

        if self.feedback_file.exists():
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                self.feedback = json.load(f)
        else:
            self.feedback = {"items": [], "pending": []}

        if self.improvements_file.exists():
            with open(self.improvements_file, 'r', encoding='utf-8') as f:
                self.improvements = json.load(f)
        else:
            self.improvements = {"completed": [], "planned": [], "learning": []}

    def save_data(self):
        """保存數據"""
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.tracker, f, ensure_ascii=False, indent=2)

        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback, f, ensure_ascii=False, indent=2)

        with open(self.improvements_file, 'w', encoding='utf-8') as f:
            json.dump(self.improvements, f, ensure_ascii=False, indent=2)

    def record_usage(self, skill_name, success=True):
        """記錄技能使用"""
        now = datetime.now().isoformat()

        if skill_name not in self.tracker["usage"]:
            self.tracker["usage"][skill_name] = 0
            self.tracker["success_rate"][skill_name] = {"success": 0, "failed": 0}

        self.tracker["usage"][skill_name] += 1
        self.tracker["last_used"][skill_name] = now

        if success:
            self.tracker["success_rate"][skill_name]["success"] += 1
        else:
            self.tracker["success_rate"][skill_name]["failed"] += 1

        self.save_data()

    def add_feedback(self, skill_name, feedback_text, priority="medium"):
        """添加反饋"""
        item = {
            "skill": skill_name,
            "feedback": feedback_text,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        self.feedback["pending"].append(item)
        self.save_data()
        return item

    def resolve_feedback(self, index, improvement_note):
        """解決反饋並記錄改進"""
        if index < len(self.feedback["pending"]):
            item = self.feedback["pending"].pop(index)
            item["status"] = "resolved"
            item["improvement"] = improvement_note
            item["resolved_at"] = datetime.now().isoformat()

            self.feedback["items"].append(item)

            # 記錄改進
            self.improvements["completed"].append({
                "skill": item["skill"],
                "feedback": item["feedback"],
                "improvement": improvement_note,
                "timestamp": datetime.now().isoformat()
            })

            self.save_data()

    def add_planned_improvement(self, skill_name, description, reason):
        """添加計劃改進"""
        self.improvements["planned"].append({
            "skill": skill_name,
            "description": description,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "status": "planned"
        })
        self.save_data()

    def add_learning(self, lesson_text):
        """記錄學習內容"""
        self.improvements["learning"].append({
            "lesson": lesson_text,
            "timestamp": datetime.now().isoformat()
        })
        self.save_data()

    def get_skill_stats(self):
        """獲取技能統計"""
        stats = []
        for skill, count in self.tracker["usage"].items():
            rate = self.tracker["success_rate"][skill]
            total = rate["success"] + rate["failed"]
            success_pct = (rate["success"] / total * 100) if total > 0 else 0

            stats.append({
                "skill": skill,
                "usage_count": count,
                "success_rate": round(success_pct, 1),
                "last_used": self.tracker["last_used"].get(skill, "Never")
            })

        return sorted(stats, key=lambda x: x["usage_count"], reverse=True)

    def get_pending_feedback(self):
        """獲取待處理反饋"""
        return self.feedback["pending"]

    def generate_report(self):
        """生成優化報告"""
        report = []
        report.append("=" * 60)
        report.append("       技能優化報告")
        report.append(f"       {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)

        # 使用統計
        stats = self.get_skill_stats()
        report.append("\n[技能使用統計]")
        for s in stats[:10]:
            report.append(f"  {s['skill']}: {s['usage_count']}次 (成功率 {s['success_rate']}%)")

        # 待處理反饋
        pending = self.get_pending_feedback()
        if pending:
            report.append(f"\n[待處理反饋] ({len(pending)} 項)")
            for i, p in enumerate(pending[:5], 1):
                report.append(f"  {i}. [{p['skill']}] {p['feedback'][:50]}...")

        # 計劃改進
        planned = self.improvements["planned"]
        if planned:
            report.append(f"\n[計劃改進] ({len(planned)} 項)")
            for p in planned[:5]:
                report.append(f"  • {p['skill']}: {p['description']}")

        # 最近學習
        learning = self.improvements["learning"][-5:]
        if learning:
            report.append("\n[最近學習]")
            for l in learning:
                report.append(f"  • {l['lesson'][:60]}...")

        return "\n".join(report)

    def print_report(self):
        """打印報告"""
        print(self.generate_report())


if __name__ == "__main__":
    import sys

    optimizer = SkillOptimizer()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "stats":
            optimizer.print_report()

        elif cmd == "feedback":
            if len(sys.argv) > 3:
                optimizer.add_feedback(sys.argv[2], sys.argv[3])
                print(f"[OK] Feedback added for: {sys.argv[2]}")
            else:
                print("Usage: python skill_optimizer.py feedback <skill_name> <feedback_text>")

        elif cmd == "improve":
            if len(sys.argv) > 4:
                optimizer.add_planned_improvement(sys.argv[2], sys.argv[3], sys.argv[4])
                print(f"[OK] Improvement planned for: {sys.argv[2]}")
            else:
                print("Usage: python skill_optimizer.py improve <skill> <description> <reason>")

        elif cmd == "learn":
            if len(sys.argv) > 2:
                optimizer.add_learning(sys.argv[2])
                print("[OK] Learning recorded")
            else:
                print("Usage: python skill_optimizer.py learn <lesson_text>")

        elif cmd == "use":
            if len(sys.argv) > 2:
                success = sys.argv[2].lower() == "success"
                if len(sys.argv) > 3:
                    optimizer.record_usage(sys.argv[3], success)
                else:
                    optimizer.record_usage("unknown", success)
            else:
                print("Usage: python skill_optimizer.py use <success|fail> <skill_name>")

        else:
            print("Commands: stats | feedback | improve | learn | use")
    else:
        optimizer.print_report()
