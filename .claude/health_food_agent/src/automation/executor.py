"""
主执行器 - 协调所有模块
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from src.data_collection.crawlers.taobao_crawler import TaobaoCrawler, crawl_health_food_products
from src.data_collection.crawlers.taiwan_market_crawler import TaiwanMarketCrawler
from src.data_collection.crawlers.competitor_crawler import CompetitorCrawler
from src.analysis.ai_analyzer.analyzer import MiniMaxAnalyzer
from src.operations.product_selector import ProductSelector
from src.operations.pricing_engine import PricingEngine
from src.operations.supplier_scorer import SupplierScorer
from src.operations.channel_planner import ChannelPlanner
from src.operations.repackage_designer import RepackageDesigner
from src.reporting.report_generator import ReportGenerator
from src.automation.email_sender.smtp_sender import SMTPSender
from src.automation.email_sender.lark_mail_sender import LarkMailSender
from src.database.session import init_db, SessionLocal
from src.database.models import Product, Supplier, MarketAnalysis, TaskExecution


class HealthFoodAgent:
    """健康食品 AI 扩客代理人 - 主执行器"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.output_dir = Path(__file__).parent / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化模块
        self.taobao_crawler = TaobaoCrawler()
        self.taiwan_crawler = TaiwanMarketCrawler()
        self.competitor_crawler = CompetitorCrawler()
        self.ai_analyzer = MiniMaxAnalyzer(self.config.get("ai", {}))
        self.product_selector = ProductSelector()
        self.pricing_engine = PricingEngine(self.config.get("pricing", {}))
        self.supplier_scorer = SupplierScorer()
        self.channel_planner = ChannelPlanner(self.config.get("channels", {}))
        self.repackage_designer = RepackageDesigner()
        self.report_generator = ReportGenerator()
        self.smtp_sender = SMTPSender(self.config)
        self.lark_sender = LarkMailSender(self.config)

        # 数据存储
        self.products_data = []
        self.suppliers_data = []
        self.market_data = {}
        self.competitor_data = {}

        logger.info("健康食品 AI 扩客代理人初始化完成")

    def _load_config(self, config_path: str = None) -> dict:
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "settings.json"

        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    async def collect_data(self) -> Dict:
        """数据收集阶段"""
        logger.info("=" * 50)
        logger.info("开始数据收集阶段")
        logger.info("=" * 50)

        init_db()
        db = SessionLocal()
        task = self._log_task(db, "data_collection", "running")

        try:
            # 1. 收集大陆供应商数据
            logger.info("[1/4] 收集淘宝/1688产品数据...")
            self.products_data = await crawl_health_food_products()
            logger.info(f"   收集到 {len(self.products_data)} 条产品数据")

            # 2. 收集台湾市场数据
            logger.info("[2/4] 收集台湾市场价格数据...")
            self.market_data = await self.taiwan_crawler.get_market_price_ranges()
            logger.info(f"   收集到 {len(self.market_data)} 个品类的价格区间")

            # 3. 收集竞争对手数据
            logger.info("[3/4] 收集竞争对手数据...")
            self.competitor_data = await self.competitor_crawler.analyze_competitor_landscape()
            logger.info(f"   分析了 {len(self.competitor_data.get('competitors', []))} 个竞争对手")

            # 4. 收集供应商信息
            logger.info("[4/4] 收集供应商信息...")
            self.suppliers_data = self._extract_suppliers(self.products_data)

            # 保存数据
            self._save_raw_data()

            task.status = "success"
            task.completed_at = datetime.utcnow()
            task.records_collected = len(self.products_data)
            db.commit()

            logger.info("数据收集完成!")
            return {
                "products": len(self.products_data),
                "market_categories": len(self.market_data),
                "competitors": len(self.competitor_data.get("competitors", [])),
                "suppliers": len(self.suppliers_data),
            }

        except Exception as e:
            logger.error(f"数据收集失败: {e}")
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
            raise
        finally:
            db.close()

    async def analyze_and_decide(self) -> Dict:
        """AI分析与运营决策阶段"""
        logger.info("=" * 50)
        logger.info("开始AI分析与运营决策")
        logger.info("=" * 50)

        init_db()
        db = SessionLocal()
        task = self._log_task(db, "ai_analysis", "running")

        try:
            # 1. 市场分析
            logger.info("[1/5] 生成市场分析...")
            market_analysis = await self._generate_market_analysis()

            # 2. 选品决策
            logger.info("[2/5] 执行选品决策...")
            selected_products = self._execute_product_selection()

            # 3. 供应商评估
            logger.info("[3/5] 评估供应商...")
            evaluated_suppliers = self._evaluate_suppliers()

            # 4. 定价策略
            logger.info("[4/5] 制定定价策略...")
            pricing_data = self._generate_pricing_strategy(selected_products)

            # 5. 渠道规划
            logger.info("[5/5] 规划销售渠道...")
            channel_plan = self._plan_channels(selected_products)

            task.status = "success"
            task.completed_at = datetime.utcnow()
            db.commit()

            logger.info("AI分析完成!")
            return {
                "market_analysis": market_analysis,
                "selected_products": len(selected_products),
                "evaluated_suppliers": len(evaluated_suppliers),
                "pricing_data": pricing_data,
                "channel_plan": channel_plan,
            }

        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
            raise
        finally:
            db.close()

    async def generate_report(self) -> str:
        """生成分析报告"""
        logger.info("=" * 50)
        logger.info("开始生成报告")
        logger.info("=" * 50)

        # 整合所有数据
        report_data = {
            "market_analysis": self._summarize_market(),
            "product_selection": self._get_selected_products(),
            "supplier_evaluation": self._get_evaluated_suppliers(),
            "pricing_strategy": self._get_pricing_data(),
            "channel_plan": self._get_channel_plan(),
            "sales_plan": self._generate_sales_plan(),
            "packaging_compliance": self._get_packaging_notes(),
        }

        # 生成HTML报告
        report_path = self.report_generator.generate_full_report(report_data)
        logger.info(f"报告已生成: {report_path}")

        return report_path

    async def send_weekly_report(self):
        """发送周报"""
        logger.info("发送周报...")

        # 生成报告
        report_path = await self.generate_report()

        # 获取收件人
        recipients = self.config.get("reporting", {}).get("recipients",
                                                           ["h13751019800@163.com"])

        # 通过SMTP发送
        for email in recipients:
            self.smtp_sender.send_report(email, report_path)

        # 飞书邮件（如果启用）
        if self.lark_sender.enabled:
            await self.lark_sender.send_report(recipients[0], report_path)

        logger.info("周报发送完成!")

    # ========== 内部辅助方法 ==========

    def _log_task(self, db, task_name: str, status: str):
        """记录任务执行"""
        task = TaskExecution(
            task_name=task_name,
            task_type="auto",
            status=status,
            started_at=datetime.utcnow()
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def _save_raw_data(self):
        """保存原始数据"""
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(data_dir / f"products_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(self.products_data, f, ensure_ascii=False, indent=2)

        with open(data_dir / f"market_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(self.market_data, f, ensure_ascii=False, indent=2)

        logger.info(f"原始数据已保存: {data_dir}")

    def _extract_suppliers(self, products: List[Dict]) -> List[Dict]:
        """从产品数据提取供应商信息"""
        suppliers = {}
        for product in products:
            seller = product.get("seller", "")
            if seller and seller not in suppliers:
                suppliers[seller] = {
                    "name": seller,
                    "platform": product.get("platform", ""),
                    "rating": product.get("seller_rating", 0),
                    "total_orders": product.get("sales_count", 0),
                    "location": product.get("location", ""),
                }
        return list(suppliers.values())

    async def _generate_market_analysis(self) -> Dict:
        """生成市场分析"""
        prompt = f"""分析台湾健康食品市场的以下数据:

1. 价格区间数据:
{json.dumps(self.market_data, ensure_ascii=False, indent=2)}

2. 竞争格局:
{json.dumps(self.competitor_data.get('top_products', {}), ensure_ascii=False, indent=2)}

请输出:
- 市场规模估算
- 主流价格区间
- 消费者偏好
- 市场机会
- 风险因素"""

        analysis = self.ai_analyzer.analyze(prompt)
        return {
            "market_size": "台湾健康食品市场年规模约200-300亿台币",
            "trends": analysis,
            "price_range": self.market_data,
        }

    def _execute_product_selection(self) -> List[Dict]:
        """执行选品"""
        market_summary = {
            "avg_price": sum(d.get("avg", 500) for d in self.market_data.values()) / max(len(self.market_data), 1),
            "min_price": min((d.get("min", 100) for d in self.market_data.values()), default=100),
            "max_price": max((d.get("max", 1000) for d in self.market_data.values()), default=1000),
        }

        selected = self.product_selector.select_top_products(
            self.products_data,
            self.suppliers_data,
            market_summary,
            top_n=20
        )

        return selected

    def _evaluate_suppliers(self) -> List[Dict]:
        """评估供应商"""
        ranked = self.supplier_scorer.rank_suppliers(self.suppliers_data)
        return ranked[:10]

    def _generate_pricing_strategy(self, products: List[Dict]) -> Dict:
        """生成定价策略"""
        return self.pricing_engine.generate_pricing_report(products, self.market_data)

    def _plan_channels(self, products: List[Dict]) -> Dict:
        """规划渠道"""
        if not products:
            return {}

        top_product = products[0]
        return self.channel_planner.plan_launch_sequence(top_product)

    def _summarize_market(self) -> Dict:
        """市场摘要"""
        return {
            "market_size": "台湾健康食品市场年规模约200-300亿台币",
            "trends": "健康化、功能化、便利化趋势明显",
            "price_range": self.market_data,
            "competitors": list(self.competitor_data.get("competitors", [])),
        }

    def _get_selected_products(self) -> List[Dict]:
        """获取选品结果"""
        return self._execute_product_selection()

    def _get_evaluated_suppliers(self) -> List[Dict]:
        """获取供应商评估结果"""
        return self._evaluate_suppliers()

    def _get_pricing_data(self) -> Dict:
        """获取定价数据"""
        products = self._get_selected_products()
        return self.pricing_engine.generate_pricing_report(products, self.market_data)

    def _get_channel_plan(self) -> Dict:
        """获取渠道规划"""
        return self._plan_channels(self._get_selected_products())

    def _generate_sales_plan(self) -> Dict:
        """生成销售计划"""
        products = self._get_selected_products()
        if not products:
            return {}

        return self.channel_planner.generate_sales_plan(products[0])

    def _get_packaging_notes(self) -> Dict:
        """获取包装说明"""
        products = self._get_selected_products()
        if not products:
            return {}

        spec = self.repackage_designer.generate_packaging_spec(products[0])
        return {
            "product_name": spec["product_name"],
            "required_elements": spec["required_elements"],
            "design_notes": spec["design_notes"],
        }

    async def run_full_cycle(self):
        """执行完整周期"""
        logger.info("=" * 60)
        logger.info(" 健康食品 AI 扩客代理人 - 完整执行周期")
        logger.info("=" * 60)

        try:
            # 1. 数据收集
            collection_result = await self.collect_data()
            logger.info(f"数据收集结果: {collection_result}")

            # 2. AI分析
            analysis_result = await self.analyze_and_decide()
            logger.info(f"AI分析结果: {analysis_result}")

            # 3. 生成报告
            report_path = await self.generate_report()
            logger.info(f"报告路径: {report_path}")

            # 4. 发送邮件
            await self.send_weekly_report()

            logger.info("=" * 60)
            logger.info(" 完整执行周期完成!")
            logger.info("=" * 60)

            return {
                "status": "success",
                "collection": collection_result,
                "analysis": analysis_result,
                "report": report_path,
            }

        except Exception as e:
            logger.error(f"执行周期异常: {e}")
            return {"status": "failed", "error": str(e)}
