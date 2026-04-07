# -*- coding: utf-8 -*-
"""
代理技能共享系統
讓所有代理人共享和學習技能
"""

import json
import os
from datetime import datetime
from pathlib import Path


class AgentSkillHub:
    """代理技能中心"""

    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.skills_dir = self.base_dir / ".claude" / "skills"
        self.shared_dir = self.base_dir / ".claude" / "shared_skills"
        self.shared_dir.mkdir(exist_ok=True)

        self.registry_file = self.shared_dir / "skill_registry.json"
        self.load_registry()

    def load_registry(self):
        """載入技能註冊表"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                "skills": {},
                "agents": {},
                "learning_log": []
            }

    def save_registry(self):
        """保存註冊表"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)

    def register_skill(self, skill_name, skill_type, description, file_path, tags=None):
        """註冊技能"""
        self.registry["skills"][skill_name] = {
            "name": skill_name,
            "type": skill_type,
            "description": description,
            "file": str(file_path),
            "tags": tags or [],
            "registered_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_rate": 100.0,
            "last_used": None,
            "version": "1.0"
        }
        self.save_registry()

    def use_skill(self, skill_name, agent_id="default", success=True):
        """使用技能"""
        if skill_name in self.registry["skills"]:
            skill = self.registry["skills"][skill_name]
            skill["usage_count"] += 1
            skill["last_used"] = datetime.now().isoformat()

            # 更新代理使用記錄
            if agent_id not in self.registry["agents"]:
                self.registry["agents"][agent_id] = {"skills_used": [], "total_uses": 0}

            if skill_name not in self.registry["agents"][agent_id]["skills_used"]:
                self.registry["agents"][agent_id]["skills_used"].append(skill_name)

            self.registry["agents"][agent_id]["total_uses"] += 1

            self.save_registry()
            return True
        return False

    def get_skill_info(self, skill_name):
        """獲取技能信息"""
        return self.registry["skills"].get(skill_name)

    def list_skills(self, skill_type=None, tag=None):
        """列出技能"""
        skills = self.registry["skills"].values()

        if skill_type:
            skills = [s for s in skills if s["type"] == skill_type]

        if tag:
            skills = [s for s in skills if tag in s.get("tags", [])]

        return sorted(skills, key=lambda x: x["usage_count"], reverse=True)

    def add_learning(self, agent_id, lesson, category="general"):
        """記錄學習"""
        self.registry["learning_log"].append({
            "agent": agent_id,
            "lesson": lesson,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        self.save_registry()

    def get_learning_log(self, limit=20):
        """獲取學習日誌"""
        return self.registry["learning_log"][-limit:]

    def generate_hub_report(self):
        """生成技能中心報告"""
        report = []
        report.append("=" * 60)
        report.append("       Agent Skill Hub Report")
        report.append(f"       {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)

        # 技能統計
        skills = self.registry["skills"]
        report.append(f"\n[Skill Statistics]")
        report.append(f"  Total Skills: {len(skills)}")

        types = {}
        for s in skills.values():
            t = s["type"]
            types[t] = types.get(t, 0) + 1

        for t, count in types.items():
            report.append(f"  - {t}: {count}")

        # 最常用技能
        report.append("\n[Top 5 Used Skills]")
        sorted_skills = sorted(skills.values(), key=lambda x: x["usage_count"], reverse=True)
        for s in sorted_skills[:5]:
            report.append(f"  - {s['name']}: {s['usage_count']} uses")

        # 代理統計
        agents = self.registry["agents"]
        report.append(f"\n[Agent Statistics]")
        report.append(f"  Active Agents: {len(agents)}")

        # 學習日誌
        learning = self.registry["learning_log"][-5:]
        if learning:
            report.append("\n[Recent Learning]")
            for l in learning:
                report.append(f"  - [{l['agent']}] {l['lesson'][:50]}...")

        return "\n".join(report)


def auto_discover_skills(hub, skills_dir):
    """自動發現技能"""
    python_files = list(Path(skills_dir).glob("*.py"))

    for f in python_files:
        skill_name = f.stem

        # 簡單分類
        skill_type = "unknown"
        if "ppt" in skill_name.lower():
            skill_type = "PPT處理"
        elif "data" in skill_name.lower() or "analy" in skill_name.lower():
            skill_type = "數據分析"
        elif "pdf" in skill_name.lower():
            skill_type = "PDF處理"
        elif "skill" in skill_name.lower():
            skill_type = "技能管理"

        # 標籤
        tags = []
        if "generate" in skill_name.lower():
            tags.append("生成")
        if "extract" in skill_name.lower():
            tags.append("提取")
        if "batch" in skill_name.lower():
            tags.append("批次")

        if skill_name not in hub.registry["skills"]:
            hub.register_skill(
                skill_name=skill_name,
                skill_type=skill_type,
                description=f"Auto-discovered skill: {skill_name}",
                file_path=str(f),
                tags=tags
            )
            print(f"[+] Discovered: {skill_name} ({skill_type})")


if __name__ == "__main__":
    import sys

    hub = AgentSkillHub()

    # 自動發現技能
    print("Discovering skills...")
    auto_discover_skills(hub, hub.skills_dir)

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "list":
            skills = hub.list_skills()
            print(f"\nAll Skills ({len(skills)}):")
            for s in skills:
                print(f"  - {s['name']} ({s['type']}) - {s['usage_count']} uses")

        elif cmd == "info" and len(sys.argv) > 2:
            info = hub.get_skill_info(sys.argv[2])
            if info:
                print(f"\n{info['name']}:")
                print(f"  Type: {info['type']}")
                print(f"  Description: {info['description']}")
                print(f"  File: {info['file']}")
                print(f"  Tags: {', '.join(info['tags'])}")
                print(f"  Uses: {info['usage_count']}")
                print(f"  Last Used: {info['last_used'] or 'Never'}")

        elif cmd == "use" and len(sys.argv) > 2:
            skill = sys.argv[2]
            agent = sys.argv[3] if len(sys.argv) > 3 else "default"
            hub.use_skill(skill, agent)
            print(f"[OK] Used: {skill}")

        elif cmd == "learn" and len(sys.argv) > 3:
            agent = sys.argv[2]
            lesson = sys.argv[3]
            hub.add_learning(agent, lesson)
            print("[OK] Learning recorded")

        elif cmd == "report":
            print(hub.generate_hub_report())

        else:
            print("Commands: list | info <skill> | use <skill> [agent] | learn <agent> <lesson> | report")
    else:
        hub.print_report = lambda: print(hub.generate_hub_report())
        hub.print_report()
