# -*- coding: utf-8 -*-
"""
PPT 數據分析腳本
功能：市場分析、趨勢預測、數據可視化
"""

import json
import sys
from collections import defaultdict


def load_ppt_data(json_path):
    """載入 PPT 分析結果"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_market_trends(data):
    """分析市場趨勢"""
    results = {
        "total_market_5yr": 0,
        "segments": [],
        "fastest_growing": [],
        "largest_segment": None
    }

    # 直接遍歷所有幻燈片的表格
    for slide in data['slides']:
        for table in slide['tables']:
            # table 是 [[row0], [row1], ...]
            if not table or len(table) < 2:
                continue

            headers = table[0]
            # 檢查是否是市場數據表
            if not any('2025' in str(h) for h in headers):
                continue

            # 解析每行數據
            for row in table[1:]:
                if len(row) < 9:
                    continue

                try:
                    segment = str(row[0]).strip()
                    if not segment or segment in ['赛道', '单位', '']:
                        continue

                    yr_2025 = float(row[2]) if row[2] else 0
                    yr_2026 = float(row[3]) if row[3] else 0
                    yr_2027 = float(row[4]) if row[4] else 0
                    yr_2028 = float(row[5]) if row[5] else 0
                    yr_2029 = float(row[6]) if row[6] else 0
                    yr_2030 = float(row[7]) if row[7] else 0
                    cumulative = float(row[8]) if row[8] else 0
                    share = float(row[9]) if row[9] else 0

                    # 計算 CAGR
                    cagr = ((yr_2030 / yr_2025) ** 0.2 - 1) * 100 if yr_2025 > 0 else 0

                    seg_data = {
                        "name": segment,
                        "cagr_2025_2030": round(cagr, 1),
                        "cumulative_5yr": cumulative,
                        "share_2025_2030": share,
                        "scale_2030": yr_2030
                    }
                    results["segments"].append(seg_data)

                    if cagr > 30:
                        results["fastest_growing"].append(seg_data)

                    if results["largest_segment"] is None or cumulative > results["largest_segment"]["cumulative_5yr"]:
                        results["largest_segment"] = seg_data

                    results["total_market_5yr"] += cumulative

                except (ValueError, IndexError) as e:
                    continue

    # 按規模排序
    results["segments"] = sorted(results["segments"],
                                  key=lambda x: x["cumulative_5yr"],
                                  reverse=True)

    # 按增速排序
    results["fastest_growing"] = sorted(results["fastest_growing"],
                                         key=lambda x: x["cagr_2025_2030"],
                                         reverse=True)

    return results


def generate_insights(analysis):
    """生成分析洞察"""
    if not analysis or not analysis["segments"]:
        return "No data available"

    insights = []
    insights.append("=" * 60)
    insights.append("MARKET ANALYSIS INSIGHTS")
    insights.append("=" * 60)
    insights.append("")

    insights.append(f"[Total Market 2025-2030] {analysis['total_market_5yr']:,.0f} 亿元 (RMB)")
    insights.append("")

    if analysis["largest_segment"]:
        top = analysis["largest_segment"]
        insights.append(f"[Largest Segment] {top['name']}")
        insights.append(f"  - 5-Year Cumulative: {top['cumulative_5yr']:,.0f} 亿元")
        insights.append(f"  - Market Share: {top['share_2025_2030']}%")
        insights.append("")

    insights.append("[Top 5 Fastest Growing Segments]")
    for i, seg in enumerate(analysis["fastest_growing"][:5], 1):
        insights.append(f"  {i}. {seg['name']} (CAGR: {seg['cagr_2025_2030']}%)")
    insights.append("")

    insights.append("[Top 5 Largest Segments by Scale]")
    for i, seg in enumerate(analysis["segments"][:5], 1):
        insights.append(f"  {i}. {seg['name']} ({seg['cumulative_5yr']:,.0f} 亿元, Share: {seg['share_2025_2030']}%)")

    return "\n".join(insights)


def export_to_csv(data, output_path):
    """導出為 CSV 格式"""
    analysis = analyze_market_trends(data)
    if not analysis or not analysis["segments"]:
        return

    lines = ["Segment,CAGR_2025_2030(%),5-Year_Cumulative(billion_RMB),2030_Scale,Share(%)"]
    for seg in analysis["segments"]:
        lines.append(
            f"{seg['name']},{seg['cagr_2025_2030']},{seg['cumulative_5yr']},{seg['scale_2030']},{seg['share_2025_2030']}"
        )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"\nData exported: {output_path}")


def export_to_json(data, output_path):
    """導出為 JSON 格式"""
    analysis = analyze_market_trends(data)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"Data exported: {output_path}")


if __name__ == "__main__":
    json_path = sys.argv[1] if len(sys.argv) > 1 else "ppt_analysis_result.json"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "market_analysis.csv"
    output_json = sys.argv[3] if len(sys.argv) > 3 else "market_analysis.json"

    print(f"Loading: {json_path}")
    data = load_ppt_data(json_path)

    analysis = analyze_market_trends(data)
    print(generate_insights(analysis))

    export_to_csv(data, output_csv)
    export_to_json(data, output_json)
