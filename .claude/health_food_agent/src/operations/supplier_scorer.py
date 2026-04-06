"""
供应商评估模块
"""
from typing import List, Dict, Optional
from loguru import logger


class SupplierScorer:
    """供应商综合评分系统"""

    def __init__(self):
        self.weights = {
            "rating": 0.20,        # 店铺评分
            "response_rate": 0.15,  # 回复率
            "total_orders": 0.15,   # 订单数
            "price": 0.15,          # 价格竞争力
            "certification": 0.15,   # 资质认证
            "location": 0.10,       # 地理位置
            "delivery_speed": 0.10, # 发货速度
        }

    def score_supplier(self, supplier: Dict, product: Optional[Dict] = None) -> Dict:
        """评估供应商综合得分"""
        scores = {}

        # 1. 店铺评分 (0-100)
        rating = supplier.get("rating", 0)
        scores["rating"] = min(rating / 5 * 100, 100)

        # 2. 回复率 (0-100)
        response_rate = supplier.get("response_rate", 0)
        scores["response_rate"] = response_rate if response_rate <= 100 else 100

        # 3. 订单量 (0-100)
        orders = supplier.get("total_orders", 0)
        if orders >= 100000:
            scores["total_orders"] = 100
        elif orders >= 10000:
            scores["total_orders"] = 85
        elif orders >= 1000:
            scores["total_orders"] = 70
        elif orders >= 100:
            scores["total_orders"] = 50
        else:
            scores["total_orders"] = 30

        # 4. 价格竞争力 (0-100)
        if product:
            supplier_price = supplier.get("quoted_price", product.get("price", 0))
            market_price = product.get("price", supplier_price)
            if market_price > 0:
                scores["price"] = max(0, min((1 - (supplier_price - market_price) / market_price) * 100, 120))
            else:
                scores["price"] = 70
        else:
            scores["price"] = 70

        # 5. 资质认证 (0-100)
        cert = supplier.get("certification", "")
        cert_score = 50
        if any(x in cert for x in ["ISO", "HACCP", "GMP", "有机", "绿色食品"]):
            cert_score += 40
        if any(x in cert for x in ["FDA", "CE", "有机认证"]):
            cert_score += 10
        scores["certification"] = min(cert_score, 100)

        # 6. 地理位置 (0-100) - 距离近有利
        location = supplier.get("location", "")
        if any(x in location for x in ["广东", "福建", "浙江", "江苏", "上海"]):
            scores["location"] = 90  # 离台湾近
        elif any(x in location for x in ["山东", "河南", "湖北", "湖南"]):
            scores["location"] = 75
        elif any(x in location for x in ["北京", "天津", "河北", "东北"]):
            scores["location"] = 60
        else:
            scores["location"] = 50

        # 7. 发货速度 (0-100)
        delivery_days = supplier.get("last_delivery_days", 7)
        if delivery_days <= 2:
            scores["delivery_speed"] = 100
        elif delivery_days <= 5:
            scores["delivery_speed"] = 85
        elif delivery_days <= 7:
            scores["delivery_speed"] = 70
        else:
            scores["delivery_speed"] = 50

        # 综合评分
        total_score = sum(scores[k] * self.weights[k] for k in self.weights)

        # 优劣势分析
        strengths = []
        weaknesses = []
        if scores["rating"] >= 80:
            strengths.append("店铺评分高，口碑好")
        elif scores["rating"] < 50:
            weaknesses.append("店铺评分偏低")

        if scores["response_rate"] >= 90:
            strengths.append("回复及时，服务态度好")
        elif scores["response_rate"] < 70:
            weaknesses.append("回复率有待提升")

        if scores["total_orders"] >= 80:
            strengths.append("订单量大，经验丰富")
        elif scores["total_orders"] < 50:
            weaknesses.append("订单经验较少")

        if scores["certification"] >= 80:
            strengths.append("资质认证齐全，产品质量有保障")
        elif scores["certification"] < 50:
            weaknesses.append("缺乏相关资质认证")

        if scores["location"] >= 85:
            strengths.append("地理位置优越，物流时效快")
        elif scores["location"] < 60:
            weaknesses.append("地理位置偏远，物流成本高")

        if scores["delivery_speed"] >= 80:
            strengths.append("发货速度快")
        elif scores["delivery_speed"] < 60:
            weaknesses.append("发货速度偏慢")

        status = "已认证" if total_score >= 70 else "待审核" if total_score >= 50 else "不合格"

        return {
            "supplier_name": supplier.get("name", ""),
            "platform": supplier.get("platform", ""),
            "total_score": round(total_score, 1),
            "scores": {k: round(v, 1) for k, v in scores.items()},
            "status": status,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": self._get_recommendation(total_score, scores),
        }

    def _get_recommendation(self, total_score: float, scores: Dict) -> str:
        """获取推荐建议"""
        if total_score >= 80:
            return "强烈推荐 - 优质供应商，可优先合作"
        elif total_score >= 70:
            return "推荐 - 合格供应商，可考虑合作"
        elif total_score >= 60:
            return "观望 - 建议进一步核实后再决定"
        elif total_score >= 50:
            return "谨慎 - 存在一定风险，需谨慎评估"
        else:
            return "不推荐 - 建议寻找其他供应商"

    def rank_suppliers(self, suppliers: List[Dict]) -> List[Dict]:
        """供应商排名"""
        ranked = []
        for supplier in suppliers:
            result = self.score_supplier(supplier)
            supplier["evaluation"] = result
            supplier["overall_score"] = result["total_score"]
            ranked.append(supplier)

        ranked.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        return ranked

    def find_best_supplier(self, suppliers: List[Dict], product: Dict = None) -> Optional[Dict]:
        """找出最佳供应商"""
        if not suppliers:
            return None

        ranked = self.rank_suppliers(suppliers)
        best = ranked[0]

        if best.get("overall_score", 0) >= 50:
            return best
        return None  # 没有合格的供应商
