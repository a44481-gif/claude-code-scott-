# -*- coding: utf-8 -*-
"""
數據分析器 - 自訂 Skill 實現
市場趨勢分析、CAGR 計算、報告生成
"""

import sys
import os
import json
from collections import defaultdict
from datetime import datetime


def load_data(json_path):
    """載入分析結果"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_market_data(data):
    """
    分析市場數據

    Returns:
        dict: 市場分析結果
    """
    results = {
        "analyzed_at": datetime.now().isoformat(),
        "source_file": data.get("file", ""),
        "total_market_5yr": 0,
        "segments": [],
        "fastest_growing": [],
        "largest_segment": None,
        "growth_rates": {}
    }

    # 遍歷所有幻燈片的表格
    for slide in data.get('slides', []):
        for table in slide.get('tables', []):
            if not table or len(table) < 2:
                continue

            headers = table[0]
            # 檢查是否是市場數據表
            if not any('2025' in str(h) for h in headers):
                continue

            # 解析每行數據
            for row in table[1:]:
                if len(row) < 10:
                    continue

                try:
                    segment = str(row[0]).strip()
                    if not segment or segment in ['賽道', '单位', '']:
                        continue

                    # 提取年度數據
                    years = {}
                    year_cols = [2, 3, 4, 5, 6, 7]  # 2025-2030
                    year_names = ['2025', '2026', '2027', '2028', '2029', '2030']

                    for col, year in zip(year_cols, year_names):
                        try:
                            years[year] = float(row[col]) if row[col] else 0
                        except (ValueError, IndexError):
                            years[year] = 0

                    cumulative = float(row[8]) if row[8] else 0
                    share = float(row[9]) if row[9] else 0

                    # 計算 CAGR (2025-2030, 5年)
                    cagr = ((years['2030'] / years['2025']) ** 0.2 - 1) * 100 \
                           if years['2025'] > 0 else 0

                    seg_data = {
                        "name": segment,
                        "cagr_2025_2030": round(cagr, 1),
                        "cumulative_5yr": cumulative,
                        "share_2025_2030": share,
                        "scale_2025": years['2025'],
                        "scale_2030": years['2030'],
                        "yearly_data": years
                    }
                    results["segments"].append(seg_data)
                    results["growth_rates"][segment] = round(cagr, 1)

                    # 追蹤最快增速
                    if cagr > 30:
                        results["fastest_growing"].append(seg_data)

                    # 追蹤最大市場
                    if results["largest_segment"] is None or \
                       cumulative > results["largest_segment"]["cumulative_5yr"]:
                        results["largest_segment"] = seg_data

                    results["total_market_5yr"] += cumulative

                except (ValueError, IndexError):
                    continue

    # 排序
    results["segments"] = sorted(results["segments"],
                                 key=lambda x: x["cumulative_5yr"],
                                 reverse=True)
    results["fastest_growing"] = sorted(results["fastest_growing"],
                                        key=lambda x: x["cagr_2025_2030"],
                                        reverse=True)

    return results


def generate_report(analysis):
    """生成分析報告"""
    report = []
    report.append("=" * 60)
    report.append("       市場分析洞察報告")
    report.append("=" * 60)
    report.append(f"分析時間: {analysis['analyzed_at']}")
    report.append(f"數據來源: {analysis['source_file']}")
    report.append("")

    report.append(f"[市場總規模]")
    report.append(f"  2025-2030 5年累計: {analysis['total_market_5yr']:,.0f} 億元")
    report.append("")

    # 最大市場
    if analysis["largest_segment"]:
        top = analysis["largest_segment"]
        report.append(f"[規模最大] {top['name']}")
        report.append(f"  5年累計: {top['cumulative_5yr']:,.0f} 億元")
        report.append(f"  市場份額: {top['share_2025_2030']}%")
        report.append("")

    # 最快增速
    report.append("[增速最快 Top 5]")
    for i, seg in enumerate(analysis["fastest_growing"][:5], 1):
        report.append(f"  {i}. {seg['name']}: CAGR {seg['cagr_2025_2030']}%")
    report.append("")

    # 市場排名
    report.append("[市場規模排名]")
    for i, seg in enumerate(analysis["segments"][:10], 1):
        report.append(f"  {i:2d}. {seg['name']:<12} {seg['cumulative_5yr']:>10,.0f} 億元 "
                      f"({seg['share_2025_2030']:>5.2f}%)")

    return "\n".join(report)


def export_csv(analysis, output_path):
    """導出 CSV"""
    lines = ["排名,賽道,CAGR (%),5年累計,2030規模,市場份額"]
    for i, seg in enumerate(analysis["segments"], 1):
        lines.append(f"{i},{seg['name']},{seg['cagr_2025_2030']},"
                     f"{seg['cumulative_5yr']},{seg['scale_2030']},{seg['share_2025_2030']}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"[OK] CSV 導出: {output_path}")


def export_json(analysis, output_path):
    """導出 JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"[OK] JSON 導出: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python data_analyzer.py <ppt_analysis_json> [output_csv] [output_json]")
        print("範例: python data_analyzer.py analysis.json market.csv market.json")
        sys.exit(1)

    json_path = sys.argv[1]
    csv_path = sys.argv[2] if len(sys.argv) > 2 else None
    json_out = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(json_path):
        print(f"[ERROR] 檔案不存在: {json_path}")
        sys.exit(1)

    print(f"載入數據: {json_path}")
    data = load_data(json_path)
    analysis = analyze_market_data(data)

    print(generate_report(analysis))

    if csv_path:
        export_csv(analysis, csv_path)
    if json_out:
        export_json(analysis, json_out)
