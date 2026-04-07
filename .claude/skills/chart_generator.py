# -*- coding: utf-8 -*-
"""
圖表生成器 - 多種類型支援
支援：柱狀圖、折線圖、餅圖、雷達圖
"""

import matplotlib
matplotlib.use('Agg')  # 非互動式後端
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
import os
from datetime import datetime


# 中文字體設置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# 配色方案
COLORS = {
    'primary': '#003366',
    'secondary': '#006699',
    'accent': '#3399FF',
    'success': '#2ECC71',
    'warning': '#F1C40F',
    'danger': '#E74C3C',
    'gray': '#95A5A6',
    'light': '#ECF0F1'
}


class ChartGenerator:
    """圖表生成器"""

    def __init__(self, output_dir="."):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def bar_chart(self, data, title, xlabel, ylabel, filename=None, top_n=10):
        """柱狀圖"""
        if filename is None:
            filename = "bar_chart.png"

        segments = data.get('segments', [])[:top_n]
        names = [s['name'][:8] for s in segments]
        values = [s['cumulative_5yr'] for s in segments]

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(range(len(names)), values, color=COLORS['primary'], alpha=0.8)

        # 數值標籤
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                   f'{val:,.0f}', ha='center', va='bottom', fontsize=8)

        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=14, fontweight='bold', color=COLORS['primary'])
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] Bar chart: {path}")
        return path

    def line_chart(self, data, title, filename=None):
        """折線圖 - 年度趨勢"""
        if filename is None:
            filename = "line_chart.png"

        segments = data.get('segments', [])[:3]
        years = ['2025', '2026', '2027', '2028', '2029', '2030']
        x = np.arange(len(years))

        fig, ax = plt.subplots(figsize=(12, 6))

        colors_list = [COLORS['primary'], COLORS['accent'], COLORS['success']]
        for i, seg in enumerate(segments):
            values = [seg['yearly_data'].get(y, 0) for y in years]
            ax.plot(x, values, marker='o', linewidth=2, markersize=6,
                   color=colors_list[i % len(colors_list)], label=seg['name'])

        ax.set_xticks(x)
        ax.set_xticklabels(years, fontsize=10)
        ax.set_xlabel('Year', fontsize=11)
        ax.set_ylabel('Market Scale (Billion RMB)', fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold', color=COLORS['primary'])
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] Line chart: {path}")
        return path

    def pie_chart(self, data, title, filename=None, top_n=6):
        """餅圖 - 市場份額"""
        if filename is None:
            filename = "pie_chart.png"

        segments = data.get('segments', [])[:top_n]

        # 計算"其他"
        all_segments = data.get('segments', [])
        if len(all_segments) > top_n:
            other_value = sum(s['cumulative_5yr'] for s in all_segments[top_n:])
            labels = [s['name'] for s in segments] + ['Others']
            sizes = [s['cumulative_5yr'] for s in segments] + [other_value]
        else:
            labels = [s['name'] for s in segments]
            sizes = [s['cumulative_5yr'] for s in segments]

        colors_pie = [COLORS['primary'], COLORS['secondary'], COLORS['accent'],
                      COLORS['success'], COLORS['warning'], COLORS['danger'], COLORS['gray']]

        fig, ax = plt.subplots(figsize=(10, 8))

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_pie[:len(sizes)],
            pctdistance=0.75
        )

        # 設置百分比文字
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        ax.legend(wedges, labels, title="Segments", loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        ax.set_title(title, fontsize=14, fontweight='bold', color=COLORS['primary'])

        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] Pie chart: {path}")
        return path

    def cagr_chart(self, data, title, filename=None, top_n=8):
        """CAGR 排名圖 - 水平柱狀圖"""
        if filename is None:
            filename = "cagr_chart.png"

        fastest = data.get('fastest_growing', [])[:top_n]
        names = [s['name'] for s in fastest]
        cagrs = [s['cagr_2025_2030'] for s in fastest]

        fig, ax = plt.subplots(figsize=(10, 6))

        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, cagrs, color=COLORS['accent'], alpha=0.8)

        # 數值標籤
        for bar, val in zip(bars, cagrs):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{val:.1f}%', va='center', fontsize=9)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10)
        ax.set_xlabel('CAGR (%)', fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold', color=COLORS['primary'])
        ax.grid(axis='x', alpha=0.3)

        # 反轉 Y軸讓最快的在上面
        ax.invert_yaxis()

        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] CAGR chart: {path}")
        return path

    def comparison_chart(self, data, title, filename=None):
        """對比圖 - 規模 vs 增速"""
        if filename is None:
            filename = "comparison_chart.png"

        segments = data.get('segments', [])[:8]

        names = [s['name'][:6] for s in segments]
        scales = [s['cumulative_5yr'] for s in segments]
        cagrs = [s['cagr_2025_2030'] for s in segments]

        x = np.arange(len(names))
        width = 0.35

        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 規模柱狀圖
        bars1 = ax1.bar(x - width/2, scales, width, label='Market Scale',
                       color=COLORS['primary'], alpha=0.8)
        ax1.set_xlabel('Segment', fontsize=11)
        ax1.set_ylabel('5Y Total (Billion RMB)', color=COLORS['primary'], fontsize=11)
        ax1.tick_params(axis='y', labelcolor=COLORS['primary'])
        ax1.set_xticks(x)
        ax1.set_xticklabels(names, rotation=45, ha='right', fontsize=9)

        # CAGR 折線
        ax2 = ax1.twinx()
        ax2.plot(x, cagrs, 'o-', color=COLORS['danger'], linewidth=2,
                markersize=8, label='CAGR')
        ax2.set_ylabel('CAGR (%)', color=COLORS['danger'], fontsize=11)
        ax2.tick_params(axis='y', labelcolor=COLORS['danger'])

        ax1.set_title(title, fontsize=14, fontweight='bold', color=COLORS['primary'])

        # 圖例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] Comparison chart: {path}")
        return path

    def dashboard(self, data, title, output_name="dashboard.png"):
        """儀表板 - 組合多圖"""
        fig = plt.figure(figsize=(16, 12))

        # 子圖佈局
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # 1. 市場份額餅圖 (左上)
        ax1 = fig.add_subplot(gs[0, 0])
        segments = data.get('segments', [])[:5]
        labels = [s['name'] for s in segments]
        sizes = [s['cumulative_5yr'] for s in segments]
        colors_pie = [COLORS['primary'], COLORS['secondary'], COLORS['accent'],
                      COLORS['success'], COLORS['warning']]
        ax1.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90,
               colors=colors_pie[:len(sizes)])
        ax1.legend(labels, loc='center left', bbox_to_anchor=(0.9, 0.5), fontsize=8)
        ax1.set_title('Market Share', fontsize=12, fontweight='bold')

        # 2. CAGR 排名 (右上)
        ax2 = fig.add_subplot(gs[0, 1])
        fastest = data.get('fastest_growing', [])[:5]
        names = [s['name'][:8] for s in fastest]
        cagrs = [s['cagr_2025_2030'] for s in fastest]
        y_pos = np.arange(len(names))
        ax2.barh(y_pos, cagrs, color=COLORS['accent'], alpha=0.8)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(names, fontsize=9)
        ax2.invert_yaxis()
        ax2.set_xlabel('CAGR (%)', fontsize=10)
        ax2.set_title('Top Growth (CAGR)', fontsize=12, fontweight='bold')

        # 3. 年度趨勢 (中)
        ax3 = fig.add_subplot(gs[1, :])
        years = ['2025', '2026', '2027', '2028', '2029', '2030']
        x = np.arange(len(years))
        colors_line = [COLORS['primary'], COLORS['accent'], COLORS['success']]
        for i, seg in enumerate(data.get('segments', [])[:3]):
            values = [seg['yearly_data'].get(y, 0) for y in years]
            ax3.plot(x, values, 'o-', linewidth=2, markersize=6,
                    label=seg['name'], color=colors_line[i])
        ax3.set_xticks(x)
        ax3.set_xticklabels(years)
        ax3.set_ylabel('Market Scale', fontsize=10)
        ax3.legend(loc='upper left')
        ax3.set_title('Annual Trend', fontsize=12, fontweight='bold')
        ax3.grid(alpha=0.3)

        # 4. 市場規模排名 (下)
        ax4 = fig.add_subplot(gs[2, :])
        segments = data.get('segments', [])[:8]
        names = [s['name'][:8] for s in segments]
        values = [s['cumulative_5yr'] for s in segments]
        bars = ax4.bar(range(len(names)), values, color=COLORS['primary'], alpha=0.8)
        ax4.set_xticks(range(len(names)))
        ax4.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
        ax4.set_ylabel('5Y Total (Billion RMB)', fontsize=10)
        ax4.set_title('Market Scale Ranking', fontsize=12, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)

        fig.suptitle(title, fontsize=16, fontweight='bold', color=COLORS['primary'])

        path = os.path.join(self.output_dir, output_name)
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] Dashboard: {path}")
        return path

    def generate_all(self, data, prefix="chart"):
        """生成所有圖表"""
        charts = {}
        charts['bar'] = self.bar_chart(data, 'Market Scale by Segment',
                                       'Segment', '5Y Total (Billion RMB)',
                                       f"{prefix}_bar.png")
        charts['line'] = self.line_chart(data, 'Annual Trend 2025-2030',
                                         f"{prefix}_line.png")
        charts['pie'] = self.pie_chart(data, 'Market Share Distribution',
                                       f"{prefix}_pie.png")
        charts['cagr'] = self.cagr_chart(data, 'CAGR Growth Ranking',
                                        f"{prefix}_cagr.png")
        charts['comparison'] = self.comparison_chart(data, 'Scale vs Growth',
                                                     f"{prefix}_comparison.png")
        charts['dashboard'] = self.dashboard(data, 'Market Analysis Dashboard',
                                            f"{prefix}_dashboard.png")
        return charts


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python chart_generator.py <market_json> [output_dir]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    generator = ChartGenerator(output_dir)
    charts = generator.generate_all(data, "market_analysis")

    print("\n" + "=" * 50)
    print("All Charts Generated!")
    print("=" * 50)
    for name, path in charts.items():
        print(f"  {name}: {os.path.basename(path)}")
