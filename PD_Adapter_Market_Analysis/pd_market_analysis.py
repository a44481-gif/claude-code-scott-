#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PD 大電流適配器集成技術應用市場分析 - 數據視覺化腳本
Global PD High-Current Adapter Integration Technology Market Analysis - Data Visualization Script
生成日期: 2025年4月
"""

import json
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving PNG files
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import font_manager
import os

# ==================== 設置中文字體 ====================
def setup_chinese_font():
    """配置支持中文的字体"""
    # 尝试多种中文字体
    font_paths = [
        'C:/Windows/Fonts/msjh.ttc',  # Microsoft JhengHei (Traditional Chinese)
        'C:/Windows/Fonts/simhei.ttf',  # SimHei (Simplified Chinese)
        'C:/Windows/Fonts/simsun.ttc',  # SimSun
        'C:/Windows/Fonts/arial.ttf',  # Fallback
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # Linux
        '/System/Library/Fonts/STHeiti Light.ttc',  # macOS
    ]

    found_fonts = []
    for fp in font_paths:
        if os.path.exists(fp):
            found_fonts.append(fp)
            font_manager.fontManager.addfont(fp)

    # 设置字体
    font_names = ['Microsoft JhengHei', 'SimHei', 'WenQuanYi Micro Hei', 'Heiti TC', 'Arial']
    for fname in font_names:
        try:
            plt.rcParams['font.family'] = fname
            plt.rcParams['axes.unicode_minus'] = False
            break
        except:
            continue

    # 使用默认sans-serif
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False

setup_chinese_font()

# ==================== 顏色配置 ====================
COLORS = {
    'bg_dark': '#1a1a2e',
    'bg_darker': '#16213e',
    'cyan': '#00d4ff',
    'coral': '#ff6b6b',
    'yellow': '#ffd93d',
    'green': '#6bcb77',
    'purple': '#a855f7',
    'blue': '#3b82f6',
    'orange': '#f97316',
    'pink': '#ec4899',
    'white': '#ffffff',
    'gray': '#9ca3af',
    'light_gray': '#e5e7eb'
}

# ==================== 市場數據 ====================
# 市場規模 (USD Billions)
market_size = {2025: 14.2, 2026: 17.1, 2027: 20.6, 2028: 24.0, 2029: 26.8, 2030: 28.7}

# 出貨量 (Million units)
shipments = {2025: 485, 2026: 572, 2027: 672, 2028: 778, 2029: 878, 2030: 978}

# 集成技術滲透率 (%)
integration_rate = {2025: 45, 2026: 58, 2027: 72, 2028: 82, 2029: 88, 2030: 92}

# 功率結構 2025
power_2025 = {"65W": 52, "100W": 28, "140W": 12, "240W": 8}
# 功率結構 2030
power_2030 = {"65W": 35, "100W": 30, "140W": 20, "240W": 15}

# 區域市場份額 2025
region_2025 = {"中國": 48, "北美": 20, "歐洲": 17, "東南亞": 8, "日韓": 5, "其他": 2}
# 區域市場份額 2030
region_2030 = {"中國": 45, "北美": 19, "歐洲": 20, "東南亞": 10, "日韓": 4, "其他": 2}

# CAGR by power tier
cagr_power = {"65W": 8.2, "100W": 16.5, "140W": 28.7, "240W": 32.4}

# 技術路線圖
tech_roadmap = {
    2025: {"integration": "PFC+LLC dual-chip", "freq_khz": "200-500", "density_wpc": "20-25", "protocol": "PD3.1+UFCS兴起"},
    2026: {"integration": "GaN co-pack主流", "freq_khz": "500-1000", "density_wpc": "25-32", "protocol": "PD3.1+UFCS必备"},
    2027: {"integration": "Single GaN SoC", "freq_khz": "1000-2000", "density_wpc": "32-40", "protocol": "多协议融合"},
    2028: {"integration": "Full digital single chip", "freq_khz": "2000-3000", "density_wpc": "40-50", "protocol": "AI感知功率分配"},
    2029: {"integration": "GaN+SiC hybrid", "freq_khz": "3000-5000", "density_wpc": "50-60", "protocol": "预测性功率管理"},
    2030: {"integration": "Monolithic GaN SoC", "freq_khz": "5000-10000", "density_wpc": "60-80", "protocol": "传感+控制全集成"},
}

# 競爭格局數據
competitive_data = {
    "Power Integrations": {"market_share": 22, "growth": 12, "strength": "可靠性"},
    "Navitas": {"market_share": 18, "growth": 25, "strength": "GaN整合"},
    "Infineon": {"market_share": 20, "growth": 8, "strength": "寬禁帶最全"},
    "TI": {"market_share": 15, "growth": 5, "strength": "模擬+數位"},
    "南芯半導體": {"market_share": 8, "growth": 35, "strength": "性價比最優"},
    "智融科技": {"market_share": 6, "growth": 40, "strength": "多口市場"},
    "英集芯": {"market_share": 5, "growth": 30, "strength": "最低成本"},
    "東科半導體": {"market_share": 6, "growth": 28, "strength": "中國最佳ACF"},
}

# ==================== 公共樣式配置 ====================
def apply_dark_theme():
    """应用深色主题样式"""
    plt.style.use('dark_background')
    plt.rcParams['figure.facecolor'] = COLORS['bg_dark']
    plt.rcParams['axes.facecolor'] = COLORS['bg_darker']
    plt.rcParams['axes.edgecolor'] = COLORS['gray']
    plt.rcParams['axes.labelcolor'] = COLORS['white']
    plt.rcParams['xtick.color'] = COLORS['gray']
    plt.rcParams['ytick.color'] = COLORS['gray']
    plt.rcParams['text.color'] = COLORS['white']
    plt.rcParams['grid.color'] = '#374151'
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['legend.facecolor'] = COLORS['bg_dark']
    plt.rcParams['legend.edgecolor'] = COLORS['gray']

def save_figure(fig, filename):
    """保存图表为PNG文件"""
    fig.savefig(filename, dpi=300, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none',
                format='png', pil_kwargs={'optimize': True})
    plt.close(fig)
    print(f"已保存: {filename}")

# ==================== 圖表1: 全球市場規模 2025-2030 ====================
def create_market_size_chart():
    """生成全球市場規模柱狀圖"""
    apply_dark_theme()

    years = list(market_size.keys())
    values = list(market_size.values())

    fig, ax = plt.subplots(figsize=(12, 7))

    # 创建渐变效果的颜色
    bar_colors = [COLORS['cyan'], COLORS['cyan'], COLORS['green'],
                  COLORS['green'], COLORS['yellow'], COLORS['coral']]

    bars = ax.bar(years, values, color=bar_colors, width=0.6,
                  edgecolor='white', linewidth=0.5)

    # 在柱子上添加数值标签
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'${val}B',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold', color=COLORS['white'])

    # 设置坐标轴
    ax.set_xlabel('年份 (Year)', fontsize=12, fontweight='bold')
    ax.set_ylabel('市場規模 (USD Billions)', fontsize=12, fontweight='bold')
    ax.set_title('全球PD適配器市場規模 2025-2030\nGlobal PD Adapter Market Size',
                 fontsize=16, fontweight='bold', pad=20)

    # 设置Y轴范围
    ax.set_ylim(0, max(values) * 1.15)

    # 添加网格
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)

    # 添加趋势线
    z = np.polyfit(years, values, 1)
    p = np.poly1d(z)
    ax.plot(years, p(years), '--', color=COLORS['coral'], alpha=0.7,
            linewidth=2, label=f'趨勢線 (CAGR ~15%)')

    # 添加图例
    ax.legend(loc='upper left', fontsize=10)

    # 添加说明文字
    ax.text(0.98, 0.02, '數據來源: 市場研究估算 | Source: Market Research Estimates',
            transform=ax.transAxes, fontsize=8, color=COLORS['gray'],
            ha='right', va='bottom')

    plt.tight_layout()
    save_figure(fig, 'chart1_market_size_2025_2030.png')

# ==================== 圖表2: 功率結構餅圖 ====================
def create_power_structure_pies():
    """生成功率結構對比餅圖 (2025 vs 2030)"""
    apply_dark_theme()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    colors = [COLORS['cyan'], COLORS['green'], COLORS['yellow'], COLORS['coral']]
    explode = (0.02, 0.02, 0.05, 0.08)  # 突出显示高功率

    # 2025 饼图
    labels_2025 = list(power_2025.keys())
    sizes_2025 = list(power_2025.values())
    wedges1, texts1, autotexts1 = ax1.pie(sizes_2025, explode=explode, labels=labels_2025,
                                           colors=colors, autopct='%1.0f%%',
                                           shadow=True, startangle=90,
                                           textprops={'color': COLORS['white'], 'fontsize': 11})
    for autotext in autotexts1:
        autotext.set_color(COLORS['bg_dark'])
        autotext.set_fontweight('bold')
    ax1.set_title('2025 功率結構\nPower Structure 2025', fontsize=14, fontweight='bold', pad=15)

    # 2030 饼图
    labels_2030 = list(power_2030.keys())
    sizes_2030 = list(power_2030.values())
    wedges2, texts2, autotexts2 = ax2.pie(sizes_2030, explode=explode, labels=labels_2030,
                                           colors=colors, autopct='%1.0f%%',
                                           shadow=True, startangle=90,
                                           textprops={'color': COLORS['white'], 'fontsize': 11})
    for autotext in autotexts2:
        autotext.set_color(COLORS['bg_dark'])
        autotext.set_fontweight('bold')
    ax2.set_title('2030 功率結構\nPower Structure 2030', fontsize=14, fontweight='bold', pad=15)

    # 添加共同图例
    fig.legend(wedges2, [f'{l} (CAGR: {cagr_power[l]}%)' for l in labels_2030],
               loc='lower center', ncol=4, fontsize=10,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('PD適配器功率結構演變 2025→2030\nEvolution of Power Structure',
                 fontsize=16, fontweight='bold', y=1.02)

    plt.tight_layout()
    save_figure(fig, 'chart2_power_structure_2025_vs_2030.png')

# ==================== 圖表3: 區域市場份額 ====================
def create_regional_share_chart():
    """生成區域市場份額分組柱狀圖"""
    apply_dark_theme()

    fig, ax = plt.subplots(figsize=(12, 7))

    regions = list(region_2025.keys())
    values_2025 = list(region_2025.values())
    values_2030 = list(region_2030.values())

    x = np.arange(len(regions))
    width = 0.35

    bars1 = ax.bar(x - width/2, values_2025, width, label='2025',
                   color=COLORS['cyan'], edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, values_2030, width, label='2030',
                   color=COLORS['green'], edgecolor='white', linewidth=0.5)

    # 添加数值标签
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, color=COLORS['white'])

    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, color=COLORS['white'])

    ax.set_xlabel('地區 (Region)', fontsize=12, fontweight='bold')
    ax.set_ylabel('市場份額 (Market Share %)', fontsize=12, fontweight='bold')
    ax.set_title('區域市場份額分佈 2025 vs 2030\nRegional Market Share Distribution',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=11)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_ylim(0, 60)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)

    # 添加注释 - 增长最快区域
    ax.annotate('↑ 增速最快\nCAGR 18%+',
                xy=(3, 10), xytext=(3.5, 25),
                fontsize=9, color=COLORS['green'],
                arrowprops=dict(arrowstyle='->', color=COLORS['green']))

    plt.tight_layout()
    save_figure(fig, 'chart3_regional_market_share_2025_2030.png')

# ==================== 圖表4: 集成技術滲透率 ====================
def create_integration_rate_chart():
    """生成集成技術滲透率折線圖"""
    apply_dark_theme()

    fig, ax = plt.subplots(figsize=(12, 7))

    years = list(integration_rate.keys())
    rates = list(integration_rate.values())

    # 绘制主折线
    ax.plot(years, rates, marker='o', markersize=10, linewidth=3,
            color=COLORS['cyan'], label='集成技術滲透率')

    # 填充区域
    ax.fill_between(years, rates, alpha=0.2, color=COLORS['cyan'])

    # 添加数据标签
    for x, y in zip(years, rates):
        ax.annotate(f'{y}%',
                    xy=(x, y),
                    xytext=(0, 12),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color=COLORS['white'],
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['bg_dark'],
                              edgecolor=COLORS['cyan'], alpha=0.8))

    # 添加里程碑线
    ax.axhline(y=50, color=COLORS['yellow'], linestyle='--', alpha=0.5, linewidth=1.5)
    ax.text(2025.3, 51, '50% 臨界點', fontsize=9, color=COLORS['yellow'])

    ax.axhline(y=80, color=COLORS['green'], linestyle='--', alpha=0.5, linewidth=1.5)
    ax.text(2025.3, 81, '80% 主流應用', fontsize=9, color=COLORS['green'])

    ax.set_xlabel('年份 (Year)', fontsize=12, fontweight='bold')
    ax.set_ylabel('滲透率 (Penetration Rate %)', fontsize=12, fontweight='bold')
    ax.set_title('PD適配器集成技術滲透率 2025-2030\nIntegration Technology Penetration Rate',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    ax.set_xlim(2024.5, 2030.5)
    ax.grid(linestyle='--', alpha=0.3)
    ax.legend(loc='lower right', fontsize=11)
    ax.set_xticks(years)

    # 添加说明
    ax.text(0.98, 0.02,
            '預測依據: GaN成本下降、EU法規、功率升級需求\nDrivers: GaN cost decline, EU regulations, Power upgrade demand',
            transform=ax.transAxes, fontsize=9, color=COLORS['gray'],
            ha='right', va='bottom')

    plt.tight_layout()
    save_figure(fig, 'chart4_integration_penetration_rate_2025_2030.png')

# ==================== 圖表5: 技術路線圖 ====================
def create_tech_roadmap_chart():
    """生成技術路線圖時間軸"""
    apply_dark_theme()

    fig, ax = plt.subplots(figsize=(14, 10))

    years = list(tech_roadmap.keys())
    y_positions = list(range(len(years)))

    # 绘制主时间轴
    ax.plot([0, 100], [len(years)-1, len(years)-1], color=COLORS['gray'],
            linewidth=3, zorder=1, alpha=0.3)

    # 为每一年添加信息块
    bar_heights = [0.6, 0.6, 0.6, 0.6, 0.6, 0.6]

    for i, (year, data) in enumerate(tech_roadmap.items()):
        y = len(years) - 1 - i

        # 绘制年份节点
        ax.scatter([10], [y], s=200, color=COLORS['cyan'], zorder=3, edgecolor='white', linewidth=2)
        ax.text(10, y, str(year), ha='center', va='center',
                fontsize=12, fontweight='bold', color=COLORS['bg_dark'], zorder=4)

        # 绘制信息框
        integration_text = f"{data['integration']}"
        freq_text = f"頻率: {data['freq_khz']} kHz"
        density_text = f"功率密度: {data['density_wpc']} W/in³"
        protocol_text = f"協議: {data['protocol']}"

        # 左侧信息
        info_x = 18
        ax.text(info_x, y + 0.2, integration_text,
                fontsize=11, fontweight='bold', color=COLORS['white'],
                ha='left', va='center')
        ax.text(info_x, y - 0.1, freq_text,
                fontsize=10, color=COLORS['green'],
                ha='left', va='center')
        ax.text(info_x + 35, y - 0.1, density_text,
                fontsize=10, color=COLORS['yellow'],
                ha='left', va='center')

        # 绘制进度条表示功率密度
        density_value = float(data['density_wpc'].split('-')[1]) / 100
        ax.barh(y, density_value * 30, left=info_x + 75, height=0.4,
                color=COLORS['coral'], alpha=0.8, zorder=2)

        # 协议标签
        ax.text(90, y, protocol_text,
                fontsize=10, color=COLORS['purple'],
                ha='right', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['bg_dark'],
                          edgecolor=COLORS['purple'], alpha=0.7))

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.8, len(years) - 0.2)
    ax.axis('off')
    ax.set_title('PD適配器集成技術路線圖 2025-2030\nIntegration Technology Roadmap',
                 fontsize=16, fontweight='bold', pad=20)

    # 添加图例说明
    legend_text = '''
    關鍵里程碑:
    • 2026: GaN共封裝成為主流
    • 2028: 全數字控制單晶片
    • 2030: 單片GaN SoC實現
    '''
    ax.text(0.02, 0.02, legend_text, transform=ax.transAxes,
            fontsize=9, color=COLORS['gray'], va='bottom',
            bbox=dict(boxstyle='round', facecolor=COLORS['bg_dark'],
                      edgecolor=COLORS['gray'], alpha=0.8))

    plt.tight_layout()
    save_figure(fig, 'chart5_technology_roadmap_2025_2030.png')

# ==================== 圖表6: 競爭格局矩陣 ====================
def create_competitive_landscape_chart():
    """生成競爭格局熱力圖"""
    apply_dark_theme()

    fig, ax = plt.subplots(figsize=(14, 8))

    companies = list(competitive_data.keys())
    companies_en = ['Power Int.', 'Navitas', 'Infineon', 'TI', 'SouthChip', 'iSmart', 'Inno', 'Dongkee']

    market_shares = [d['market_share'] for d in competitive_data.values()]
    growths = [d['growth'] for d in competitive_data.values()]

    # 合并数据用于颜色编码
    combined_scores = [(ms * 0.6 + g * 0.4) for ms, g in zip(market_shares, growths)]

    # 创建水平柱状图
    y_pos = np.arange(len(companies))
    bars = ax.barh(y_pos, market_shares, color=[COLORS['cyan'] if g >= 20 else COLORS['green']
                                                 if g >= 10 else COLORS['yellow']
                                                 for g in growths],
                   edgecolor='white', linewidth=0.5, height=0.6)

    # 在柱子上添加数值
    for bar, ms, g in zip(bars, market_shares, growths):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                f'{ms}% | {g}%↑', ha='left', va='center',
                fontsize=10, fontweight='bold', color=COLORS['white'])

    # 添加公司英文名
    for i, en_name in enumerate(companies_en):
        ax.text(-2, i, en_name, ha='right', va='center', fontsize=10, color=COLORS['gray'])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(companies)
    ax.set_xlabel('市場份額 (Market Share %)', fontsize=12, fontweight='bold')
    ax.set_title('PD晶片市場競爭格局 2025\nCompetitive Landscape Matrix',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 30)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.invert_yaxis()

    # 添加图例
    legend_patches = [
        mpatches.Patch(color=COLORS['cyan'], label='高增長 (>20%)'),
        mpatches.Patch(color=COLORS['green'], label='中增長 (10-20%)'),
        mpatches.Patch(color=COLORS['yellow'], label='穩健 (<10%)')
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=10)

    # 添加说明
    ax.text(0.98, 0.02, '注: 數值為市場份額 | 箭頭表示同比增長率\nNote: Values indicate market share | Arrows show YoY growth rate',
            transform=ax.transAxes, fontsize=8, color=COLORS['gray'],
            ha='right', va='bottom')

    plt.tight_layout()
    save_figure(fig, 'chart6_competitive_landscape_matrix.png')

# ==================== 生成JSON數據文件 ====================
def generate_json_data():
    """生成完整的JSON數據文件"""
    full_data = {
        "report_info": {
            "title": "PD大電流適配器集成技術應用市場分析 2025-2030",
            "generated_date": "2025-04-05",
            "data_source": "市場研究估算"
        },
        "market_overview": {
            "market_size_usd_billion": market_size,
            "shipments_million_units": shipments,
            "integration_penetration_rate": integration_rate,
            "base_year_cagr": 15.2
        },
        "power_structure": {
            "2025": power_2025,
            "2030": power_2030,
            "cagr_by_tier": cagr_power
        },
        "regional_market": {
            "2025": region_2025,
            "2030": region_2030
        },
        "technology_roadmap": tech_roadmap,
        "competitive_landscape": {
            company: {
                "market_share_percent": data["market_share"],
                "yoy_growth_percent": data["growth"],
                "core_strength": data["strength"]
            }
            for company, data in competitive_data.items()
        },
        "application_segments": {
            "AI_PC_Laptop": {"power_range": "140-240W", "cagr": 28.7, "market_size_billion": 45},
            "Flagship_Smartphone": {"power_range": "100-150W", "cagr": 8, "market_size_billion": 38},
            "Gaming_Devices": {"power_range": "45-240W", "cagr": 25, "market_size_billion": 12},
            "AI_Terminals": {"power_range": "100-240W", "cagr": 45, "market_size_billion": 5},
            "Industrial": {"power_range": "65-240W", "cagr": 10, "market_size_billion": 8},
            "Medical": {"power_range": "65-150W", "cagr": 14, "market_size_billion": 5},
            "Commercial_Display": {"power_range": "65-240W", "cagr": 18, "market_size_billion": 12},
            "EV_800V": {"power_range": "200-240W", "cagr": 38, "market_size_billion": 15},
            "Outdoor_Storage": {"power_range": "100-240W", "cagr": 30, "market_size_billion": 8}
        },
        "cost_analysis": {
            "65W": {"low_end": 3, "mid": 6, "high_end": 12, "avg": 6.2, "chip_bom": "0.8-1.5"},
            "100W": {"low_end": 6, "mid": 12, "high_end": 25, "avg": 13.5, "chip_bom": "1.5-2.5"},
            "140W": {"low_end": 10, "mid": 18, "high_end": 38, "avg": 19.8, "chip_bom": "2.5-4.0"},
            "240W": {"low_end": 18, "mid": 30, "high_end": 55, "avg": 32.5, "chip_bom": "4.0-7.0"}
        },
        "key_insights": {
            "investment_opportunities": [
                "GaN集成晶片爆發期 (2025-2027)",
                "AI PC 140W+ 市場高速增長",
                "汽車V2L 200W+ 新賽道"
            ],
            "key_risks": [
                "專利叢林加劇",
                "中國廠商價格內捲",
                "地緣政治風險"
            ]
        }
    }

    json_path = 'pd_market_data.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    print(f"已保存: {json_path}")

# ==================== 主程序 ====================
def main():
    """主程序入口"""
    print("=" * 60)
    print("PD 大電流適配器集成技術市場分析 - 數據視覺化")
    print("=" * 60)

    # 创建输出目录
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(output_dir)

    print("\n[1/7] 生成市場規模柱狀圖...")
    create_market_size_chart()

    print("[2/7] 生成功率結構餅圖...")
    create_power_structure_pies()

    print("[3/7] 生成區域市場份額圖...")
    create_regional_share_chart()

    print("[4/7] 生成集成技術滲透率圖...")
    create_integration_rate_chart()

    print("[5/7] 生成技術路線圖...")
    create_tech_roadmap_chart()

    print("[6/7] 生成競爭格局矩陣...")
    create_competitive_landscape_chart()

    print("[7/7] 生成JSON數據文件...")
    generate_json_data()

    print("\n" + "=" * 60)
    print("所有視覺化文件已生成完成!")
    print("=" * 60)
    print("\n生成的文件:")
    print("  • chart1_market_size_2025_2030.png")
    print("  • chart2_power_structure_2025_vs_2030.png")
    print("  • chart3_regional_market_share_2025_2030.png")
    print("  • chart4_integration_penetration_rate_2025_2030.png")
    print("  • chart5_technology_roadmap_2025_2030.png")
    print("  • chart6_competitive_landscape_matrix.png")
    print("  • pd_market_data.json")

if __name__ == "__main__":
    main()
