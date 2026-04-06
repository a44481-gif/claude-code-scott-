# -*- coding: utf-8 -*-
"""
GPU 電源線燒毀研究工具 - 主程序
GPU Power Cable Burn Research Toolkit - Main Entry Point

用法:
    python main.py                    # 完整流程
    python main.py --collect         # 只收集數據
    python main.py --generate        # 只生成報告
    python main.py --send            # 只發送郵件
    python main.py --lark            # 只同步飛書
    python main.py --all             # 執行所有步驟
"""

import sys
import os
import argparse
from datetime import datetime

# Windows 控制台 UTF-8 支持
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 src 目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.collector import GPUCollector
from src.generator import ReportGenerator
from src.sender import EmailSender
from src.lark_sync import LarkSync
from src.config import config


class GPUMiningTool:
    """
    GPU 研究工具主類
    """

    def __init__(self):
        self.collector = GPUCollector()
        self.generator = ReportGenerator()
        self.sender = EmailSender()
        self.lark_sync = LarkSync()
        self.cases = []
        self.report_html = ''

        # 輸出目錄
        self.output_dir = os.path.join(os.path.dirname(__file__), 'docs')
        os.makedirs(self.output_dir, exist_ok=True)

    def run_all(self) -> bool:
        """
        執行完整流程
        """
        print("=" * 60)
        print("🚀 GPU 電源線燒毀研究工具 - 完整流程")
        print("=" * 60)

        # 1. 收集數據
        if not self.collect():
            return False

        # 2. 生成報告
        if not self.generate():
            return False

        # 3. 保存報告
        self.save()

        # 4. 發送郵件
        self.send_email()

        # 5. 同步飛書
        self.sync_lark()

        print("\n" + "=" * 60)
        print("✅ 完整流程執行完成!")
        print("=" * 60)

        return True

    def collect(self) -> bool:
        """
        收集數據
        """
        print("\n📊 步驟 1/4: 收集數據...")
        try:
            self.cases = self.collector.collect_all()
            stats = self.collector.get_statistics()

            print(f"   ✅ 收集到 {len(self.cases)} 個案例")
            print(f"   📈 按平台: {stats['by_platform']}")
            print(f"   📈 按地區: {stats['by_region']}")

            # 保存 JSON 數據
            json_path = os.path.join(self.output_dir, 'gpu_case_database.json')
            self.collector.export_to_json(json_path)
            print(f"   💾 數據已保存: {json_path}")

            return True
        except Exception as e:
            print(f"   ❌ 數據收集失敗: {e}")
            return False

    def generate(self) -> bool:
        """
        生成報告
        """
        print("\n📝 步驟 2/4: 生成報告...")
        try:
            self.report_html = self.generator.generate_html(self.cases)
            print(f"   ✅ 報告生成成功 ({len(self.report_html)} bytes)")
            return True
        except Exception as e:
            print(f"   ❌ 報告生成失敗: {e}")
            return False

    def save(self):
        """
        保存報告
        """
        print("\n💾 步驟 3/4: 保存報告...")
        try:
            # 保存 HTML 報告
            html_path = os.path.join(self.output_dir, 'gpu_report_complete.html')
            self.generator.save_report(self.report_html, html_path)
            print(f"   ✅ HTML 報告已保存: {html_path}")

            # 保存 Markdown 報告
            md_content = self.generator.generate_markdown(self.cases)
            md_path = os.path.join(self.output_dir, 'gpu_report_complete.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"   ✅ Markdown 報告已保存: {md_path}")

            # 保存 JSON 報告
            json_content = self.generator.generate_json(self.cases)
            json_path = os.path.join(self.output_dir, 'gpu_report_complete.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            print(f"   ✅ JSON 報告已保存: {json_path}")

        except Exception as e:
            print(f"   ❌ 保存失敗: {e}")

    def send_email(self):
        """
        發送郵件
        """
        print("\n📧 步驟 4/4: 發送郵件...")
        try:
            if not config.email.sender_auth_code:
                print("   ⚠️ 郵箱授權碼未設置，跳過郵件發送")
                return

            success = self.sender.send_report(
                report_html=self.report_html,
                recipients=['h13751019800@163.com']
            )

            if success:
                print("   ✅ 郵件發送成功")
            else:
                print("   ❌ 郵件發送失敗")

        except Exception as e:
            print(f"   ❌ 郵件發送失敗: {e}")

    def sync_lark(self):
        """
        同步飛書
        """
        print("\n📄 同步飛書...")
        try:
            if not config.lark.app_id:
                print("   ⚠️ 飛書 App ID 未設置，跳過飛書同步")
                return

            doc_url = self.lark_sync.sync_report(
                report_html=self.report_html,
                title=f"顯卡電源線燒毀研究報告 {datetime.now().strftime('%Y年%m月%d日')}"
            )

            if doc_url:
                print(f"   ✅ 飛書文檔已創建: {doc_url}")
            else:
                print("   ❌ 飛書同步失敗")

        except Exception as e:
            print(f"   ❌ 飛書同步失敗: {e}")

    def show_statistics(self):
        """
        顯示統計信息
        """
        if not self.cases:
            self.cases = self.collector.collect_all()

        stats = self.collector.get_statistics()

        print("\n" + "=" * 60)
        print("📊 案例統計")
        print("=" * 60)
        print(f"總案例數: {stats['total']}")
        print(f"\n按地區:")
        for region, count in stats['by_region'].items():
            print(f"  - {region}: {count}")
        print(f"\n按 GPU 型號:")
        for gpu, count in stats['by_gpu'].items():
            print(f"  - {gpu}: {count}")
        print(f"\n按嚴重程度:")
        for severity, count in stats['by_severity'].items():
            print(f"  - {severity}: {count}")
        print(f"\n按狀態:")
        for status, count in stats['by_status'].items():
            print(f"  - {status}: {count}")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='GPU 電源線燒毀研究工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python main.py                    # 完整流程
  python main.py --collect         # 只收集數據
  python main.py --generate        # 只生成報告
  python main.py --send            # 只發送郵件
  python main.py --lark            # 只同步飛書
  python main.py --stats           # 顯示統計信息
  python main.py --all             # 執行所有步驟
        """
    )

    parser.add_argument('--collect', action='store_true', help='只收集數據')
    parser.add_argument('--generate', action='store_true', help='只生成報告')
    parser.add_argument('--send', action='store_true', help='只發送郵件')
    parser.add_argument('--lark', action='store_true', help='只同步飛書')
    parser.add_argument('--stats', action='store_true', help='顯示統計信息')
    parser.add_argument('--all', action='store_true', help='執行所有步驟')

    args = parser.parse_args()

    tool = GPUMiningTool()

    # 如果沒有指定任何參數，執行完整流程
    if len(sys.argv) == 1 or args.all:
        tool.run_all()
        return

    # 執行指定的操作
    if args.collect:
        tool.collect()
        tool.save()

    if args.generate:
        tool.cases = tool.collector.collect_all()
        tool.generate()
        tool.save()

    if args.send:
        tool.cases = tool.collector.collect_all()
        tool.report_html = tool.generator.generate_html(tool.cases)
        tool.send_email()

    if args.lark:
        tool.cases = tool.collector.collect_all()
        tool.report_html = tool.generator.generate_html(tool.cases)
        tool.sync_lark()

    if args.stats:
        tool.show_statistics()


if __name__ == '__main__':
    main()
