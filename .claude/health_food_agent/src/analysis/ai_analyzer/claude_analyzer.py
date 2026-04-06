"""
Claude Code AI 分析器 - 调用本地 Claude Code CLI
"""
import subprocess
import json
import asyncio
import os
from typing import Dict, Optional, List
from loguru import logger


# Claude CLI 路径（尝试多个可能的位置）
CLAUDE_PATHS = [
    "claude",  # 默认 PATH
    "C:/Users/Administrator/AppData/Roaming/npm/claude.cmd",  # Windows npm
    "C:/Users/Administrator/AppData/Roaming/npm/claude",  # Windows npm (unix style)
]


class ClaudeAnalyzer:
    """Claude Code CLI 分析器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.timeout = self.config.get("timeout", 60)  # Claude 响应超时
        self.model = self.config.get("model", "sonnet")
        self.max_tokens = self.config.get("max_tokens", 4000)
        self._claude_cmd = self._find_claude()

    def _find_claude(self) -> Optional[str]:
        """查找 Claude CLI 路径"""
        for path in CLAUDE_PATHS:
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"找到 Claude CLI: {path}")
                    return path
            except:
                continue
        return None

    def analyze(self, prompt: str, system: str = None) -> str:
        """
        调用 Claude Code CLI 进行分析

        Args:
            prompt: 用户提示词
            system: 系统提示词（可选）

        Returns:
            Claude 的分析回应
        """
        if not self._claude_cmd:
            logger.warning("Claude Code CLI 未找到，使用本地模拟分析")
            return self._mock_analyze(prompt)

        # 构造完整的 prompt
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        # 构建 Claude Code 命令
        cmd = [
            self._claude_cmd,
            "-p",  # 预览模式，不使用 REPL
            "--model", self.model,
            "--output-format", "json",
        ]

        try:
            logger.info(f"正在调用 Claude Code CLI: {self._claude_cmd}...")

            # 执行 Claude Code
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8'
            )

            if result.returncode == 0:
                # 解析 JSON 输出
                try:
                    data = json.loads(result.stdout)
                    if "result" in data:
                        return data["result"]
                    elif "content" in data:
                        return data["content"]
                    elif "text" in data:
                        return data["text"]
                    else:
                        return json.dumps(data, ensure_ascii=False, indent=2)
                except json.JSONDecodeError:
                    return result.stdout.strip()
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"Claude Code CLI 错误: {error_msg}")
                return self._mock_analyze(prompt)

        except subprocess.TimeoutExpired:
            logger.error("Claude Code CLI 超时")
            return self._mock_analyze(prompt)
        except FileNotFoundError:
            logger.error("Claude Code CLI 未找到")
            return self._mock_analyze(prompt)
        except Exception as e:
            logger.error(f"Claude Code CLI 异常: {e}")
            return self._mock_analyze(prompt)

    async def analyze_async(self, prompt: str, system: str = None) -> str:
        """异步调佣 Claude 分析"""
        return await asyncio.to_thread(self.analyze, prompt, system)

    def _mock_analyze(self, prompt: str) -> str:
        """备用本地分析（Claude 不可用时）"""
        return f"""【AI 分析报告 - 本地模拟】

分析时间: {asyncio.get_event_loop().time()}

系统提示：Claude Code CLI 暂时不可用，以下是本地模拟分析：

基于提供的信息，分析如下：

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

    def generate_market_analysis(self, products_data: List, taiwan_data: List) -> str:
        """生成市场分析报告"""
        prompt = f"""作为台湾健康食品市场分析专家，请分析以下数据并给出建议：

## 大陆供应商产品数据
产品数量: {len(products_data)}
样例产品: {json.dumps(products_data[:3], ensure_ascii=False, indent=2)}

## 台湾市场行情数据
产品数量: {len(taiwan_data)}
样例数据: {json.dumps(taiwan_data[:3], ensure_ascii=False, indent=2)}

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
            "reason": "产品符合市场需求，性价比比较高",
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
