# -*- coding: utf-8 -*-
"""
決策分析工具 - 幫助商業決策的量化分析
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class DecisionType(Enum):
    BUY_SELL = "buy_sell"  # 買賣決策
    GO_NO_GO = "go_no_go"  # 執行/放棄
    RANKING = "ranking"    # 排序選擇
    RESOURCE = "resource"  # 資源分配


@dataclass
class Decision:
    """決策選項"""
    name: str
    score: float = 0.0
    factors: Dict[str, float] = None
    notes: str = ""


class DecisionAnalyzer:
    """決策分析工具"""

    # 評估維度
    DIMENSIONS = {
        "市場潛力": {"weight": 0.25, "description": "市場規模和增長潛力"},
        "技術可行性": {"weight": 0.20, "description": "技術實現難度"},
        "財務回報": {"weight": 0.25, "description": "投資回報率和現金流"},
        "競爭優勢": {"weight": 0.15, "description": "與競爭對手的差異化"},
        "風險程度": {"weight": 0.15, "description": "執行風險和不确定性"},  # 風險越高分數越低
    }

    def __init__(self):
        self.decision_type = None
        self.options: List[Decision] = []

    def set_decision_type(self, decision_type: str):
        """設置決策類型"""
        if decision_type == "investment":
            self.decision_type = DecisionType.BUY_SELL
        elif decision_type == "project":
            self.decision_type = DecisionType.GO_NO_GO
        else:
            self.decision_type = DecisionType.RANKING

    def add_option(self, name: str, factors: Dict[str, float] = None, notes: str = "") -> Decision:
        """添加決策選項"""
        option = Decision(name=name, factors=factors or {}, notes=notes)
        self.options.append(option)
        return option

    def score_option(self, option: Decision) -> float:
        """計算選項得分"""
        if not option.factors:
            return 0.0

        total_score = 0.0
        for dim, data in self.DIMENSIONS.items():
            if dim in option.factors:
                # 因子值 * 權重
                factor_score = option.factors[dim] * data["weight"]
                total_score += factor_score

        # 標準化到 0-100
        option.score = total_score * 100
        return option.score

    def analyze(self) -> Dict:
        """執行分析"""
        if not self.options:
            return {"error": "No options to analyze"}

        # 計算所有選項得分
        for option in self.options:
            self.score_option(option)

        # 排序
        ranked = sorted(self.options, key=lambda x: x.score, reverse=True)

        # 生成報告
        report = {
            "timestamp": self.get_timestamp(),
            "decision_type": self.decision_type.value if self.decision_type else "unknown",
            "options_count": len(self.options),
            "ranking": [
                {
                    "rank": i + 1,
                    "name": opt.name,
                    "score": round(opt.score, 2),
                    "factors": opt.factors,
                    "notes": opt.notes
                }
                for i, opt in enumerate(ranked)
            ],
            "recommendation": ranked[0].name if ranked else None,
            "dimensions": {k: v["weight"] for k, v in self.DIMENSIONS.items()}
        }

        return report

    def swot_analysis(self, strengths: List[str], weaknesses: List[str],
                     opportunities: List[str], threats: List[str]) -> Dict:
        """SWOT 分析"""
        return {
            "Strengths": strengths,
            "Weaknesses": weaknesses,
            "Opportunities": opportunities,
            "Threats": threats,
            "Strategies": {
                "SO (Strengths-Opportunities)": "利用優勢抓住機會",
                "WO (Weaknesses-Opportunities)": "克服弱點抓住機會",
                "ST (Strengths-Threats)": "利用優勢規避威脅",
                "WT (Weaknesses-Threats)": "減少弱點規避威脅"
            }
        }

    def risk_assessment(self, risks: List[Dict]) -> Dict:
        """風險評估"""
        # 計算風險分數
        for risk in risks:
            impact = risk.get("impact", 5)  # 1-10
            probability = risk.get("probability", 5)  # 1-10
            risk["risk_score"] = impact * probability

        # 分類
        high_risk = [r for r in risks if r["risk_score"] >= 40]
        medium_risk = [r for r in risks if 15 <= r["risk_score"] < 40]
        low_risk = [r for r in risks if r["risk_score"] < 15]

        return {
            "total_risks": len(risks),
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "overall_assessment": "高風險" if high_risk else "中等風險" if medium_risk else "低風險"
        }

    def print_report(self, report: Dict):
        """打印報告"""
        print("\n" + "=" * 60)
        print("       Decision Analysis Report")
        print("=" * 60)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Options Analyzed: {report['options_count']}")
        print(f"Recommendation: {report['recommendation']}")

        print("\n[Dimension Weights]")
        for dim, weight in report["dimensions"].items():
            print(f"  - {dim}: {weight*100:.0f}%")

        print("\n[Ranking]")
        for opt in report["ranking"]:
            mark = ">>>" if opt["rank"] == 1 else "   "
            print(f"{mark} #{opt['rank']} {opt['name']}: {opt['score']:.1f}分")
            if opt['notes']:
                print(f"      Note: {opt['notes']}")

        print("=" * 60)

    @staticmethod
    def get_timestamp() -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def quick_decision(options: List[Tuple[str, Dict]]) -> Dict:
    """快速決策分析"""
    analyzer = DecisionAnalyzer()

    for name, factors in options:
        analyzer.add_option(name, factors)

    report = analyzer.analyze()
    analyzer.print_report(report)

    return report


if __name__ == "__main__":
    # 演示
    options = [
        ("方案A: 自主研發", {
            "市場潛力": 0.8,
            "技術可行性": 0.6,
            "財務回報": 0.7,
            "競爭優勢": 0.8,
            "風險程度": 0.6
        }),
        ("方案B: 戰略合作", {
            "市場潛力": 0.7,
            "技術可行性": 0.9,
            "財務回報": 0.6,
            "競爭優勢": 0.5,
            "風險程度": 0.4
        }),
        ("方案C: 並購", {
            "市場潛力": 0.9,
            "技術可行性": 0.9,
            "財務回報": 0.4,
            "競爭優勢": 0.9,
            "風險程度": 0.7
        })
    ]

    print("\n[Decision Analysis Demo]")
    quick_decision(options)
