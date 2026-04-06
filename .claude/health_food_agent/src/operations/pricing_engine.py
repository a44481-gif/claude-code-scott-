"""
定价引擎
"""
from typing import Dict, List, Optional
from loguru import logger


class PricingEngine:
    """智能定价引擎"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.cost_factors = self.config.get("cost_factors", {
            "product_cost": 1.0,
            "shipping_to_taiwan": 0.15,
            "tariff_rate": 0.10,
            "platform_fee": 0.10,
            "target_margin": 0.25,
        })
        self.price_tiers = self.config.get("price_tiers", {
            "premium": 1.3,
            "standard": 1.0,
            "budget": 0.8,
        })
        self.cny_to_twd_rate = 4.5  # 默认汇率

    def calculate_price(self, cost_cny: float, tier: str = "standard",
                       market_data: Optional[Dict] = None) -> Dict:
        """计算产品定价"""
        tier_multiplier = self.price_tiers.get(tier, 1.0)

        # 成本分解
        cost_details = {
            "product_cost_cny": cost_cny,
            "exchange_rate": self.cny_to_twd_rate,
            "product_cost_twd": cost_cny * self.cny_to_twd_rate,
            "shipping_to_taiwan_twd": cost_cny * self.cny_to_twd_rate * self.cost_factors["shipping_to_taiwan"],
            "tariff_twd": cost_cny * self.cny_to_twd_rate * self.cost_factors["tariff_rate"],
            "platform_fee_twd": 0,  # 待定
            "total_cost_twd": 0,
            "target_margin": self.cost_factors["target_margin"],
            "final_price_twd": 0,
            "profit_twd": 0,
        }

        # 计算总成本
        cost_details["platform_fee_twd"] = 0  # 先按0算，后续根据渠道调整
        cost_details["total_cost_twd"] = (
            cost_details["product_cost_twd"]
            + cost_details["shipping_to_taiwan_twd"]
            + cost_details["tariff_twd"]
            + cost_details["platform_fee_twd"]
        )

        # 应用市场数据（如果有）
        if market_data:
            market_avg = market_data.get("avg_price", cost_details["total_cost_twd"])
            recommended_price = cost_details["total_cost_twd"] * (1 + self.cost_factors["target_margin"]) * tier_multiplier

            # 确保价格有竞争力
            if recommended_price > market_avg * 1.5:
                recommended_price = market_avg * 1.2  # 溢价20%
            elif recommended_price < market_avg * 0.5:
                recommended_price = market_avg * 0.7  # 降价30%但保持利润
        else:
            recommended_price = cost_details["total_cost_twd"] * (1 + self.cost_factors["target_margin"]) * tier_multiplier

        cost_details["final_price_twd"] = round(recommended_price, 0)
        cost_details["profit_twd"] = round(recommended_price - cost_details["total_cost_twd"], 0)
        cost_details["profit_margin"] = round(cost_details["profit_twd"] / recommended_price * 100, 1) if recommended_price > 0 else 0

        return cost_details

    def calculate_channel_price(self, base_price: float, channel: str) -> Dict:
        """计算各渠道定价"""
        channel_fees = {
            "shopee": 0,  # 虾皮成交费约2%
            "rakuten": 0,  # 乐天约3%
            "pchome": 0,  # PChome约5%
            "facebook": 0,  # FB无平台费
            "offline": 0,  # 线下渠道约10-15%
        }

        fee_rate = channel_fees.get(channel, 0.05)
        price_with_fee = base_price * (1 + fee_rate)

        # 渠道差异化
        if channel in ["shopee", "pchome"]:
            # 电商平台：保持原价或小幅优惠
            return {
                "channel": channel,
                "list_price": round(base_price, 0),
                "selling_price": round(base_price * 0.98, 0),  # 98折
                "fee_rate": fee_rate,
            }
        elif channel == "rakuten":
            # 乐天：可溢价
            return {
                "channel": channel,
                "list_price": round(base_price * 1.05, 0),
                "selling_price": round(base_price * 1.03, 0),
                "fee_rate": fee_rate,
            }
        elif channel == "facebook":
            # FB：无平台费，可降价
            return {
                "channel": channel,
                "list_price": round(base_price * 0.95, 0),
                "selling_price": round(base_price * 0.92, 0),
                "fee_rate": 0,
            }
        else:
            return {
                "channel": channel,
                "list_price": round(base_price * 1.1, 0),
                "selling_price": round(base_price * 1.05, 0),
                "fee_rate": 0.10,
            }

    def calculate_bulk_discount(self, quantity: int, unit_price: float) -> Dict:
        """计算批发折扣"""
        if quantity >= 100:
            discount = 0.70  # 7折
        elif quantity >= 50:
            discount = 0.80  # 8折
        elif quantity >= 20:
            discount = 0.85  # 85折
        elif quantity >= 10:
            discount = 0.90  # 9折
        else:
            discount = 1.0

        return {
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_rate": discount,
            "discounted_price": round(unit_price * discount, 0),
            "savings": round(unit_price * (1 - discount), 0),
        }

    def generate_pricing_report(self, products: List[Dict], market_data: Dict) -> Dict:
        """生成定价报告"""
        report = {
            "generated_at": "",
            "currency_rate": self.cny_to_twd_rate,
            "products": [],
            "summary": {
                "total_products": len(products),
                "avg_profit_margin": 0,
                "min_price": float("inf"),
                "max_price": 0,
            }
        }

        total_margin = 0
        for product in products:
            cost = product.get("price", 0)
            pricing = self.calculate_price(cost, tier="standard", market_data=market_data.get(product.get("category", "")))
            product["pricing"] = pricing
            report["products"].append({
                "name": product.get("name", ""),
                "category": product.get("category", ""),
                "cost_cny": cost,
                **pricing
            })

            total_margin += pricing["profit_margin"]
            report["summary"]["min_price"] = min(report["summary"]["min_price"], pricing["final_price_twd"])
            report["summary"]["max_price"] = max(report["summary"]["max_price"], pricing["final_price_twd"])

        report["summary"]["avg_profit_margin"] = round(total_margin / len(products), 1) if products else 0
        return report
