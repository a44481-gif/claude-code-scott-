# -*- coding: utf-8 -*-
"""
商業計劃書生成器 - 自動生成標準商業計劃書
"""

import json
import os
from datetime import datetime
from typing import Dict, List


class BusinessPlanGenerator:
    """商業計劃書生成器"""

    def __init__(self):
        self.template = """
================================================================================
                              {title}
                           商業計劃書
================================================================================

版本: {version}
日期: {date}
聯絡窗口: {contact}
================================================================================

一、執行摘要
--------------------------------------------------------------------------------
{summary}

二、公司/項目介紹
--------------------------------------------------------------------------------
公司名稱: {company_name}
成立時間: {established_date}
主要業務: {main_business}
核心團隊: {team}

三、產品與服務
--------------------------------------------------------------------------------
3.1 核心產品
{products}

3.2 服務內容
{services}

3.3 技術優勢
{technology}

四、市場分析
--------------------------------------------------------------------------------
4.1 市場概況
{market_overview}

4.2 目標市場
{target_market}

4.3 市場規模預測
{market_forecast}

五、商業模式
--------------------------------------------------------------------------------
{business_model}

六、競爭分析
--------------------------------------------------------------------------------
{competition}

七、發展規劃
--------------------------------------------------------------------------------
{roadmap}

八、財務預測
--------------------------------------------------------------------------------
{financial}

九、風險評估
--------------------------------------------------------------------------------
{risks}

十、合作需求
--------------------------------------------------------------------------------
{cooperation}

================================================================================
聯絡窗口:
- Email: {email}
- 微信: {wechat}
================================================================================

文檔生成時間: {generated_at}
"""

    def generate(self, data: Dict, output_path: str = None) -> str:
        """生成商業計劃書"""
        # 填充默認值
        defaults = {
            "title": "項目商業計劃書",
            "version": "1.0",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "contact": "Scott | scott365888@gmail.com",
            "email": "scott365888@gmail.com",
            "wechat": "PTS9800",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": "本商業計劃書概述了項目的核心價值主張、市場機會和發展策略。",
            "company_name": "[公司名稱]",
            "established_date": "[成立日期]",
            "main_business": "[主營業務描述]",
            "team": "[核心團隊成員]",
            "products": "[核心產品列表]",
            "services": "[服務內容]",
            "technology": "[技術優勢說明]",
            "market_overview": "[市場概況]",
            "target_market": "[目標市場描述]",
            "market_forecast": "[市場規模預測]",
            "business_model": "[商業模式說明]",
            "competition": "[競爭對手分析]",
            "roadmap": "[發展規劃時間表]",
            "financial": "[財務預測數據]",
            "risks": "[風險評估與應對]",
            "cooperation": "[尋求的合作機會]"
        }

        # 合併數據
        plan_data = {**defaults, **data}

        # 生成文檔
        content = self.template.format(**plan_data)

        # 保存
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Business plan saved: {output_path}")

        return content

    def generate_presentation(self, data: Dict) -> str:
        """生成簡報版商業計劃"""
        slides = []

        # 封面
        slides.append(f"# {data.get('title', '商業計劃書')}")

        # 執行摘要
        slides.append("""
## 執行摘要
- 市場機會: {market_opportunity}
- 核心優勢: {core_advantage}
- 發展目標: {goal}
- 融資需求: {funding_need}
""".format(
            market_opportunity=data.get('market_opportunity', 'N/A'),
            core_advantage=data.get('core_advantage', 'N/A'),
            goal=data.get('goal', 'N/A'),
            funding_need=data.get('funding_need', 'N/A')
        ))

        # 團隊
        slides.append(f"""
## 核心團隊
{data.get('team', '[團隊介紹]')}
""")

        # 產品
        slides.append(f"""
## 產品/服務
{data.get('products', '[產品服務說明]')}
""")

        # 市場
        slides.append(f"""
## 市場分析
{data.get('market', '[市場分析內容]')}
""")

        # 聯絡
        slides.append("""
## 聯絡我們
- Email: scott365888@gmail.com
- 微信: PTS9800
""")

        return '\n\n'.join(slides)


def quick_business_plan(project_name: str, market_data: Dict = None) -> str:
    """快速生成商業計劃"""
    generator = BusinessPlanGenerator()

    data = {
        "title": project_name,
        "market_overview": f"""
市場現狀:
- 總市場規模: {market_data.get('total', '107,343億元') if market_data else '107,343億元'}
- 增長率: {market_data.get('growth', '16.6%') if market_data else '16.6%'}
- 主要驅動因素: 電動化、智能化、碳中和政策
""",
        "target_market": """
目標客戶:
- 新能源汽車廠商
- 儲能系統集成商
- AI數據中心運營商
- 工商業用戶
""",
        "core_advantage": "技術領先、資源整合能力、專業團隊",
        "goal": "3年內成為細分市場領導者",
        "funding_need": "天使輪: 500-1000萬元",
        "cooperation": """
尋求合作:
- 戰略投資者
- 產業合作夥伴
- 渠道合作夥伴
"""
    }

    output_path = f"{project_name}_商業計劃書_{datetime.now().strftime('%Y%m%d')}.txt"
    content = generator.generate(data, output_path)

    return content


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        # 生成示例
        result = quick_business_plan("儲能項目")
        print(result)
    else:
        project_name = sys.argv[1]
        result = quick_business_plan(project_name)
        print(f"\n[OK] Business plan generated for: {project_name}")
