# -*- coding: utf-8 -*-
"""
完整分析流程 - 一鍵分析 PPT 並生成市場報告
"""

import sys
import os
import json
import subprocess
from datetime import datetime


def run_command(cmd, description):
    """執行命令並返回結果"""
    print(f"\n>>> {description}")
    print(f"    {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"    [Note] {result.stderr[:200]}")
    return result.returncode == 0


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("PPT 完整分析工具 - 一鍵生成市場分析報告")
        print("=" * 60)
        print("")
        print("用法: python full_analysis.py <pptx_file>")
        print("")
        print("範例:")
        print("  python full_analysis.py Global_Storage_Market_2025_2030.pptx")
        print("  python full_analysis.py \"d:/項目報告.pptx\"")
        print("")
        print("輸出:")
        print("  - analysis_result.json  (PPT 完整分析)")
        print("  - market_analysis.csv   (市場數據表)")
        print("  - market_report.txt     (分析報告)")
        sys.exit(1)

    pptx_file = sys.argv[1]

    if not os.path.exists(pptx_file):
        print(f"[ERROR] 檔案不存在: {pptx_file}")
        sys.exit(1)

    # 取得腳本目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    # 生成輸出檔名
    base_name = os.path.splitext(os.path.basename(pptx_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_json = os.path.join(base_dir, f"{base_name}_analysis.json")
    market_csv = os.path.join(base_dir, f"{base_name}_market.csv")
    market_json = os.path.join(base_dir, f"{base_name}_market.json")
    report_txt = os.path.join(base_dir, f"{base_name}_report_{timestamp}.txt")

    print("=" * 60)
    print(f"開始分析: {os.path.basename(pptx_file)}")
    print("=" * 60)

    # Step 1: 分析 PPT
    cmd1 = [
        sys.executable,
        os.path.join(script_dir, "ppt_analyzer.py"),
        pptx_file,
        analysis_json
    ]
    run_command(cmd1, "步驟1: 分析 PPT 內容")

    # Step 2: 分析市場數據
    if os.path.exists(analysis_json):
        cmd2 = [
            sys.executable,
            os.path.join(script_dir, "data_analyzer.py"),
            analysis_json,
            market_csv,
            market_json
        ]
        run_command(cmd2, "步驟2: 分析市場數據")

        # Step 3: 生成報告
        if os.path.exists(market_json):
            with open(market_json, 'r', encoding='utf-8') as f:
                analysis = json.load(f)

            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("       全球市場分析報告")
            report_lines.append(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"數據來源: {os.path.basename(pptx_file)}")
            report_lines.append("=" * 60)
            report_lines.append("")

            report_lines.append(f"[市場總規模]")
            report_lines.append(f"  2025-2030 5年累計: {analysis['total_market_5yr']:,.0f} 億元")
            report_lines.append("")

            if analysis["largest_segment"]:
                top = analysis["largest_segment"]
                report_lines.append(f"[規模最大賽道] {top['name']}")
                report_lines.append(f"  5年累計: {top['cumulative_5yr']:,.0f} 億元")
                report_lines.append(f"  市場份額: {top['share_2025_2030']}%")
                report_lines.append("")

            report_lines.append("[增速最快 Top 5]")
            for i, seg in enumerate(analysis["fastest_growing"][:5], 1):
                report_lines.append(f"  {i}. {seg['name']}: CAGR {seg['cagr_2025_2030']}%")
            report_lines.append("")

            report_lines.append("[市場規模排名 Top 10]")
            report_lines.append(f"  {'排名':<4} {'賽道':<14} {'5年累計(億元)':>14} {'CAGR':>8} {'份額':>8}")
            report_lines.append("  " + "-" * 55)
            for i, seg in enumerate(analysis["segments"][:10], 1):
                report_lines.append(
                    f"  {i:>2}.  {seg['name']:<12} {seg['cumulative_5yr']:>14,.0f} "
                    f"{seg['cagr_2025_2030']:>7.1f}% {seg['share_2025_2030']:>7.2f}%"
                )

            report_lines.append("")
            report_lines.append("=" * 60)
            report_lines.append("                    分析完成")
            report_lines.append("=" * 60)

            report_content = "\n".join(report_lines)
            with open(report_txt, 'w', encoding='utf-8') as f:
                f.write(report_content)

            print(f"\n[OK] 報告已生成: {report_txt}")

    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)
    print(f"  PPT 分析: {analysis_json}")
    print(f"  市場數據: {market_csv}")
    print(f"  分析報告: {report_txt}")


if __name__ == "__main__":
    main()
