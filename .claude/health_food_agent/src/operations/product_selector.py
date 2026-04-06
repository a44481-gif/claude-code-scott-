"""
选品决策模块
"""
import json
from typing import List, Dict, Optional
from loguru import logger


class ProductSelector:
    """智能选品决策器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def evaluate_product(self, product: Dict, supplier: Dict, market_data: Dict) -> Dict:
        """评估单个产品是否值得引入"""
        scores = {}
        reasons = []

        # 1. 市场需求评分
        scores["market_demand"] = self._score_market_demand(product, market_data)
        if scores["market_demand"] >= 70:
            reasons.append("市场需求旺盛")

        # 2. 价格竞争力评分
        scores["price_competitiveness"] = self._score_price(product, market_data)
        if scores["price_competitiveness"] >= 70:
            reasons.append("价格有竞争力")

        # 3. 利润空间评分
        scores["profit_margin"] = self._score_profit_margin(product, market_data)
        if scores["profit_margin"] >= 60:
            reasons.append("利润空间可观")

        # 4. 供应商可靠性评分
        scores["supplier_reliability"] = self._score_supplier(supplier)
        if scores["supplier_reliability"] >= 70:
            reasons.append("供应商可靠")

        # 5. 合规可行性评分
        scores["compliance"] = self._score_compliance(product)
        if scores["compliance"] >= 60:
            reasons.append("合规风险可控")

        # 6. 物流可行性评分
        scores["logistics"] = self._score_logistics(product)
        if scores["logistics"] >= 50:
            reasons.append("物流运输可行")

        # 综合评分
        weights = {
            "market_demand": 0.25,
            "price_competitiveness": 0.20,
            "profit_margin": 0.20,
            "supplier_reliability": 0.15,
            "compliance": 0.10,
            "logistics": 0.10,
        }
        total_score = sum(scores[k] * weights[k] for k in weights)

        recommendation = "强烈推荐" if total_score >= 75 else \
                        "推荐" if total_score >= 60 else \
                        "观望" if total_score >= 45 else "不推荐"

        return {
            "product_name": product.get("name", ""),
            "total_score": round(total_score, 1),
            "scores": {k: round(v, 1) for k, v in scores.items()},
            "recommendation": recommendation,
            "reasons": reasons,
            "concerns": self._get_concerns(scores),
        }

    def _score_market_demand(self, product: Dict, market_data: Dict) -> float:
        """市场需求评分"""
        sales_count = product.get("sales_count", 0)
        # 1688上销量越高说明市场需求越大
        if sales_count >= 10000:
            return 90
        elif sales_count >= 5000:
            return 80
        elif sales_count >= 1000:
            return 70
        elif sales_count >= 100:
            return 50
        else:
            return 30

    def _score_price(self, product: Dict, market_data: Dict) -> float:
        """价格竞争力评分"""
        source_price = product.get("price", 0)
        if not source_price:
            return 50

        # 计算台湾终端售价
        estimated_twd = source_price * 4.5 * 1.15 * 1.10 * 1.25  # 成本*汇率*运费*关税*利润

        # 与市场价对比
        market_avg = market_data.get("avg_price", 500)
        if estimated_twd <= market_avg * 0.7:
            return 95  # 非常有竞争力
        elif estimated_twd <= market_avg:
            return 80
        elif estimated_twd <= market_avg * 1.3:
            return 60
        else:
            return 40

    def _score_profit_margin(self, product: Dict, market_data: Dict) -> float:
        """利润空间评分"""
        source_price = product.get("price", 0)
        market_avg = market_data.get("avg_price", 500)
        margin = (market_avg - source_price * 4.5) / market_avg if market_avg > 0 else 0

        if margin >= 0.4:
            return 90
        elif margin >= 0.3:
            return 75
        elif margin >= 0.2:
            return 60
        elif margin >= 0.1:
            return 40
        else:
            return 20

    def _score_supplier(self, supplier: Dict) -> float:
        """供应商可靠性评分"""
        score = 50
        rating = supplier.get("rating", 0)
        if rating >= 4.8:
            score += 30
        elif rating >= 4.5:
            score += 20
        elif rating >= 4.0:
            score += 10

        total_orders = supplier.get("total_orders", 0)
        if total_orders >= 10000:
            score += 20
        elif total_orders >= 1000:
            score += 10

        return min(score, 100)

    def _score_compliance(self, product: Dict) -> float:
        """合规可行性评分"""
        score = 60
        # 检查基本信息完整性
        if product.get("name"):
            score += 10
        if product.get("weight"):
            score += 10
        if product.get("shelf_life"):
            score += 10
        # 风险项扣分
        if "进口" in product.get("name", "") or "代购" in product.get("name", ""):
            score -= 20
        return max(0, min(score, 100))

    def _score_logistics(self, product: Dict) -> float:
        """物流可行性评分"""
        score = 50
        weight = product.get("weight", "")
        # 解析重量
        import re
        weight_match = re.search(r"(\d+\.?\d*)\s*(kg|克|g)", weight.lower() if weight else "")
        if weight_match:
            weight_val = float(weight_match.group(1))
            if weight_match.group(2) in ["克", "g"]:
                weight_val /= 1000
            if weight_val <= 5:
                score += 30
            elif weight_val <= 10:
                score += 20
            elif weight_val <= 20:
                score += 10
            else:
                score -= 10
        return max(0, min(score, 100))

    def _get_concerns(self, scores: Dict) -> List[str]:
        """获取需要关注的问题"""
        concerns = []
        if scores["compliance"] < 60:
            concerns.append("合规风险需重点关注")
        if scores["logistics"] < 50:
            concerns.append("物流成本可能较高")
        if scores["supplier_reliability"] < 60:
            concerns.append("建议进一步核实供应商资质")
        if scores["price_competitiveness"] < 60:
            concerns.append("价格优势不明显，需谈更优批发价")
        return concerns

    def select_top_products(self, products: List[Dict], suppliers: List[Dict],
                           market_data: Dict, top_n: int = 20) -> List[Dict]:
        """筛选TOP产品"""
        results = []
        supplier_map = {s.get("name", ""): s for s in suppliers}

        for product in products:
            supplier_name = product.get("seller", "")
            supplier = supplier_map.get(supplier_name, {})
            evaluation = self.evaluate_product(product, supplier, market_data)
            product["evaluation"] = evaluation
            product["ai_recommendation_score"] = evaluation["total_score"]
            results.append(product)

        # 按评分排序
        results.sort(key=lambda x: x.get("ai_recommendation_score", 0), reverse=True)
        return results[:top_n]
