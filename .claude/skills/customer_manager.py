# -*- coding: utf-8 -*-
"""
客戶管理工具 - 管理潛在客戶和聯繫人
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class CustomerManager:
    """客戶管理系統"""

    def __init__(self, db_path="customers.json"):
        self.db_path = db_path
        self.customers = self._load()

    def _load(self) -> List[Dict]:
        """載入數據"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save(self):
        """保存數據"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.customers, f, ensure_ascii=False, indent=2)

    def add_customer(self, name: str, company: str = "", email: str = "",
                     wechat: str = "", phone: str = "", source: str = "",
                     notes: str = "") -> Dict:
        """添加客戶"""
        customer = {
            "id": len(self.customers) + 1,
            "name": name,
            "company": company,
            "email": email,
            "wechat": wechat,
            "phone": phone,
            "source": source,
            "status": "new",  # new, contacted, qualified, proposal, won, lost
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "interactions": []
        }
        self.customers.append(customer)
        self._save()
        print(f"[OK] Customer added: {name}")
        return customer

    def add_interaction(self, customer_id: int, interaction_type: str,
                       content: str) -> bool:
        """添加互動記錄"""
        for customer in self.customers:
            if customer["id"] == customer_id:
                customer["interactions"].append({
                    "type": interaction_type,
                    "content": content,
                    "date": datetime.now().isoformat()
                })
                customer["updated_at"] = datetime.now().isoformat()
                self._save()
                return True
        return False

    def update_status(self, customer_id: int, status: str) -> bool:
        """更新客戶狀態"""
        valid_statuses = ["new", "contacted", "qualified", "proposal", "won", "lost"]
        if status not in valid_statuses:
            print(f"[ERROR] Invalid status. Must be one of: {valid_statuses}")
            return False

        for customer in self.customers:
            if customer["id"] == customer_id:
                customer["status"] = status
                customer["updated_at"] = datetime.now().isoformat()
                self._save()
                print(f"[OK] Status updated: {customer['name']} -> {status}")
                return True
        return False

    def search(self, query: str) -> List[Dict]:
        """搜索客戶"""
        results = []
        query = query.lower()
        for customer in self.customers:
            if (query in customer["name"].lower() or
                query in customer["company"].lower() or
                query in customer["email"].lower() or
                query in customer.get("wechat", "").lower()):
                results.append(customer)
        return results

    def get_stats(self) -> Dict:
        """獲取統計"""
        total = len(self.customers)
        by_status = {}

        for customer in self.customers:
            status = customer["status"]
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_customers": total,
            "by_status": by_status
        }

    def export_leads(self) -> str:
        """導出銷售線索"""
        leads = []
        for c in self.customers:
            if c["status"] in ["new", "contacted"]:
                leads.append({
                    "name": c["name"],
                    "company": c["company"],
                    "email": c["email"],
                    "wechat": c.get("wechat", ""),
                    "source": c["source"],
                    "status": c["status"]
                })

        path = f"leads_export_{datetime.now().strftime('%Y%m%d')}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)
        print(f"[OK] Leads exported: {path}")
        return path

    def print_summary(self):
        """打印摘要"""
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("       Customer Management Summary")
        print("=" * 50)
        print(f"Total Customers: {stats['total_customers']}")
        print("\nBy Status:")
        status_names = {
            "new": "New",
            "contacted": "Contacted",
            "qualified": "Qualified",
            "proposal": "Proposal",
            "won": "Won",
            "lost": "Lost"
        }
        for status, count in stats["by_status"].items():
            print(f"  - {status_names.get(status, status)}: {count}")
        print("=" * 50)


if __name__ == "__main__":
    import sys

    cm = CustomerManager()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python customer_manager.py add <name> [company] [email] [wechat]")
        print("  python customer_manager.py search <query>")
        print("  python customer_manager.py status <id> <new_status>")
        print("  python customer_manager.py stats")
        print("  python customer_manager.py export")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        name = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
        company = sys.argv[3] if len(sys.argv) > 3 else ""
        email = sys.argv[4] if len(sys.argv) > 4 else ""
        wechat = sys.argv[5] if len(sys.argv) > 5 else ""
        cm.add_customer(name, company, email, wechat, source="Direct Contact")

    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = cm.search(query)
        print(f"\nFound {len(results)} customers:")
        for c in results:
            print(f"  - {c['name']} ({c['company']}) - {c['status']}")

    elif cmd == "status":
        if len(sys.argv) > 3:
            cm.update_status(int(sys.argv[2]), sys.argv[3])

    elif cmd == "stats":
        cm.print_summary()

    elif cmd == "export":
        cm.export_leads()

    else:
        print(f"Unknown command: {cmd}")
