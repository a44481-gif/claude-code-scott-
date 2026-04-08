# -*- coding: utf-8 -*-
"""
大數據分析工具 - 市場數據分析、趨勢預測、數據視覺化
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DataPoint:
    """數據點"""
    date: str
    value: float
    category: str = ""


class BigDataAnalyzer:
    """大數據分析工具"""

    def __init__(self):
        self.datasets: Dict[str, List[DataPoint]] = {}
        self.analysis_results: Dict = {}

    def load_dataset(self, name: str, data: List[Dict]):
        """載入數據集"""
        points = [DataPoint(**d) for d in data]
        self.datasets[name] = points
        return len(points)

    def add_data_point(self, dataset: str, date: str, value: float, category: str = ""):
        """添加數據點"""
        if dataset not in self.datasets:
            self.datasets[dataset] = []
        self.datasets[dataset].append(DataPoint(date, value, category))

    def calculate_stats(self, dataset: str) -> Dict:
        """計算統計數據"""
        if dataset not in self.datasets or not self.datasets[dataset]:
            return {"error": "Dataset not found or empty"}

        values = [p.value for p in self.datasets[dataset]]
        n = len(values)

        # 基本統計
        total = sum(values)
        mean = total / n
        sorted_vals = sorted(values)
        median = sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
        min_val = min(values)
        max_val = max(values)

        # 標準差
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = math.sqrt(variance)

        # 增長率
        growth_rate = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0

        return {
            "dataset": dataset,
            "count": n,
            "total": round(total, 2),
            "mean": round(mean, 2),
            "median": round(median, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "std_dev": round(std_dev, 2),
            "growth_rate": round(growth_rate, 2),
            "range": round(max_val - min_val, 2)
        }

    def calculate_cagr(self, dataset: str, years: int = None) -> float:
        """計算年均複合增長率 (CAGR)"""
        if dataset not in self.datasets or len(self.datasets[dataset]) < 2:
            return 0

        data = self.datasets[dataset]
        start_value = data[0].value
        end_value = data[-1].value

        if start_value <= 0 or end_value <= 0:
            return 0

        if years is None:
            # 嘗試從日期計算
            try:
                start_date = datetime.strptime(data[0].date, "%Y-%m-%d")
                end_date = datetime.strptime(data[-1].date, "%Y-%m-%d")
                years = (end_date - start_date).days / 365
            except:
                years = len(data) - 1

        if years <= 0:
            years = 1

        cagr = (pow(end_value / start_value, 1 / years) - 1) * 100
        return round(cagr, 2)

    def trend_analysis(self, dataset: str, window: int = 3) -> Dict:
        """趨勢分析 (移動平均)"""
        if dataset not in self.datasets or len(self.datasets[dataset]) < window:
            return {"error": "Insufficient data"}

        values = [p.value for p in self.datasets[dataset]]

        # 簡單移動平均
        ma = []
        for i in range(len(values)):
            if i < window - 1:
                ma.append(None)
            else:
                avg = sum(values[i - window + 1:i + 1]) / window
                ma.append(round(avg, 2))

        # 趨勢判斷
        trend = "Stable"
        if values[-1] > values[0] * 1.1:
            trend = "Upward"
        elif values[-1] < values[0] * 0.9:
            trend = "Downward"

        return {
            "dataset": dataset,
            "trend": trend,
            "moving_average": ma,
            "latest_value": values[-1],
            "first_value": values[0],
            "change_pct": round((values[-1] - values[0]) / values[0] * 100, 2)
        }

    def correlation_analysis(self, dataset1: str, dataset2: str) -> float:
        """相關性分析"""
        if dataset1 not in self.datasets or dataset2 not in self.datasets:
            return 0

        d1 = self.datasets[dataset1]
        d2 = self.datasets[dataset2]

        n = min(len(d1), len(d2))
        if n < 2:
            return 0

        vals1 = [d1[i].value for i in range(n)]
        vals2 = [d2[i].value for i in range(n)]

        mean1 = sum(vals1) / n
        mean2 = sum(vals2) / n

        # Pearson相關系數
        numerator = sum((vals1[i] - mean1) * (vals2[i] - mean2) for i in range(n))
        denom1 = math.sqrt(sum((v - mean1) ** 2 for v in vals1))
        denom2 = math.sqrt(sum((v - mean2) ** 2 for v in vals2))

        if denom1 == 0 or denom2 == 0:
            return 0

        correlation = numerator / (denom1 * denom2)
        return round(correlation, 3)

    def outlier_detection(self, dataset: str, threshold: float = 2.0) -> List[Dict]:
        """異常值檢測 (Z-score)"""
        if dataset not in self.datasets or len(self.datasets[dataset]) < 3:
            return []

        values = [(i, p.value) for i, p in enumerate(self.datasets[dataset])]
        mean = sum(v for _, v in values) / len(values)
        std = math.sqrt(sum((v - mean) ** 2 for _, v in values) / len(values))

        if std == 0:
            return []

        outliers = []
        for i, v in values:
            z_score = abs((v - mean) / std)
            if z_score > threshold:
                outliers.append({
                    "index": i,
                    "date": self.datasets[dataset][i].date,
                    "value": v,
                    "z_score": round(z_score, 2),
                    "deviation": "High" if v > mean else "Low"
                })

        return outliers

    def forecast_simple(self, dataset: str, periods: int = 3) -> List[float]:
        """簡單預測 (線性回歸)"""
        if dataset not in self.datasets or len(self.datasets[dataset]) < 3:
            return []

        values = [(i, p.value) for i, p in enumerate(self.datasets[dataset])]
        n = len(values)

        # 線性回歸
        sum_x = sum(i for i, _ in values)
        sum_y = sum(v for _, v in values)
        sum_xy = sum(i * v for i, v in values)
        sum_xx = sum(i * i for i, _ in values)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        # 預測
        forecasts = []
        for i in range(n, n + periods):
            forecast = slope * i + intercept
            forecasts.append(round(forecast, 2))

        return forecasts

    def segment_analysis(self, dataset: str) -> Dict:
        """分群分析"""
        if dataset not in self.datasets:
            return {}

        data = self.datasets[dataset]
        values = [p.value for p in data]

        # 按值分群
        segments = {
            "High": [],      # > 75%
            "Medium": [],    # 50-75%
            "Low": []        # < 50%
        }

        if not values:
            return segments

        sorted_vals = sorted(values)
        p50 = sorted_vals[len(sorted_vals) // 2]
        p75 = sorted_vals[len(sorted_vals) * 3 // 4]

        for p in data:
            if p.value >= p75:
                segments["High"].append({"date": p.date, "value": p.value})
            elif p.value >= p50:
                segments["Medium"].append({"date": p.date, "value": p.value})
            else:
                segments["Low"].append({"date": p.date, "value": p.value})

        return {
            "dataset": dataset,
            "segments": segments,
            "high_count": len(segments["High"]),
            "medium_count": len(segments["Medium"]),
            "low_count": len(segments["Low"])
        }

    def generate_report(self, dataset: str) -> str:
        """生成分析報告"""
        stats = self.calculate_stats(dataset)
        cagr = self.calculate_cagr(dataset)
        trend = self.trend_analysis(dataset)
        forecast = self.forecast_simple(dataset, 3)
        outliers = self.outlier_detection(dataset)

        report = []
        report.append("=" * 60)
        report.append("       Big Data Analysis Report")
        report.append("=" * 60)
        report.append(f"Dataset: {dataset}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        report.append("\n[Statistics]")
        for k, v in stats.items():
            if k != "dataset":
                report.append(f"  {k}: {v}")

        report.append(f"\n[CAGR] {cagr}%")

        report.append(f"\n[Trend] {trend.get('trend', 'Unknown')}")
        report.append(f"  Change: {trend.get('change_pct', 0)}%")

        if forecast:
            report.append(f"\n[Forecast (Next 3 periods)]")
            for i, f in enumerate(forecast, 1):
                report.append(f"  Period {i}: {f}")

        if outliers:
            report.append(f"\n[Outliers Detected: {len(outliers)}]")
            for o in outliers[:5]:
                report.append(f"  - {o['date']}: {o['value']} ({o['deviation']}, z={o['z_score']})")

        report.append("=" * 60)
        return "\n".join(report)

    def print_report(self, dataset: str):
        """打印報告"""
        print(self.generate_report(dataset))


def main():
    analyzer = BigDataAnalyzer()

    # 載入樣本數據
    sample_data = [
        {"date": "2024-01", "value": 100, "category": "A"},
        {"date": "2024-02", "value": 115, "category": "A"},
        {"date": "2024-03", "value": 130, "category": "A"},
        {"date": "2024-04", "value": 125, "category": "A"},
        {"date": "2024-05", "value": 150, "category": "A"},
        {"date": "2024-06", "value": 170, "category": "A"},
        {"date": "2024-07", "value": 165, "category": "A"},
        {"date": "2024-08", "value": 190, "category": "A"},
        {"date": "2024-09", "value": 210, "category": "A"},
        {"date": "2024-10", "value": 230, "category": "A"},
        {"date": "2024-11", "value": 220, "category": "A"},
        {"date": "2024-12", "value": 250, "category": "A"},
    ]
    analyzer.load_dataset("Revenue_2024", sample_data)

    import sys

    if len(sys.argv) < 2:
        print("\n[Big Data Analysis Demo]")
        analyzer.print_report("Revenue_2024")

        # 相關性測試
        analyzer.add_data_point("Test2", "2024-01", 50)
        analyzer.add_data_point("Test2", "2024-06", 80)
        analyzer.add_data_point("Test2", "2024-12", 120)
        corr = analyzer.correlation_analysis("Revenue_2024", "Test2")
        print(f"\n[Correlation with Test2: {corr}]")

    else:
        cmd = sys.argv[1]

        if cmd == "stats":
            if len(sys.argv) > 2:
                print(json.dumps(analyzer.calculate_stats(sys.argv[2]), indent=2))
            else:
                print("Usage: python big_data_analyzer.py stats <dataset>")

        elif cmd == "cagr":
            if len(sys.argv) > 2:
                years = int(sys.argv[3]) if len(sys.argv) > 3 else None
                print(f"CAGR: {analyzer.calculate_cagr(sys.argv[2], years)}%")
            else:
                print("Usage: python big_data_analyzer.py cagr <dataset> [years]")

        elif cmd == "trend":
            if len(sys.argv) > 2:
                print(json.dumps(analyzer.trend_analysis(sys.argv[2]), indent=2))
            else:
                print("Usage: python big_data_analyzer.py trend <dataset>")

        elif cmd == "forecast":
            if len(sys.argv) > 2:
                periods = int(sys.argv[3]) if len(sys.argv) > 3 else 3
                forecasts = analyzer.forecast_simple(sys.argv[2], periods)
                print(f"Forecasts: {forecasts}")
            else:
                print("Usage: python big_data_analyzer.py forecast <dataset> [periods]")

        elif cmd == "outliers":
            if len(sys.argv) > 2:
                threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
                outliers = analyzer.outlier_detection(sys.argv[2], threshold)
                print(json.dumps(outliers, indent=2))
            else:
                print("Usage: python big_data_analyzer.py outliers <dataset> [threshold]")

        elif cmd == "report":
            if len(sys.argv) > 2:
                analyzer.print_report(sys.argv[2])
            else:
                print("Usage: python big_data_analyzer.py report <dataset>")

        else:
            print("Commands: stats | cagr | trend | forecast | outliers | report")


if __name__ == "__main__":
    main()
