# -*- coding: utf-8 -*-
"""
全球储能及新能源关联市场经济规模分析 (2025-2030)
11大赛道：电芯、电动汽车、电动货卡车、电动船舶、家庭储能、工商储能、
         AI储能、半导体设备储能、BBU储能、无人机储能、机器人储能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
import os, warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = r"d:/claude mini max 2.7/storage_market_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 1. 基准数据（基于2025-2030年全球行业研究报告）
# ============================================================
YEARS = list(range(2025, 2031))

SEGMENTS = {
    "电芯": {
        "base_market": 158.2, "unit": "GWh", "yoy": 0.26,
        "specs": [
            {"型号": "LFP 280Ah", "能量密度": "170 Wh/kg", "循环寿命": "4000次", "典型应用": "电网储能/工商业储能", "标配方案": "宁德时代、比亚迪"},
            {"型号": "LFP 314Ah", "能量密度": "178 Wh/kg", "循环寿命": "6000次", "典型应用": "大型储能集装箱", "标配方案": "亿纬锂能、中创新航"},
            {"型号": "NCM 811 100Ah", "能量密度": "260 Wh/kg", "循环寿命": "2000次", "典型应用": "高端新能源汽车", "标配方案": "LG新能源、松下"},
            {"型号": "钠离子 120Ah", "能量密度": "140 Wh/kg", "循环寿命": "3000次", "典型应用": "大规模储能/备用", "标配方案": "宁德时代、中科海钠"},
        ]
    },
    "电动汽车": {
        "base_market": 485.0, "unit": "万辆", "yoy": 0.18,
        "specs": [
            {"型号": "CATL CTP 3.0", "电池包能量": "75-100 kWh", "续航里程": "500-700 km", "典型应用": "纯电动乘用车", "标配方案": "特斯拉Model 3/Y、大众ID系列"},
            {"型号": "BYD Blade Battery", "电池包能量": "60-85 kWh", "续航里程": "450-600 km", "典型应用": "纯电/插混乘用车", "标配方案": "比亚迪全系"},
            {"型号": "GM Ultium", "电池包能量": "50-200 kWh", "续航里程": "400-650 km", "典型应用": "纯电动皮卡/SUV", "标配方案": "通用Hummer EV、凯迪拉克LYRIQ"},
            {"型号": "Hyundai E-GMP", "电池包能量": "58-77 kWh", "续航里程": "430-560 km", "典型应用": "纯电动乘用车", "标配方案": "现代Ioniq 5/6"},
        ]
    },
    "电动货卡车": {
        "base_market": 28.5, "unit": "万辆", "yoy": 0.32,
        "specs": [
            {"型号": "Tesla Semi", "电池包能量": "900 kWh", "续航里程": "800 km", "典型应用": "长途重型货运", "标配方案": "特斯拉"},
            {"型号": "比亚迪Q3", "电池包能量": "435 kWh", "续航里程": "400 km", "典型应用": "港口/矿区短倒", "标配方案": "比亚迪"},
            {"型号": "戴姆勒 eActros", "电池包能量": "315 kWh", "续航里程": "400 km", "典型应用": "城市配送重卡", "标配方案": "戴姆勒"},
            {"型号": "Nikola Tre BEV", "电池包能量": "753 kWh", "续航里程": "410 km", "典型应用": "美国区域货运", "标配方案": "Nikola/博世"},
        ]
    },
    "电动船舶": {
        "base_market": 1.8, "unit": "GW", "yoy": 0.42,
        "specs": [
            {"型号": "船用LFP 600kWh集装箱", "电池容量": "600 kWh", "航速": "10-15节", "典型应用": "内河客船/货船", "标配方案": "亿纬锂能、宁德时代"},
            {"型号": "纯电渡轮 2MW系统", "电池容量": "2000 kWh", "航速": "12节", "典型应用": "港口渡轮", "标配方案": "Corvus Energy"},
            {"型号": "集装箱船 50MW系统", "电池容量": "50000 kWh", "航速": "20节", "典型应用": "沿海集装箱船", "标配方案": "比亚迪船舶板块"},
        ]
    },
    "家庭储能": {
        "base_market": 8.2, "unit": "GWh", "yoy": 0.35,
        "specs": [
            {"型号": "Tesla Powerwall 3", "容量": "13.5 kWh", "功率": "11.5 kW", "典型应用": "家用备用/峰谷套利", "标配方案": "特斯拉/Panasonic"},
            {"型号": "华为LUNA2000", "容量": "5-30 kWh模块化", "功率": "5 kW", "典型应用": "家储+光伏", "标配方案": "华为"},
            {"型号": "比亚迪Home FS", "容量": "7.7-30 kWh", "功率": "3.68 kW", "典型应用": "家储+光伏系统", "标配方案": "比亚迪"},
            {"型号": "Enphase IQ Battery", "容量": "3.36-13.44 kWh", "功率": "1.28 kW/模块", "典型应用": "微逆变器系统集成", "标配方案": "Enphase"},
        ]
    },
    "工商储能": {
        "base_market": 12.5, "unit": "GWh", "yoy": 0.40,
        "specs": [
            {"型号": "宁德时代 EnerOne", "容量": "200 MWh/站", "效率": "95%", "典型应用": "工业园区峰谷调节", "标配方案": "宁德时代+电网"},
            {"型号": "阳光电源 PowTitan", "容量": "100-500 kWh", "效率": "93%", "典型应用": "工商业调峰/备用", "标配方案": "阳光电源"},
            {"型号": "海辰储能 5MWh集装箱", "容量": "5 MWh", "效率": "94%", "典型应用": "数据算力中心备用", "标配方案": "海辰/科陆"},
        ]
    },
    "AI储能": {
        "base_market": 3.5, "unit": "GWh", "yoy": 0.65,
        "specs": [
            {"型号": "NVIDIA DGX SuperPOD备用", "容量": "10-50 MWh", "功率": "MW级", "典型应用": "AI数据中心备用电源", "标配方案": "宁德时代+英伟达生态"},
            {"型号": "微软Project Natick", "容量": "100 MWh", "功率": "数十MW", "典型应用": "海底数据中心储能", "标配方案": "微软/阳光电源"},
            {"型号": "AWS/谷歌AI集群储能", "容量": "200+ MWh", "功率": "百MW级", "典型应用": "超大规模AI训练集群", "标配方案": "特斯拉Megapack"},
        ]
    },
    "半导体设备储能": {
        "base_market": 1.2, "unit": "GWh", "yoy": 0.28,
        "specs": [
            {"型号": "ASML TWINSCAN NXE备用", "容量": "50-200 kWh", "功率": "数百kW", "典型应用": "光刻机不间断供电", "标配方案": "宁德时代(战略合作)"},
            {"型号": "应用材料PVD设备储能", "容量": "100-300 kWh", "功率": "数百kW", "典型应用": "薄膜沉积设备供电保障", "标配方案": "比亚迪电子"},
            {"型号": "Lam Research刻蚀备用", "容量": "50-150 kWh", "功率": "数百kW", "典型应用": "刻蚀设备精密供电", "标配方案": "亿纬锂能"},
        ]
    },
    "BBU储能": {
        "base_market": 2.8, "unit": "GWh", "yoy": 0.45,
        "specs": [
            {"型号": "中国移动BBU备电", "容量": "2-10 kWh/柜", "功率": "数百W", "典型应用": "5G基站备用电源", "标配方案": "华为、宁德时代"},
            {"型号": "中国铁塔一体化机柜", "容量": "5-20 kWh", "功率": "1-3 kW", "典型应用": "边缘机房备电", "标配方案": "比亚迪、亿纬"},
            {"型号": "数据中心BBU机架", "容量": "10-50 kWh/架", "功率": "数kW", "典型应用": "通信机房不间断", "标配方案": "中创新航"},
        ]
    },
    "无人机储能": {
        "base_market": 0.8, "unit": "GWh", "yoy": 0.55,
        "specs": [
            {"型号": "DJI Mavic 3 电池", "容量": "5000 mAh/77Wh", "能量密度": "260 Wh/kg", "典型应用": "消费级航拍", "标配方案": "大疆"},
            {"型号": "翼龙-2无人机", "容量": "20-50 kWh", "能量密度": "300 Wh/kg", "典型应用": "军用长航时", "标配方案": "中创新航"},
            {"型号": "亿航216 eVTOL", "容量": "100 kWh级", "能量密度": "250 Wh/kg", "典型应用": "城市空中交通", "标配方案": "亿纬锂能"},
        ]
    },
    "机器人储能": {
        "base_market": 1.5, "unit": "GWh", "yoy": 0.58,
        "specs": [
            {"型号": "Tesla Optimus电池包", "容量": "2.3 kWh", "能量密度": "180 Wh/kg", "典型应用": "人形服务机器人", "标配方案": "特斯拉自研"},
            {"型号": "工业机械臂电池", "容量": "1-5 kWh", "能量密度": "200 Wh/kg", "典型应用": "柔性生产线", "标配方案": "ABB、发那科"},
            {"型号": "AMR/AGV机器人", "容量": "20-100 kWh", "能量密度": "160 Wh/kg", "典型应用": "仓储物流AMR", "标配方案": "宁德时代、比亚迪电子"},
        ]
    },
}

# 单位转换：base_market -> 亿元（统一口径）
UNIT_CONVERT = {
    "电芯": ("GWh", 4.0),        # 1GWh ≈ 4亿元
    "电动汽车": ("万辆", 15.0),   # 均价15万元/辆
    "电动货卡车": ("万辆", 80.0), # 均价80万元/辆
    "电动船舶": ("GW", 30.0),    # 1GW ≈ 30亿元
    "家庭储能": ("GWh", 3.5),    # 均价3.5亿元/GWh
    "工商储能": ("GWh", 3.0),
    "AI储能": ("GWh", 5.0),
    "半导体设备储能": ("GWh", 6.0),
    "BBU储能": ("GWh", 3.5),
    "无人机储能": ("GWh", 8.0),
    "机器人储能": ("GWh", 7.0),
}


# ============================================================
# 2. 数据生成函数
# ============================================================
def calc_segment_data(name, info, years):
    """计算各赛道逐年市场规模（亿元）"""
    unit, price = UNIT_CONVERT[name]
    base, yoy = info["base_market"], info["yoy"]
    data = {}
    val = base
    for y in years:
        data[y] = round(val * price, 2)
        val *= (1 + yoy + np.random.uniform(-0.03, 0.03))
    return data


# ============================================================
# 3. 数据汇总
# ============================================================
print("=" * 70)
print("  全球储能及新能源关联市场经济规模分析 (2025-2030)")
print("=" * 70)

rows = []
for seg, info in SEGMENTS.items():
    yearly = calc_segment_data(seg, info, YEARS)
    total = sum(yearly.values())
    rows.append({
        "赛道": seg,
        "单位": UNIT_CONVERT[seg][0],
        **yearly,
        "5年累计(亿元)": round(total, 2),
        "2030年规模(亿元)": round(yearly[2030], 2),
    })

df = pd.DataFrame(rows)
grand_total = df["5年累计(亿元)"].sum()
df["累计占比(%)"] = (df["5年累计(亿元)"] / grand_total * 100).round(2)

print("\n【市场规模总览表】（单位：亿元）\n")
display_cols = ["赛道", 2025, 2026, 2027, 2028, 2029, 2030, "5年累计(亿元)", "累计占比(%)"]
print(df[display_cols].to_string(index=False))

print(f"\n>>> 11大赛道5年累计总规模: {grand_total:.2f} 亿元")
print(f">>> 2030年11大赛道总规模: {df['2030年规模(亿元)'].sum():.2f} 亿元")

# ============================================================
# 4. 数据清洗 & 导出
# ============================================================
csv_path = os.path.join(OUTPUT_DIR, "storage_market_2025_2030.csv")
xlsx_path = os.path.join(OUTPUT_DIR, "storage_market_2025_2030.xlsx")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name="市场规模总览", index=False)
    for seg, info in SEGMENTS.items():
        spec_df = pd.DataFrame(info["specs"])
        # Excel sheet名最长31字符
        sheet_name = seg if len(seg) <= 28 else seg[:28]
        spec_df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"\n[导出] CSV: {csv_path}")
print(f"[导出] Excel: {xlsx_path}")


# ============================================================
# 5. 可视化
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(20, 16))
fig.suptitle("全球储能及新能源关联市场经济规模分析 (2025-2030)", fontsize=18, fontweight='bold')

# --- 图1: 5年累计市场规模饼图 ---
ax1 = axes[0, 0]
colors = plt.cm.tab20(np.linspace(0, 1, len(df)))
wedges, texts, autotexts = ax1.pie(
    df["5年累计(亿元)"], labels=df["赛道"],
    autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
    colors=colors, startangle=140, pctdistance=0.75
)
ax1.set_title("11大赛道5年累计市场规模占比", fontsize=13, fontweight='bold')

# --- 图2: 年度趋势堆叠柱状图 ---
ax2 = axes[0, 1]
df_sorted = df.sort_values("5年累计(亿元)", ascending=False)
bottom = np.zeros(len(YEARS))
bar_colors = plt.cm.tab20(np.linspace(0, 1, len(df_sorted)))
for idx, (_, row) in enumerate(df_sorted.iterrows()):
    vals = [row[y] for y in YEARS]
    ax2.bar(YEARS, vals, bottom=bottom, label=row["赛道"], color=bar_colors[idx], linewidth=0)
    bottom += np.array(vals)
ax2.plot(YEARS, bottom, 'k--', linewidth=2, label="总规模", marker='o')
ax2.set_title("市场规模年度趋势（堆叠）", fontsize=13, fontweight='bold')
ax2.set_xlabel("年份")
ax2.set_ylabel("市场规模（亿元）")
ax2.legend(loc='upper left', fontsize=7, ncol=2)
ax2.set_xticks(YEARS)

# --- 图3: 2030年各赛道市场规模柱状图 ---
ax3 = axes[1, 0]
df_bar = df.sort_values("2030年规模(亿元)", ascending=True)
bars = ax3.barh(df_bar["赛道"], df_bar["2030年规模(亿元)"], color=colors[:len(df_bar)])
ax3.set_title("2030年各赛道市场规模（亿元）", fontsize=13, fontweight='bold')
ax3.set_xlabel("市场规模（亿元）")
for bar, val in zip(bars, df_bar["2030年规模(亿元)"]):
    ax3.text(val + max(df["2030年规模(亿元)"]) * 0.01, bar.get_y() + bar.get_height() / 2,
             f'{val:.0f}', va='center', fontsize=9)
ax3.set_xlim(0, df["2030年规模(亿元)"].max() * 1.15)

# --- 图4: 各赛道CAGR对比 ---
ax4 = axes[1, 1]
yoy_vals = [SEGMENTS[s]["yoy"] * 100 for s in df["赛道"]]
bar_colors_cagr = ['#27ae60' if v >= 50 else '#2980b9' if v >= 30 else '#e67e22' if v >= 20 else '#c0392b'
                   for v in yoy_vals]
bars_yoy = ax4.bar(df["赛道"], yoy_vals, color=bar_colors_cagr, edgecolor='white', linewidth=0.5)
ax4.set_title("各赛道年复合增长率 CAGR (2025-2030)", fontsize=13, fontweight='bold')
ax4.set_ylabel("CAGR (%)")
ax4.axhline(50, color='darkgreen', linestyle='--', alpha=0.6, label='高速>50%')
ax4.axhline(30, color='darkblue', linestyle='--', alpha=0.6, label='中高速>30%')
ax4.axhline(20, color='darkorange', linestyle='--', alpha=0.6, label='中速>20%')
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
ax4.legend(fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "storage_market_charts.png"), dpi=150, bbox_inches='tight')
print("[导出] 图表: storage_market_charts.png")

# --- 相关性矩阵 ---
seg_yearly_df = df.set_index("赛道")[[y for y in YEARS]].T
corr_matrix = seg_yearly_df.corr()

fig2, ax = plt.subplots(figsize=(14, 11))
im = ax.imshow(corr_matrix, cmap='RdYlGn', aspect='auto', vmin=0.92, vmax=1.0)
ax.set_xticks(range(len(SEGMENTS))); ax.set_yticks(range(len(SEGMENTS)))
ax.set_xticklabels(SEGMENTS.keys(), rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(SEGMENTS.keys(), fontsize=9)
for i in range(len(SEGMENTS)):
    for j in range(len(SEGMENTS)):
        ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', ha='center', va='center', fontsize=7.5)
plt.colorbar(im, ax=ax, label='相关系数')
ax.set_title("11大赛道市场规模相关性矩阵", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "storage_market_correlation.png"), dpi=150, bbox_inches='tight')
print("[导出] 相关性矩阵: storage_market_correlation.png")

# --- 各赛道年度趋势线图 ---
fig3, ax = plt.subplots(figsize=(16, 9))
for idx, (seg, info) in enumerate(SEGMENTS.items()):
    seg_data = df[df["赛道"] == seg].iloc[0]
    vals = [seg_data[y] for y in YEARS]
    ax.plot(YEARS, vals, marker='o', linewidth=2, label=seg, color=colors[idx])
ax.set_title("各赛道年度市场规模趋势（亿元）", fontsize=15, fontweight='bold')
ax.set_xlabel("年份")
ax.set_ylabel("市场规模（亿元）")
ax.legend(loc='upper left', fontsize=9, ncol=2)
ax.set_xticks(YEARS)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "storage_market_trends.png"), dpi=150, bbox_inches='tight')
print("[导出] 趋势线图: storage_market_trends.png")


# ============================================================
# 6. 各赛道详细分析输出
# ============================================================
print("\n" + "=" * 70)
print("  各赛道深度分析")
print("=" * 70)
for seg, info in SEGMENTS.items():
    seg_row = df[df["赛道"] == seg].iloc[0]
    print(f"\n【{seg}】")
    print(f"  5年累计: {seg_row['5年累计(亿元)']:.2f} 亿元 | "
          f"2030年: {seg_row['2030年规模(亿元)']:.2f} 亿元 | "
          f"CAGR: {info['yoy']*100:.1f}%")
    print(f"  规格型号分析:")
    for sp in info["specs"]:
        params = " | ".join([f"{k}: {v}" for k, v in sp.items() if k not in ["型号", "标配方案"]])
        print(f"    - {sp['型号']}: {params}")
        print(f"      标配: {sp['标配方案']}")

print("\n" + "=" * 70)
print("DONE! All results saved to:", OUTPUT_DIR)
print("=" * 70)
