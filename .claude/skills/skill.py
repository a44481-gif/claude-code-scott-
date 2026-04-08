# -*- coding: utf-8 -*-
"""
統一啟動器 - 一個命令啟動所有技能
"""

import sys
import os
from pathlib import Path

# 確保 UTF-8 編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class SkillLauncher:
    """技能啟動器"""

    SKILLS = {
        # PPT/數據處理
        "ppt-analyze": {"file": "ppt_analyzer.py", "desc": "分析 PPT 內容"},
        "ppt-gen": {"file": "ppt_generator_v3.py", "desc": "生成 PPT 報告"},
        "data-analyze": {"file": "data_analyzer.py", "desc": "分析市場數據"},
        "excel-read": {"file": "excel_reader.py", "desc": "讀取 Excel/CSV"},
        "chart": {"file": "chart_generator.py", "desc": "生成圖表"},
        "pdf": {"file": "pdf_generator.py", "desc": "生成 PDF 報告"},
        "auto-report": {"file": "auto_report.py", "desc": "一鍵自動化報告"},

        # 商務工具
        "market": {"file": "market_research.py", "desc": "市場研究"},
        "customer": {"file": "customer_manager.py", "desc": "客戶管理"},
        "business-plan": {"file": "business_plan_generator.py", "desc": "商業計劃書"},
        "meeting": {"file": "meeting_manager.py", "desc": "會議管理"},
        "decision": {"file": "decision_analyzer.py", "desc": "決策分析"},
        "translate": {"file": "translation_tool.py", "desc": "翻譯工具"},

        # 系統工具
        "backup": {"file": "data_backup.py", "desc": "數據備份"},
        "tag": {"file": "tag_manager.py", "desc": "標籤管理"},
        "batch": {"file": "batch_process.py", "desc": "批次處理"},
        "skill-hub": {"file": "agent_skill_hub.py", "desc": "技能中心"},
        "skill-opt": {"file": "skill_optimizer.py", "desc": "技能優化"},
    }

    def __init__(self):
        self.skills_dir = Path(__file__).parent

    def list_skills(self):
        """列出所有技能"""
        print("\n" + "=" * 60)
        print("       Available Skills (23)")
        print("=" * 60)

        categories = {
            "PPT/資料處理": ["ppt-analyze", "ppt-gen", "data-analyze", "excel-read", "chart", "pdf", "auto-report"],
            "商務工具": ["market", "customer", "business-plan", "meeting", "decision", "translate"],
            "系統工具": ["backup", "tag", "batch", "skill-hub", "skill-opt"]
        }

        for category, skills in categories.items():
            print(f"\n[{category}]")
            for skill_id in skills:
                if skill_id in self.SKILLS:
                    info = self.SKILLS[skill_id]
                    print(f"  {skill_id:<15} - {info['desc']}")

        print("\n" + "=" * 60)
        print("Usage: python skill.py <skill-id> [args...]")
        print("Example: python skill.py ppt-analyze report.pptx")
        print("=" * 60)

    def run_skill(self, skill_id, args):
        """運行技能"""
        if skill_id not in self.SKILLS:
            print(f"[ERROR] Unknown skill: {skill_id}")
            self.list_skills()
            return False

        info = self.SKILLS[skill_id]
        script = self.skills_dir / info["file"]

        if not script.exists():
            print(f"[ERROR] Script not found: {script}")
            return False

        # 構建命令
        cmd = [sys.executable, str(script)] + args

        # 執行
        try:
            import subprocess
            result = subprocess.run(cmd)
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] Failed to run: {e}")
            return False

    def test_all(self):
        """測試所有技能"""
        print("\nTesting all skills...")

        # 只測試不需要參數的技能
        test_skills = [
            ("skill-opt", ["stats"]),
            ("decision", []),
        ]

        results = []
        for skill_id, args in test_skills:
            info = self.SKILLS[skill_id]
            script = self.skills_dir / info["file"]

            try:
                import subprocess
                cmd = [sys.executable, str(script)] + args
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                status = "OK" if result.returncode == 0 else "FAIL"
                results.append((skill_id, status))
            except Exception as e:
                results.append((skill_id, f"ERROR: {e}"))

        print("\n" + "=" * 50)
        print("       Test Results")
        print("=" * 50)
        for skill_id, status in results:
            print(f"  [{status}] {skill_id}")
        print("=" * 50)

        return results


def main():
    launcher = SkillLauncher()

    if len(sys.argv) < 2:
        launcher.list_skills()
    else:
        cmd = sys.argv[1]

        if cmd == "list":
            launcher.list_skills()
        elif cmd == "test":
            launcher.test_all()
        elif cmd == "help":
            launcher.list_skills()
        else:
            args = sys.argv[2:] if len(sys.argv) > 2 else []
            launcher.run_skill(cmd, args)


if __name__ == "__main__":
    main()
