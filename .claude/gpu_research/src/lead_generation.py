# -*- coding: utf-8 -*-
"""
獲客管理系統 - Lead Generation & Tracking System

自動化管理品牌方開發和客戶追蹤
"""

import csv
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum


class InterestLevel(Enum):
    """興趣程度"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"
    NONE = "無"
    PENDING = "待確認"


class OutreachStatus(Enum):
    """跟進狀態"""
    NOT_CONTACTED = "未聯繫"
    EMAIL_SENT = "已發郵件"
    FOLLOWED_UP = "已跟進"
    REPLIED = "已回覆"
    MEETING_SCHEDULED = "已預約會議"
    NEGOTIATING = "談判中"
    CLOSED_WON = "成交"
    CLOSED_LOST = "失敗"


@dataclass
class BrandContact:
    """品牌聯繫人"""
    brand: str
    region: str
    contact_name: str
    email: str
    phone: str = ""
    wechat: str = ""
    title: str = ""
    department: str = ""
    linkedin: str = ""
    notes: str = ""


@dataclass
class OutreachRecord:
    """跟進記錄"""
    brand: str
    contact: str
    email: str
    sent_date: str
    subject: str
    template_used: str
    status: str = OutreachStatus.NOT_CONTACTED.value
    interest_level: str = InterestLevel.PENDING.value
    reply_date: str = ""
    reply_content: str = ""
    next_follow_up: str = ""
    notes: str = ""


class LeadGenerationSystem:
    """
    獲客管理系統
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = "d:/claude mini max 2.7/.claude/gpu_research"

        self.data_dir = data_dir
        self.contacts_file = f"{data_dir}/contacts_database.csv"
        self.outreach_file = f"{data_dir}/outreach_tracking.csv"
        self.contacts: List[BrandContact] = []
        self.outreach_records: List[OutreachRecord] = []

    def add_contact(self, contact: BrandContact):
        """添加聯繫人"""
        self.contacts.append(contact)
        self._save_contacts()

    def create_outreach(self, record: OutreachRecord):
        """創建跟進記錄"""
        self.outreach_records.append(record)
        self._save_outreach()

    def update_status(self, email: str, new_status: OutreachStatus,
                     interest_level: InterestLevel = None, reply_content: str = ""):
        """更新跟進狀態"""
        for record in self.outreach_records:
            if record.email == email:
                record.status = new_status.value
                if interest_level:
                    record.interest_level = interest_level.value
                if reply_content:
                    record.reply_content = reply_content
                    record.reply_date = datetime.now().strftime("%Y-%m-%d")
                break
        self._save_outreach()

    def get_follow_ups_due(self) -> List[OutreachRecord]:
        """獲取需要跟進的記錄"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [r for r in self.outreach_records
                if r.next_follow_up and r.next_follow_up <= today
                and r.status not in [OutreachStatus.CLOSED_WON.value,
                                     OutreachStatus.CLOSED_LOST.value]]

    def get_statistics(self) -> dict:
        """獲取統計信息"""
        total = len(self.outreach_records)
        by_status = {}
        by_interest = {}
        by_brand = {}

        for record in self.outreach_records:
            by_status[record.status] = by_status.get(record.status, 0) + 1
            by_interest[record.interest_level] = by_interest.get(record.interest_level, 0) + 1
            by_brand[record.brand] = by_brand.get(record.brand, 0) + 1

        return {
            "total_outreach": total,
            "by_status": by_status,
            "by_interest": by_interest,
            "by_brand": by_brand,
            "follow_ups_due": len(self.get_follow_ups_due()),
            "conversion_rate": (by_status.get(OutreachStatus.CLOSED_WON.value, 0) / total * 100
                               if total > 0 else 0)
        }

    def _save_contacts(self):
        """保存聯繫人數據"""
        with open(self.contacts_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['brand', 'region', 'contact_name', 'email', 'phone',
                           'wechat', 'title', 'department', 'linkedin', 'notes'])
            for c in self.contacts:
                writer.writerow([c.brand, c.region, c.contact_name, c.email,
                               c.phone, c.wechat, c.title, c.department,
                               c.linkedin, c.notes])

    def _save_outreach(self):
        """保存跟進數據"""
        with open(self.outreach_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['brand', 'contact', 'email', 'sent_date', 'subject',
                           'template_used', 'status', 'interest_level', 'reply_date',
                           'reply_content', 'next_follow_up', 'notes'])
            for r in self.outreach_records:
                writer.writerow([r.brand, r.contact, r.email, r.sent_date, r.subject,
                               r.template_used, r.status, r.interest_level, r.reply_date,
                               r.reply_content, r.next_follow_up, r.notes])

    def export_to_json(self, filepath: str):
        """導出為JSON"""
        data = {
            "contacts": [asdict(c) for c in self.contacts],
            "outreach_records": [asdict(r) for r in self.outreach_records],
            "statistics": self.get_statistics()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def init_sample_data(system: LeadGenerationSystem):
    """初始化示例數據"""

    # 添加品牌聯繫人
    sample_contacts = [
        BrandContact(
            brand="ASUS",
            region="台灣",
            contact_name="採購總監",
            email="purchasing@asus.com",
            title="採購總監",
            department="採購部"
        ),
        BrandContact(
            brand="MSI",
            region="台灣",
            contact_name="產品總監",
            email="product@msi.com",
            title="產品總監",
            department="產品部"
        ),
        BrandContact(
            brand="Corsair",
            region="美國",
            contact_name="B2B業務總監",
            email="B2B@corsair.com",
            title="B2B業務總監",
            department="商務發展部"
        ),
        BrandContact(
            brand="Seasonic",
            region="台灣",
            contact_name="商務總監",
            email="sales@seasonic.com",
            title="商務總監",
            department="國際業務部"
        ),
        BrandContact(
            brand="曜越T.T",
            region="台灣",
            contact_name="業務總監",
            email="sales@thermaltake.com.tw",
            title="業務總監",
            department="國際業務部"
        ),
    ]

    for contact in sample_contacts:
        system.add_contact(contact)

    # 添加跟進記錄
    today = datetime.now().strftime("%Y-%m-%d")
    sample_records = [
        OutreachRecord(
            brand="ASUS",
            contact="採購總監",
            email="purchasing@asus.com",
            sent_date=today,
            subject="全球顯卡電源接口燒毀研究報告",
            template_used="模板A",
            status=OutreachStatus.EMAIL_SENT.value,
            interest_level=InterestLevel.PENDING.value,
            next_follow_up=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        ),
        OutreachRecord(
            brand="MSI",
            contact="產品總監",
            email="product@msi.com",
            sent_date=today,
            subject="顯卡12VHPWR接口燒毀解決方案",
            template_used="模板B",
            status=OutreachStatus.EMAIL_SENT.value,
            interest_level=InterestLevel.PENDING.value,
            next_follow_up=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        ),
    ]

    for record in sample_records:
        system.create_outreach(record)


def main():
    """主函數"""
    system = LeadGenerationSystem()

    # 初始化示例數據
    init_sample_data(system)

    # 顯示統計
    stats = system.get_statistics()
    print("\n" + "=" * 60)
    print("📊 獲客管理系統 - 統計概覽")
    print("=" * 60)
    print(f"總跟進記錄: {stats['total_outreach']}")
    print(f"\n按狀態分佈:")
    for status, count in stats['by_status'].items():
        print(f"  - {status}: {count}")
    print(f"\n按品牌分佈:")
    for brand, count in stats['by_brand'].items():
        print(f"  - {brand}: {count}")
    print(f"\n待跟進: {stats['follow_ups_due']} 個")

    # 導出JSON
    export_file = f"{system.data_dir}/lead_generation_report.json"
    system.export_to_json(export_file)
    print(f"\n✅ 數據已導出: {export_file}")


if __name__ == '__main__':
    main()
