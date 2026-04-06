"""
报告生成器
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Template
from loguru import logger


class ReportGenerator:
    """健康食品销售分析报告生成器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.template_dir = Path(__file__).parent / "templates"
        self.output_dir = Path(__file__).parent.parent.parent / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_full_report(self, data: Dict) -> str:
        """生成完整分析报告"""
        report_data = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_title": "健康食品销售分析报告",
            "market_analysis": data.get("market_analysis", {}),
            "product_selection": data.get("product_selection", []),
            "supplier_evaluation": data.get("supplier_evaluation", []),
            "pricing_strategy": data.get("pricing_strategy", {}),
            "channel_plan": data.get("channel_plan", {}),
            "sales_plan": data.get("sales_plan", {}),
            "packaging_compliance": data.get("packaging_compliance", {}),
            "executive_summary": self._generate_summary(data),
        }

        html = self._render_html(report_data)
        json_data = self._generate_json_report(report_data)

        # 保存文件
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = self.output_dir / f"health_food_report_{date_str}.html"
        json_path = self.output_dir / f"health_food_report_{date_str}.json"

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_data)

        logger.info(f"报告已生成: {html_path}")
        return str(html_path)

    def _generate_summary(self, data: Dict) -> Dict:
        """生成执行摘要"""
        return {
            "market_opportunity": "台湾健康食品市场年增长率约8-10%，功能米、减糖食品需求旺盛",
            "top_recommendation": f"建议优先引入{data.get('top_product', '富硒米')}，预计毛利率35%以上",
            "channel_strategy": "线上渠道为主，虾皮首发，乐天扩充，社交媒体配合",
            "key_risks": "食品安全法规合规、供应商稳定性、市场竞争",
            "next_actions": [
                "联系TOP 3供应商获取样品",
                "完成产品包装设计初稿",
                "申请虾皮店铺",
                "制定网红合作计划",
            ],
        }

    def _render_html(self, data: Dict) -> str:
        """渲染HTML报告"""
        template_path = self.template_dir / "report_template.html"

        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                template = Template(f.read())
        else:
            template = Template(self._get_default_template())

        return template.render(**data)

    def _generate_json_report(self, data: Dict) -> str:
        """生成JSON格式报告"""
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)

    def _get_default_template(self) -> str:
        """默认HTML模板"""
        return """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{report_title}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'PingFang TC', 'Microsoft JhengHei', sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 40px 30px; border-radius: 12px; margin-bottom: 30px; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header .date { opacity: 0.9; }
        .card { background: white; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .card h2 { color: #2E7D32; font-size: 20px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #E8F5E9; }
        .card h3 { color: #388E3C; font-size: 16px; margin: 15px 0 10px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .summary-item { background: #E8F5E9; padding: 20px; border-radius: 8px; }
        .summary-item h4 { color: #2E7D32; margin-bottom: 8px; }
        .summary-item .value { font-size: 24px; font-weight: bold; color: #1B5E20; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th { background: #4CAF50; color: white; padding: 12px; text-align: left; }
        td { padding: 10px 12px; border-bottom: 1px solid #E0E0E0; }
        tr:hover { background: #F5F5F5; }
        .tag { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin: 2px; }
        .tag-success { background: #C8E6C9; color: #2E7D32; }
        .tag-warning { background: #FFF9C4; color: #F57F17; }
        .tag-danger { background: #FFCDD2; color: #C62828; }
        .progress { background: #E0E0E0; border-radius: 10px; height: 10px; overflow: hidden; }
        .progress-bar { background: #4CAF50; height: 100%; border-radius: 10px; }
        .actions { display: flex; flex-direction: column; gap: 10px; }
        .action-item { background: #F5F5F5; padding: 12px 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px; }
        .action-item .num { background: #4CAF50; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; }
        .footer { text-align: center; padding: 30px; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{report_title}}</h1>
            <div class="date">生成时间: {{generated_at}}</div>
        </div>

        <div class="card">
            <h2>执行摘要</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h4>市场机会</h4>
                    <div>{{executive_summary.market_opportunity}}</div>
                </div>
                <div class="summary-item">
                    <h4>重点推荐</h4>
                    <div>{{executive_summary.top_recommendation}}</div>
                </div>
                <div class="summary-item">
                    <h4>渠道策略</h4>
                    <div>{{executive_summary.channel_strategy}}</div>
                </div>
                <div class="summary-item">
                    <h4>关键风险</h4>
                    <div>{{executive_summary.key_risks}}</div>
                </div>
            </div>
        </div>

        {% if market_analysis %}
        <div class="card">
            <h2>市场分析</h2>
            <h3>市场规模</h3>
            <p>{{market_analysis.market_size or '待分析'}}</p>
            <h3>消费趋势</h3>
            <p>{{market_analysis.trends or '待分析'}}</p>
            <h3>价格区间</h3>
            <p>{{market_analysis.price_range or '待分析'}}</p>
        </div>
        {% endif %}

        {% if product_selection %}
        <div class="card">
            <h2>精选产品 ({{product_selection|length}} 款)</h2>
            <table>
                <thead>
                    <tr>
                        <th>产品名称</th>
                        <th>类别</th>
                        <th>采购价(CNY)</th>
                        <th>建议售价(TWD)</th>
                        <th>AI评分</th>
                        <th>推荐等级</th>
                    </tr>
                </thead>
                <tbody>
                    {% for product in product_selection[:10] %}
                    <tr>
                        <td>{{product.name or product.get('product_name', '')}}</td>
                        <td>{{product.category or '-'}}</td>
                        <td>{{product.price or product.get('cost_cny', '-')}}</td>
                        <td>{{product.target_price_twd or product.get('final_price_twd', '-')}}</td>
                        <td>{{product.ai_recommendation_score or product.get('total_score', '-')}}</td>
                        <td>
                            {% set score = product.ai_recommendation_score or product.get('total_score', 0) %}
                            {% if score >= 80 %}
                            <span class="tag tag-success">强烈推荐</span>
                            {% elif score >= 60 %}
                            <span class="tag tag-success">推荐</span>
                            {% else %}
                            <span class="tag tag-warning">观望</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        {% if supplier_evaluation %}
        <div class="card">
            <h2>供应商评估</h2>
            <table>
                <thead>
                    <tr>
                        <th>供应商</th>
                        <th>平台</th>
                        <th>评分</th>
                        <th>认证</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
                    {% for supplier in supplier_evaluation[:10] %}
                    <tr>
                        <td>{{supplier.supplier_name or supplier.name}}</td>
                        <td>{{supplier.platform}}</td>
                        <td>{{supplier.total_score or supplier.get('overall_score', '-')}}</td>
                        <td>{{supplier.certification or supplier.get('cert', '-')}}</td>
                        <td>
                            {% set status = supplier.status %}
                            {% if '认证' in status %}
                            <span class="tag tag-success">{{status}}</span>
                            {% else %}
                            <span class="tag tag-warning">{{status}}</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        {% if channel_plan %}
        <div class="card">
            <h2>渠道规划</h2>
            {% for phase in channel_plan.get('phases', []) %}
            <h3>第{{phase.phase}}阶段: {{phase.channel}}</h3>
            <p><strong>时间:</strong> {{phase.timeline}}</p>
            <p><strong>策略:</strong> {{phase.strategy}}</p>
            {% endfor %}
        </div>
        {% endif %}

        <div class="card">
            <h2>下一步行动</h2>
            <div class="actions">
                {% for action in executive_summary.next_actions %}
                <div class="action-item">
                    <span class="num">{{loop.index}}</span>
                    <span>{{action}}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="footer">
            <p>本报告由 AI 扩客代理人自动生成 | 数据仅供参考</p>
        </div>
    </div>
</body>
</html>"""

    def generate_weekly_summary(self, sales_data: Dict) -> str:
        """生成周报摘要"""
        return f"""# 健康食品销售周报

生成时间: {datetime.now().strftime('%Y-%m-%d')}

## 本周销售概况
- 订单数: {sales_data.get('orders', 'N/A')}
- 销售额: {sales_data.get('revenue', 'N/A')} TWD
- 转化率: {sales_data.get('conversion', 'N/A')}%

## 热销产品
{sales_data.get('top_products', '暂无数据')}

## 问题与改进
{sales_data.get('issues', '暂无问题')}
"""
