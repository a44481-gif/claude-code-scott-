# -*- coding: utf-8 -*-
"""
IT Power IC 分析工具 - 電源管理IC技術分析
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ICComponent:
    """IC元件"""
    name: str
    part_number: str
    category: str  # buck, boost, ldo, buck_boost, motor_driver, load_switch
    vin_range: Tuple[float, float]  # V
    vout_range: Tuple[float, float]  # V
    iout_max: float  # A
    efficiency: float  # %
    package: str  # SOP-8, QFN, etc
    features: List[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []


class PowerICAnalyzer:
    """電源IC分析工具"""

    # 關鍵參數評估維度
    DIMENSIONS = {
        "效率": {"weight": 0.25, "unit": "%", "higher_better": True},
        "輸入電壓範圍": {"weight": 0.15, "unit": "V", "higher_better": True},
        "輸出電流能力": {"weight": 0.20, "unit": "A", "higher_better": True},
        "功率密度": {"weight": 0.20, "unit": "W/in³", "higher_better": True},
        "性價比": {"weight": 0.20, "unit": "分", "higher_better": True},
    }

    # 常見應用場景
    APPLICATIONS = {
        "穿戴裝置": {"vin": (2.5, 5.5), "vout": (1.2, 3.3), "iout": (0.5, 2), "priority": ["LDO", "Buck"]},
        "物聯網設備": {"vin": (3.0, 5.0), "vout": (1.8, 3.3), "iout": (1, 3), "priority": ["Buck", "LDO"]},
        "工業控制": {"vin": (8, 48), "vout": (5, 24), "iout": (2, 10), "priority": ["Buck", "Boost", "Motor Driver"]},
        "汽車電子": {"vin": (9, 16), "vout": (3.3, 12), "iout": (3, 20), "priority": ["Buck", "LDO", "Load Switch"]},
        "伺服器/資料中心": {"vin": (12, 48), "vout": (0.6, 12), "iout": (10, 50), "priority": ["Buck", "Multi-phase"]},
        "消費電子": {"vin": (3, 20), "vout": (1.2, 12), "iout": (1, 8), "priority": ["Buck", "Buck-Boost"]},
    }

    def __init__(self):
        self.components: List[ICComponent] = []

    def add_component(self, data: Dict):
        """添加元件"""
        ic = ICComponent(
            name=data.get("name", ""),
            part_number=data.get("part_number", ""),
            category=data.get("category", "unknown"),
            vin_range=tuple(data.get("vin_range", [0, 0])),
            vout_range=tuple(data.get("vout_range", [0, 0])),
            iout_max=data.get("iout_max", 0),
            efficiency=data.get("efficiency", 0),
            package=data.get("package", "Unknown"),
            features=data.get("features", [])
        )
        self.components.append(ic)
        return ic

    def load_sample_data(self):
        """載入樣本數據"""
        sample_ics = [
            {
                "name": "MP1484", "part_number": "MP1484DN",
                "category": "buck", "vin_range": [4.5, 16], "vout_range": [0.8, 15], "iout_max": 3,
                "efficiency": 92, "package": "SOP-8", "features": ["同步整流", "過溫保護", "短路保護"]
            },
            {
                "name": "LM2596", "part_number": "LM2596T-5.0",
                "category": "buck", "vin_range": [4.5, 40], "vout_range": [3.3, 12], "iout_max": 3,
                "efficiency": 75, "package": "TO-220", "features": ["簡單可靠", "成本低", "廣泛使用"]
            },
            {
                "name": "RT8289", "part_number": "RT8289GSP",
                "category": "buck", "vin_range": [4.5, 26], "vout_range": [0.8, 20], "iout_max": 5,
                "efficiency": 93, "package": "SOP-8", "features": ["高效率", "低EMI", "過流保護"]
            },
            {
                "name": "TPS62840", "part_number": "TPS62840DLCR",
                "category": "buck", "vin_range": [1.8, 6.5], "vout_range": [0.4, 5.5], "iout_max": 0.75,
                "efficiency": 95, "package": "SOT-563", "features": ["微型", "超低靜態電流", "I2C可調"]
            },
            {
                "name": "AMC7135", "part_number": "AMC7135AP",
                "category": "buck", "vin_range": [2.7, 6], "vout_range": [3.2, 3.2], "iout_max": 0.38,
                "efficiency": 88, "package": "SOT-89", "features": ["恒流輸出", "LED驅動"]
            },
            {
                "name": "MT3608", "part_number": "MT3608",
                "category": "boost", "vin_range": [2, 24], "vout_range": [5, 28], "iout_max": 2,
                "efficiency": 87, "package": "SOT-23-6", "features": ["升壓", "1.2MHz開關頻率"]
            },
            {
                "name": "SY6288", "part_number": "SY6288AAC",
                "category": "load_switch", "vin_range": [2.5, 5.5], "vout_range": [2.5, 5.5], "iout_max": 2,
                "efficiency": 95, "package": "SOT-23-6", "features": ["負載開關", "低導通電阻"]
            },
        ]
        for ic_data in sample_ics:
            self.add_component(ic_data)
        print(f"[OK] Loaded {len(self.components)} sample ICs")

    def filter_by_application(self, app: str) -> List[ICComponent]:
        """根據應用場景篩選"""
        if app not in self.APPLICATIONS:
            return self.components

        req = self.APPLICATIONS[app]
        results = []

        for ic in self.components:
            # 檢查輸入電壓範圍
            if ic.vin_range[0] > req["vin"][0] or ic.vin_range[1] < req["vin"][1]:
                continue

            # 檢查輸出電壓範圍
            if ic.vout_range[1] < req["vout"][0]:
                continue

            # 檢查輸出電流
            if ic.iout_max < req["iout"][0]:
                continue

            results.append(ic)

        return results

    def compare_components(self, part_numbers: List[str]) -> List[Dict]:
        """對比選定的元件"""
        selected = [ic for ic in self.components if ic.part_number in part_numbers or ic.name in part_numbers]

        if not selected:
            return []

        comparison = []
        for ic in selected:
            # 計算功率密度 (估算)
            power_density = (ic.iout_max * ic.vout_range[1]) / 0.5  # 簡化估算

            comparison.append({
                "name": ic.name,
                "part_number": ic.part_number,
                "category": ic.category,
                "vin_range": f"{ic.vin_range[0]:.1f}-{ic.vin_range[1]:.1f}V",
                "vout_range": f"{ic.vout_range[0]:.1f}-{ic.vout_range[1]:.1f}V",
                "iout_max": f"{ic.iout_max}A",
                "efficiency": f"{ic.efficiency}%",
                "package": ic.package,
                "power_density": f"{power_density:.1f}W/in³",
                "features": ic.features
            })

        return comparison

    def generate_selection_guide(self, v_in: float, v_out: float, i_out: float, app: str = "") -> Dict:
        """生成選型指南"""
        # 確定拓撲
        if v_out > v_in:
            topology = "boost"
        elif v_out < v_in * 0.8:
            topology = "buck"
        else:
            topology = "buck_boost"

        # 篩選
        candidates = []
        for ic in self.components:
            if ic.vin_range[0] <= v_in <= ic.vin_range[1]:
                if ic.vout_range[0] <= v_out <= ic.vout_range[1]:
                    if ic.iout_max >= i_out:
                        candidates.append(ic)

        # 評分
        for ic in candidates:
            score = 0
            score += ic.efficiency * 0.4
            score += (ic.iout_max / i_out) * 20 if ic.iout_max > i_out else (ic.iout_max / i_out) * 30
            score += 20 if ic.category == topology else 0
            ic.score = score

        candidates.sort(key=lambda x: x.score, reverse=True)

        return {
            "input": {"vin": v_in, "vout": v_out, "iout": i_out},
            "recommended_topology": topology,
            "application": app,
            "candidates": [
                {
                    "name": ic.name,
                    "part_number": ic.part_number,
                    "category": ic.category,
                    "efficiency": ic.efficiency,
                    "iout_max": ic.iout_max,
                    "score": round(ic.score, 1),
                    "features": ic.features
                }
                for ic in candidates[:5]
            ]
        }

    def print_comparison(self, comparison: List[Dict]):
        """打印對比表"""
        print("\n" + "=" * 80)
        print("       IT Power IC Comparison Table")
        print("=" * 80)

        for ic in comparison:
            print(f"\n【{ic['name']}】{ic['part_number']}")
            print(f"  Category: {ic['category']}")
            print(f"  Vin: {ic['vin_range']} | Vout: {ic['vout_range']} | Iout: {ic['iout_max']}")
            print(f"  Efficiency: {ic['efficiency']} | Package: {ic['package']}")
            print(f"  Power Density: {ic['power_density']}")
            if ic['features']:
                print(f"  Features: {', '.join(ic['features'])}")

        print("\n" + "=" * 80)

    def print_selection_guide(self, guide: Dict):
        """打印選型指南"""
        print("\n" + "=" * 70)
        print("       Power IC Selection Guide")
        print("=" * 70)
        print(f"Input: {guide['input']['vin']}V | Output: {guide['input']['vout']}V | Current: {guide['input']['iout']}A")
        print(f"Recommended Topology: {guide['recommended_topology'].upper()}")
        if guide['application']:
            print(f"Application: {guide['application']}")

        print("\n[Top Candidates]")
        for i, cand in enumerate(guide['candidates'], 1):
            print(f"\n  #{i} {cand['name']} ({cand['part_number']})")
            print(f"      Efficiency: {cand['efficiency']}% | Iout: {cand['iout_max']}A")
            print(f"      Score: {cand['score']}")
            print(f"      Features: {', '.join(cand['features'])}")

        print("\n" + "=" * 70)


def main():
    analyzer = PowerICAnalyzer()
    analyzer.load_sample_data()

    import sys

    if len(sys.argv) < 2:
        # 演示
        print("\n[Power IC Analysis Demo]")

        # 對比
        comparison = analyzer.compare_components(["MP1484DN", "LM2596T-5.0", "RT8289GSP"])
        if comparison:
            analyzer.print_comparison(comparison)

        # 選型
        guide = analyzer.generate_selection_guide(12, 3.3, 2, "消費電子")
        analyzer.print_selection_guide(guide)

    else:
        cmd = sys.argv[1]

        if cmd == "compare":
            if len(sys.argv) > 2:
                parts = sys.argv[2].split(',')
                comparison = analyzer.compare_components(parts)
                analyzer.print_comparison(comparison)
            else:
                print("Usage: python power_ic_analyzer.py compare <part1,part2,...>")

        elif cmd == "select":
            if len(sys.argv) >= 5:
                v_in = float(sys.argv[2])
                v_out = float(sys.argv[3])
                i_out = float(sys.argv[4])
                app = sys.argv[5] if len(sys.argv) > 5 else ""
                guide = analyzer.generate_selection_guide(v_in, v_out, i_out, app)
                analyzer.print_selection_guide(guide)
            else:
                print("Usage: python power_ic_analyzer.py select <vin> <vout> <iout> [app]")

        elif cmd == "list":
            print(f"\nTotal ICs: {len(analyzer.components)}")
            for ic in analyzer.components:
                print(f"  - {ic.name} ({ic.part_number}) [{ic.category}]")

        else:
            print("Commands: compare | select | list")


if __name__ == "__main__":
    main()
