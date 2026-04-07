# -*- coding: utf-8 -*-
"""
翻譯工具 - 中英文互譯、專業術語詞典
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class TranslationTool:
    """翻譯工具"""

    # 專業術語詞典
    GLOSSARY = {
        # 儲能/新能源
        "電芯": "Battery Cell",
        "儲能": "Energy Storage",
        "新能源": "New Energy",
        "電動汽車": "Electric Vehicle (EV)",
        "工商儲能": "Commercial & Industrial Energy Storage",
        "家庭儲能": "Residential Energy Storage",
        "AI儲能": "AI Energy Storage",
        "BBU儲能": "BBU (Backup Battery Unit) Energy Storage",
        "CCS": "Cell Contact System / Integrated Busbar",
        "集成母排": "Integrated Busbar",
        "線束": "Wire Harness",
        "半導體": "Semiconductor",

        # 商務
        "市場規模": "Market Size",
        "市場份額": "Market Share",
        "複合成長率": "CAGR (Compound Annual Growth Rate)",
        "市場滲透率": "Market Penetration",
        "競爭格局": "Competitive Landscape",
        "目標市場": "Target Market",
        "銷售渠道": "Sales Channel",
        "客戶關係": "Customer Relationship",
        "合作夥伴": "Partner",

        # 報告
        "執行摘要": "Executive Summary",
        "市場分析": "Market Analysis",
        "SWOT分析": "SWOT Analysis",
        "財務預測": "Financial Projection",
        "風險評估": "Risk Assessment",
        "投資回報": "ROI (Return on Investment)",
    }

    def __init__(self):
        self.history = []

    def translate_term(self, term: str, target_lang: str = "en") -> str:
        """翻譯術語"""
        if target_lang == "en":
            return self.GLOSSARY.get(term, term)
        else:
            # 反向查找
            for cn, en in self.GLOSSARY.items():
                if en.lower() == term.lower():
                    return cn
        return term

    def translate_text(self, text: str, source_lang: str = "zh",
                      target_lang: str = "en") -> str:
        """翻譯文本"""
        result = text

        if source_lang == "zh" and target_lang == "en":
            for cn, en in self.GLOSSARY.items():
                result = result.replace(cn, en)
        elif source_lang == "en" and target_lang == "zh":
            for cn, en in self.GLOSSARY.items():
                result = result.replace(en, cn)

        # 記錄歷史
        self.history.append({
            "text": text,
            "result": result,
            "from": source_lang,
            "to": target_lang,
            "timestamp": datetime.now().isoformat()
        })

        return result

    def translate_report(self, content: str, direction: str = "zh2en") -> str:
        """翻譯報告"""
        lines = content.split('\n')
        translated = []

        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip()
                value = parts[1].strip()

                if direction == "zh2en":
                    key_trans = self.translate_text(key, "zh", "en")
                else:
                    key_trans = self.translate_text(key, "en", "zh")

                translated.append(f"{key_trans}: {value}")
            else:
                translated.append(self.translate_text(line, "zh" if direction == "zh2en" else "en", "zh"))

        return '\n'.join(translated)

    def export_glossary(self, output_path: str = "glossary.json"):
        """導出術語表"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.GLOSSARY, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[OK] Glossary exported: {output_path}")
        return output_path

    def add_term(self, chinese: str, english: str):
        """添加術語"""
        self.GLOSSARY[chinese] = english
        print(f"[OK] Term added: {chinese} = {english}")

    def get_translation_history(self) -> List[Dict]:
        """獲取翻譯歷史"""
        return self.history[-20:]  # 最近20條


def main():
    tool = TranslationTool()

    # 示例翻譯
    sample = """
執行摘要: 全球儲能市場快速增長
市場規模: 2025-2030年累計107,343億元
市場份額: 電動汽車佔比61.33%
CAGR: AI儲能增速最快達63.9%
    """

    print("=" * 50)
    print("Translation Tool Demo")
    print("=" * 50)

    print("\n[Original (Chinese)]:")
    print(sample)

    print("\n[Translated (English)]:")
    translated = tool.translate_report(sample, "zh2en")
    print(translated)

    print("\n[Glossary]:")
    for i, (k, v) in enumerate(list(tool.GLOSSARY.items())[:10]):
        print(f"  {k} -> {v}")


if __name__ == "__main__":
    main()
