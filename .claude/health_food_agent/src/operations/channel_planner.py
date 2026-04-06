"""
渠道规划模块
"""
from typing import Dict, List, Optional
from loguru import logger


class ChannelPlanner:
    """销售渠道规划器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.online_channels = self.config.get("online", [
            {"id": "shopee", "name": "虾皮购物", "commission": 0.02, "monthly_fee": 0},
            {"id": "rakuten", "name": "乐天市场", "commission": 0.03, "monthly_fee": 595},
            {"id": "pchome", "name": "PChome", "commission": 0.05, "monthly_fee": 0},
            {"id": "momo", "name": "momo", "commission": 0.05, "monthly_fee": 0},
            {"id": "yahoo", "name": "Yahoo", "commission": 0.03, "monthly_fee": 0},
        ])
        self.offline_channels = self.config.get("offline", [
            {"id": "health_store", "name": "健康食品专卖店", "channel_type": "offline"},
            {"id": "supermarket", "name": "超市/大卖场", "channel_type": "offline"},
            {"id": "convenience", "name": "便利店", "channel_type": "offline"},
            {"id": "department", "name": "百货公司", "channel_type": "offline"},
        ])

    def plan_launch_sequence(self, product: Dict, budget: str = "medium") -> Dict:
        """规划产品上市渠道顺序"""
        online_priority = [
            {"phase": 1, "channel": "虾皮", "reason": "门槛低、流量大、快速测试市场", "timeline": "第1-2周"},
            {"phase": 2, "channel": "Facebook/Instagram", "reason": "社交营销、建立品牌认知", "timeline": "第3-4周"},
            {"phase": 3, "channel": "乐天/PChome", "reason": "扩充流量入口、提升品牌可信度", "timeline": "第2-3月"},
            {"phase": 4, "channel": "momo/Yahoo", "reason": "全渠道覆盖", "timeline": "第3-6月"},
        ]

        offline_priority = [
            {"phase": 1, "channel": "健康食品店", "reason": "目标客群精准", "timeline": "第3-6月"},
            {"phase": 2, "channel": "超市", "reason": "扩大市场覆盖", "timeline": "第6-12月"},
        ]

        budget_adjustments = {
            "low": {"online_only": True, "influencer_budget": 5000, "ads_budget": 3000},
            "medium": {"online_only": False, "influencer_budget": 15000, "ads_budget": 10000},
            "high": {"online_only": False, "influencer_budget": 50000, "ads_budget": 30000},
        }

        budget_cfg = budget_adjustments.get(budget, budget_adjustments["medium"])

        return {
            "product_name": product.get("name", ""),
            "budget_level": budget,
            "online_phases": online_priority,
            "offline_phases": offline_priority if not budget_cfg["online_only"] else [],
            "budget_allocation": budget_cfg,
            "estimated_roi": self._estimate_roi(budget_cfg),
        }

    def _estimate_roi(self, budget_cfg: Dict) -> Dict:
        """估算投资回报"""
        total_investment = budget_cfg["influencer_budget"] + budget_cfg["ads_budget"]
        expected_sales = total_investment * 3  # 3倍回报预估
        return {
            "total_investment_twd": total_investment,
            "expected_revenue_twd": expected_sales,
            "expected_roi_percent": 200,
            "break_even_sales_twd": total_investment,
        }

    def create_channel_strategy(self, product: Dict, channels: List[str]) -> Dict:
        """为产品制定渠道策略"""
        strategies = {}

        channel_strategies = {
            "shopee": {
                "pricing": "中等价位，标品定价",
                "promotion": "参与平台活动、设置折扣券、Shopee Live直播",
                "operations": "早晚回复、保持高评分、处理差评",
                "tips": "争取'优选卖家'标志，提升曝光",
            },
            "rakuten": {
                "pricing": "可略高，主打品质",
                "promotion": "积分回赠、节日促销、Rakuten TV推广",
                "operations": "注重包装和服务细节，争取乐天精选",
                "tips": "乐天用户消费力较强，可推高端礼盒",
            },
            "facebook": {
                "pricing": "灵活定价，可提供组购优惠",
                "promotion": "内容营销、社群经营、直播销售",
                "operations": "定期发帖、互动回复、建立粉丝社群",
                "tips": "可与社团合作，如健康生活社团、妈咪社团",
            },
            "instagram": {
                "pricing": "视觉溢价，可以略高",
                "promotion": "美图营销、Story/Reels短视频、UGC内容",
                "operations": "保持视觉风格统一、hashtag策略",
                "tips": "与健身/美食/健康类KOL合作",
            },
            "offline": {
                "pricing": "统一定价，线上线下同价",
                "promotion": "店内陈列、试用体验、店员培训",
                "operations": "建立经销商体系、设置最低拿货量",
                "tips": "健康食品店可先铺货后结款模式",
            },
        }

        for channel in channels:
            strategies[channel] = channel_strategies.get(channel, {})

        return strategies

    def calculate_channel_costs(self, monthly_sales: int, channel: str) -> Dict:
        """计算渠道成本"""
        fees = {
            "shopee": {"commission": 0.02, "payment_fee": 0.019, "logistics": 30},
            "rakuten": {"commission": 0.03, "monthly_fee": 595, "payment_fee": 0.02},
            "pchome": {"commission": 0.05, "payment_fee": 0.02, "logistics": 35},
            "momo": {"commission": 0.05, "payment_fee": 0.02, "logistics": 35},
        }

        fee_cfg = fees.get(channel, {"commission": 0.03, "monthly_fee": 0, "payment_fee": 0.02})
        avg_price = 400  # 假设平均客单价

        monthly_revenue = monthly_sales * avg_price
        commission = monthly_revenue * fee_cfg["commission"]
        payment_fee = monthly_revenue * fee_cfg.get("payment_fee", 0.02)
        monthly_fee = fee_cfg.get("monthly_fee", 0)
        logistics = monthly_sales * fee_cfg.get("logistics", 30)

        total_cost = commission + payment_fee + monthly_fee + logistics
        net_revenue = monthly_revenue - total_cost

        return {
            "channel": channel,
            "monthly_sales_count": monthly_sales,
            "gross_revenue": monthly_revenue,
            "commission": commission,
            "payment_fee": payment_fee,
            "monthly_fee": monthly_fee,
            "logistics_cost": logistics,
            "total_cost": total_cost,
            "net_revenue": net_revenue,
            "effective_rate": round(total_cost / monthly_revenue * 100, 1) if monthly_revenue > 0 else 0,
        }

    def generate_sales_plan(self, product: Dict, timeline_months: int = 12) -> Dict:
        """生成销售计划"""
        plan = {
            "product": product.get("name", ""),
            "timeline_months": timeline_months,
            "monthly_targets": [],
            "total_targets": {
                "units": 0,
                "revenue_twd": 0,
                "profit_twd": 0,
            }
        }

        # 销售曲线假设
        growth_curve = {
            1: {"units": 50, "growth": 0},
            2: {"units": 80, "growth": 60},
            3: {"units": 120, "growth": 50},
            4: {"units": 180, "growth": 50},
            5: {"units": 250, "growth": 39},
            6: {"units": 320, "growth": 28},
            7: {"units": 380, "growth": 19},
            8: {"units": 420, "growth": 11},
            9: {"units": 450, "growth": 7},
            10: {"units": 470, "growth": 4},
            11: {"units": 480, "growth": 2},
            12: {"units": 490, "growth": 2},
        }

        avg_price = product.get("target_price_twd", 400)
        cost_rate = 0.6  # 成本率约60%

        for month in range(1, timeline_months + 1):
            if month in growth_curve:
                data = growth_curve[month]
            else:
                data = {"units": 500 + month * 10, "growth": 1}

            units = data["units"]
            revenue = units * avg_price
            cost = revenue * cost_rate
            profit = revenue - cost

            plan["monthly_targets"].append({
                "month": month,
                "units": units,
                "revenue_twd": revenue,
                "cost_twd": cost,
                "profit_twd": profit,
                "growth_percent": data["growth"],
            })

            plan["total_targets"]["units"] += units
            plan["total_targets"]["revenue_twd"] += revenue
            plan["total_targets"]["profit_twd"] += profit

        return plan
