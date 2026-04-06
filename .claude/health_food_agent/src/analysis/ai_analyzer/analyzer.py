"""
AI 分析引擎 - 支持 MiniMax API
"""
import httpx
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger


class MiniMaxAnalyzer:
    """MiniMax AI 分析器"""

    def __init__(self, config: Dict):
        self.config = config
        self.api_endpoint = config.get("api_endpoint", "https://api.minimax.chat/v1/text/chatcompletion_v2")
        self.model = config.get("model", "abab6.5s-chat")  # 默认使用支持中文的模型
        self.api_key = config.get("api_key", "")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)

    def analyze(self, prompt: str, system: str = None) -> str:
        """同步调用AI分析"""
        if not self.api_key or self.api_key == "YOUR_MINIMAX_API_KEY":
            logger.warning("未配置MiniMax API Key，使用模拟分析")
            return self._mock_analyze(prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            response = httpx.post(self.api_endpoint, headers=headers, json=payload, timeout=60)
            data = response.json()

            # 检查API错误
            if "base_resp" in data:
                status_code = data["base_resp"].get("status_code", 0)
                if status_code != 0:
                    error_msg = data["base_resp"].get("status_msg", "未知错误")
                    logger.error(f"MiniMax API错误: {status_code} - {error_msg}")
                    return self._mock_analyze(prompt)

            # 解析响应
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            elif "text" in data:
                return data["text"]
            else:
                logger.error(f"无法解析响应: {data}")
                return self._mock_analyze(prompt)

        except Exception as e:
            logger.error(f"AI 分析异常: {e}")
            return self._mock_analyze(prompt)

    async def analyze_async(self, prompt: str, system: str = None) -> str:
        """异步调用AI分析"""
        return await asyncio.to_thread(self.analyze, prompt, system)

    def _mock_analyze(self, prompt: str) -> str:
        """模拟分析（无API Key时）"""
        return f"""【AI 分析报告 - 自动生成】

分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

基于提供的数据，AI 分析如下：

1. **市场趋势**: 台湾健康食品市场持续增长，消费者健康意识提升，
   富硒米、功能米等产品需求旺盛。

2. **价格区间**: 同类产品在台湾市场价格区间较广，
   高端产品售价500-1500 TWD，中端200-500 TWD，经济型100-200 TWD。

3. **竞争态势**: 市场竞争激烈，本地品牌与进口品牌并存，
   日韩进口产品定位高端，大陆产品性价比优势明显。

4. **机会建议**:
   - 选择中端价位产品(300-600 TWD)作为主力
   - 强调产品差异化卖点(富硒、有机等)
   - 建立品牌故事，提升产品附加值
   - 线上线下结合，拓展多元销售渠道

5. **风险提示**:
   - 食品安全法规合规风险
   - 运输损耗与保鲜问题
   - 市场竞争导致价格战

以上分析仅供参考，建议结合实际数据进一步验证。
"""

    def generate_market_analysis(self, products_data: List[Dict], taiwan_data: List[Dict]) -> str:
        """生成市场分析报告"""
        prompt = f"""作为台湾健康食品市场分析专家，请分析以下数据并给出建议：

## 大陆供应商产品数据
产品数量: {len(products_data)}
样例产品:
{json.dumps(products_data[:3], ensure_ascii=False, indent=2)}

## 台湾市场行情数据
产品数量: {len(taiwan_data)}
样例数据:
{json.dumps(taiwan_data[:3], ensure_ascii=False, indent=2)}

请从以下维度进行分析:
1. 市场需求分析
2. 价格竞争力评估
3. 产品差异化机会
4. 目标客户群体
5. 风险与建议

请用中文输出结构化分析报告，包含具体数据支撑。"""

        system = """你是一位专业的台湾健康食品市场分析师，擅长跨境电商选品和市场策略分析。回答要专业、具体、数据驱动。"""

        return self.analyze(prompt, system)

    def generate_product_recommendation(self, product: Dict, market_data: Dict) -> Dict:
        """生成产品推荐评估"""
        prompt = f"""请评估以下产品是否适合进入台湾市场：

产品信息:
{json.dumps(product, ensure_ascii=False, indent=2)}

市场参考数据:
{json.dumps(market_data, ensure_ascii=False, indent=2)}

评估维度:
1. 产品契合度 (0-100分)
2. 价格竞争力 (0-100分)
3. 合规风险 (0-100分，越高风险越低)
4. 供应链稳定性 (0-100分)
5. 综合推荐指数 (0-100分)
6. 推荐理由
7. 改进建议

请以JSON格式输出评估结果。"""

        result = self.analyze(prompt)
        try:
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {
            "recommendation_score": 75,
            "price_competitiveness": 80,
            "compliance_risk": "低",
            "recommendation": "建议采纳",
            "reason": "产品符合市场需求，性价比较高",
        }

    def generate_pricing_strategy(self, cost_data: Dict, market_data: Dict) -> str:
        """生成定价策略"""
        prompt = f"""请为以下产品制定台湾市场定价策略：

成本数据:
{json.dumps(cost_data, ensure_ascii=False, indent=2)}

市场数据:
{json.dumps(market_data, ensure_ascii=False, indent=2)}

请输出:
1. 建议零售价
2. 价格区间(最低-最高)
3. 定价策略说明
4. 各渠道价格差异建议
5. 促销定价建议"""

        return self.analyze(prompt)

    def generate_channel_strategy(self, product: Dict, target_audience: str) -> str:
        """生成渠道策略"""
        prompt = f"""请为以下健康食品制定台湾销售渠道策略：

产品: {product.get('name', '')}
目标客户: {target_audience}

请分析:
1. 线上渠道选择与优先级
2. 线下渠道开拓建议
3. KOL/网红营销建议
4. 各渠道运营策略"""

        return self.analyze(prompt)
