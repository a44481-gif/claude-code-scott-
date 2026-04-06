# -*- coding: utf-8 -*-
"""
批次處理腳本 - 分析多個 PPT 並生成報告
"""

import subprocess
import os
import json
from datetime import datetime


def process_ppt(pptx_path, output_dir):
    """處理單個 PPT 檔案"""
    basename = os.path.splitext(os.path.basename(pptx_path))[0]
    print(f"\n{'='*60}")
    print(f"處理: {basename}")
    print(f"{'='*60}")

    # Step 1: 分析 PPT
    analysis_json = os.path.join(output_dir, f"{basename}_analysis.json")
    print(f"\n[1/3] 分析 PPT 內容...")

    # Run analysis
    result = subprocess.run([
        'python', '.claude/skills/ppt_analyzer.py',
        pptx_path, analysis_json
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  [警告] 分析可能失敗: {result.stderr[:200]}")
        if os.path.exists(analysis_json):
            print(f"  [OK] 分析結果已保存")

    # Check if it's market data
    has_market_data = False
    if os.path.exists(analysis_json):
        with open(analysis_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            has_market_data = data.get('statistics', {}).get('total_tables', 0) > 0

    if has_market_data:
        # Step 2: 分析數據
        market_json = os.path.join(output_dir, f"{basename}_market.json")
        market_csv = os.path.join(output_dir, f"{basename}_market.csv")
        print(f"\n[2/3] 分析市場數據...")

        result = subprocess.run([
            'python', '.claude/skills/data_analyzer.py',
            analysis_json, market_csv, market_json
        ], capture_output=True, text=True)

        if os.path.exists(market_json):
            print(f"  [OK] 市場數據已生成")

        # Step 3: 生成 PPT
        output_pptx = os.path.join(output_dir, f"{basename}_報告.pptx")
        print(f"\n[3/3] 生成報告 PPT...")

        result = subprocess.run([
            'python', '.claude/skills/ppt_generator_v2.py',
            market_json, output_pptx
        ], capture_output=True, text=True)

        if os.path.exists(output_pptx):
            print(f"  [OK] PPT 已生成: {basename}_報告.pptx")
    else:
        print(f"  [跳過] 無市場數據表格")

    print(f"\n[完成] {basename}")


def main():
    output_dir = "d:/claude mini max 2.7/ppt_reports"
    os.makedirs(output_dir, exist_ok=True)

    # 要處理的 PPT 列表
    ppt_files = [
        "d:/李總項目/CCS集成母排商业开发方案-李總方案.pptx",
        "d:/李總項目/CCS 全球销售计划及产品竞品分析0404.pptx",
        "d:/李總項目/IFPCS整合规划书.pptx",
    ]

    print("="*60)
    print("PPT 批次處理 - 分析與報告生成")
    print("="*60)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"輸出目錄: {output_dir}")
    print(f"待處理檔案: {len(ppt_files)} 個")
    print("="*60)

    for pptx in ppt_files:
        if os.path.exists(pptx):
            process_ppt(pptx, output_dir)
        else:
            print(f"\n[錯誤] 檔案不存在: {pptx}")

    print("\n" + "="*60)
    print("批次處理完成！")
    print("="*60)
    print(f"輸出目錄: {output_dir}")

    # 列出生成的文件
    files = [f for f in os.listdir(output_dir) if f.endswith('.pptx')]
    if files:
        print(f"\n生成的 PPT ({len(files)} 個):")
        for f in sorted(files):
            print(f"  - {f}")


if __name__ == "__main__":
    main()
