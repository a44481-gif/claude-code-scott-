"""
Prompt Engineer Agent - 提示詞工程師 Agent
負責設計、優化、測試和管理 AI 提示詞
"""

import os
import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None


class PromptLibrary:
    """提示詞庫管理"""

    def __init__(self, library_path: str = None):
        if library_path is None:
            library_path = Path(__file__).parent / "prompt_library"
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
        self._ensure_structure()

    def _ensure_structure(self):
        """確保目錄結構存在"""
        dirs = ["it_news", "report", "content", "_templates", "test_results", "recommendations"]
        for d in dirs:
            (self.library_path / d).mkdir(parents=True, exist_ok=True)

    def list_prompts(self, category: str = None) -> list:
        """列出所有提示詞"""
        prompts = []
        search_dirs = [self.library_path / category] if category else [
            self.library_path / d for d in ["it_news", "report", "content"] if not d.startswith("_")
        ]

        for d in search_dirs:
            if d.exists():
                for f in d.glob("*.yaml"):
                    data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
                    prompts.append({
                        "id": f.stem,
                        "path": str(f),
                        "category": d.name,
                        **data.get("prompt", {})
                    })
        return prompts

    def save_prompt(self, prompt_data: dict, category: str, filename: str):
        """保存提示詞"""
        filepath = self.library_path / category / f"{filename}.yaml"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # 包裝為標準格式
        wrapper = {"prompt": prompt_data}
        filepath.write_text(yaml.dump(wrapper, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return filepath

    def load_prompt(self, prompt_id: str) -> Optional[dict]:
        """加載提示詞"""
        for d in ["it_news", "report", "content"]:
            filepath = self.library_path / d / f"{prompt_id}.yaml"
            if filepath.exists():
                data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
                return data.get("prompt", {})
        return None


class PromptEngineer:
    """提示詞工程師核心類"""

    def __init__(self, library_path: str = None):
        self.library = PromptLibrary(library_path)

    def design(self, task: str, context: dict = None, requirements: list = None) -> dict:
        """設計新提示詞"""
        task_lower = task.lower()

        # 根據任務類型生成提示詞模板
        if "news" in task_lower or "摘要" in task_lower:
            prompt = self._design_news_summary_prompt(context or {})
        elif "report" in task_lower or "報告" in task_lower:
            prompt = self._design_report_prompt(context or {})
        elif "翻譯" in task_lower or "translation" in task_lower:
            prompt = self._design_translation_prompt(context or {})
        elif "分析" in task_lower or "analysis" in task_lower:
            prompt = self._design_analysis_prompt(context or {})
        else:
            prompt = self._design_generic_prompt(task, context or {}, requirements or [])

        # 添加元數據
        prompt["id"] = f"{task}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        prompt["created"] = datetime.now().strftime("%Y-%m-%d")
        prompt["model"] = "claude-sonnet-4"
        prompt["task"] = task

        return prompt

    def _design_news_summary_prompt(self, context: dict) -> dict:
        """設計新聞摘要提示詞"""
        sources = context.get("sources", ["TechCrunch", "AnandTech", "IT之家"])
        languages = context.get("languages", ["zh", "en"])

        return {
            "name": "IT新聞摘要",
            "version": "1.0",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "system": f"""你是一個專業的科技行業分析師，擅長從多個來源快速提取關鍵信息。

## 你的優勢
- 熟悉 {"、".join(sources)} 等科技新聞來源
- 能夠處理 {"中文" if "zh" in languages else ""}{"英文" if "en" in languages else ""} 新聞
- 善於識別新聞中的關鍵人物、公司和技術

## 分析框架
1. 新聞事實（5W1H）
2. 行業影響評估
3. 關聯技術/公司分析
4. 趨勢判斷""",
            "user_template": """請分析以下新聞，生成結構化摘要：

## 要求
1. 每篇新聞提取：標題、來源、時間、關鍵人物/公司、要點
2. 按行業分類：AI基礎設施 / PC零組件 / 存儲 / 雲服務 / 其他
3. 生成50字內的AI摘要
4. 標註新聞重要性（1-5星）

## 新聞內容
{content}

## 輸出格式（JSON）
```json
{{
  "summaries": [
    {{
      "title": "標題",
      "source": "來源",
      "time": "時間",
      "key_entities": ["人物/公司"],
      "category": "分類",
      "summary": "50字摘要",
      "importance": 4
    }}
  ],
  "trends": ["趨勢1", "趨勢2"],
  "ai_summary": "總體分析100字"
}}
```""",
            "variables": [
                {"name": "sources", "type": "list", "description": "新聞來源列表"},
                {"name": "languages", "type": "list", "description": "語言列表"},
                {"name": "content", "type": "text", "description": "新聞內容"}
            ],
            "few_shot_examples": [
                {
                    "input": {"content": "NVIDIA發布新一代GPU...", "sources": ["TechCrunch"]},
                    "output": {"summaries": [...], "trends": ["GPU性能提升"], "ai_summary": "..."}
                }
            ],
            "evaluation_criteria": [
                "是否覆蓋所有新聞來源",
                "摘要是否準確且簡潔",
                "分類是否正確",
                "是否包含關鍵人物/公司",
                "重要性評級是否合理"
            ],
            "optimization_tips": [
                "使用Few-shot examples提高一致性",
                "添加角色定義提升專業性",
                "明確輸出格式減少解析錯誤"
            ]
        }

    def _design_report_prompt(self, context: dict) -> dict:
        """設計報告生成提示詞"""
        report_type = context.get("type", "daily_brief")
        sections = context.get("sections", ["摘要", "詳情", "建議"])

        return {
            "name": f"{report_type}報告生成",
            "version": "1.0",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "system": """你是一個專業的商業報告分析師，擅長將複雜數據轉化為清晰的商業洞察。

## 報告原則
- 數據驅動：基於事實，而非推測
- 結構清晰：使用層級結構，重點突出
- 可操作性：每個洞察都有明確的行動建議
- 簡潔專業：避免冗餘，用數據說話""",
            "user_template": """生成{report_type}，包含以下章節：{sections}

## 數據輸入
{data}

## 輸出要求
- 語言：{language}
- 格式：Markdown
- 長度：{length}
- 受眾：{audience}

## 結構要求
{structure}

## 輸出
""",
            "variables": [
                {"name": "report_type", "type": "string", "default": report_type},
                {"name": "sections", "type": "list", "default": sections},
                {"name": "data", "type": "text", "description": "原始數據"},
                {"name": "language", "type": "enum", "options": ["中文", "英文", "中英雙語"], "default": "中文"},
                {"name": "length", "type": "enum", "options": ["簡短", "中等", "詳細"], "default": "中等"},
                {"name": "audience", "type": "string", "default": "專業投資者"},
                {"name": "structure", "type": "text", "description": "自定義結構要求"}
            ],
            "evaluation_criteria": [
                "內容完整覆蓋要求章節",
                "數據引用準確",
                "洞察具有深度",
                "建議具有可操作性"
            ]
        }

    def _design_translation_prompt(self, context: dict) -> dict:
        """設計翻譯提示詞"""
        return {
            "name": "專業領域翻譯",
            "version": "1.0",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "system": """你是一個專業的科技領域翻譯專家，擅長精準翻譯AI、半導體、PC等技術內容。

## 翻譯原則
- 術語一致性：使用行業標準術語
- 上下文理解：根據上下文選擇最準確的譯法
- 本地化：符合目標語言的表達習慣
- 保留原意：在通順的基礎上最大程度保留原意""",
            "user_template": """將以下{source_lang}內容翻譯為{target_lang}：

## 領域
{domain}

## 術語表（如有）
{glossary}

## 原文
{content}

## 翻譯要求
- 風格：{style}
- 術語：{terminology}
- 保留：{preserve}

## 輸出
""",
            "variables": [
                {"name": "source_lang", "type": "enum", "options": ["中文", "英文", "日文", "韓文"]},
                {"name": "target_lang", "type": "enum", "options": ["中文", "英文", "日文", "韓文"]},
                {"name": "domain", "type": "enum", "options": ["AI/ML", "半導體", "PC硬體", "雲計算", "一般科技"], "default": "一般科技"},
                {"name": "glossary", "type": "text", "default": "無"},
                {"name": "content", "type": "text", "description": "待翻譯內容"},
                {"name": "style", "type": "enum", "options": ["正式", "中性", "輕鬆"], "default": "正式"},
                {"name": "terminology", "type": "enum", "options": ["標準術語", "新興術語保留原文", "全部保留原文"], "default": "標準術語"},
                {"name": "preserve", "type": "list", "options": ["品牌名", "型號", "術語", "人名"], "default": ["品牌名", "型號"]}
            ],
            "evaluation_criteria": [
                "術語翻譯準確",
                "語境理解正確",
                "表達通順自然",
                "格式保持一致"
            ]
        }

    def _design_analysis_prompt(self, context: dict) -> dict:
        """設計分析提示詞"""
        analysis_type = context.get("type", "general")
        return {
            "name": f"{analysis_type}分析",
            "version": "1.0",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "system": """你是一個專業的商業/技術分析師，擅長深入分析問題並提供結構化洞察。

## 分析框架
- 現狀描述：清晰界定分析對象
- 原因分析：多角度剖析根本原因
- 影響評估：正面/負面/風險
- 趨勢預判：基於數據的趨勢判斷
- 建議行動：具體可執行的建議""",
            "user_template": """對以下內容進行{analysis_type}分析：

## 分析目標
{objective}

## 分析維度
{dimensions}

## 輸入內容
{content}

## 輸出格式
{format}

## 分析
""",
            "variables": [
                {"name": "analysis_type", "type": "enum", "options": ["競爭分析", "技術趨勢分析", "市場分析", "風險分析", "SWOT分析"], "default": analysis_type},
                {"name": "objective", "type": "text", "description": "分析目標"},
                {"name": "dimensions", "type": "list", "default": ["市場", "技術", "競爭", "趨勢"]},
                {"name": "content", "type": "text", "description": "分析內容"},
                {"name": "format", "type": "enum", "options": ["Markdown", "JSON", "表格", "圖表描述"], "default": "Markdown"}
            ],
            "evaluation_criteria": [
                "分析維度完整",
                "邏輯推理嚴謹",
                "結論有數據支撐",
                "建議具有可操作性"
            ]
        }

    def _design_generic_prompt(self, task: str, context: dict, requirements: list) -> dict:
        """設計通用提示詞"""
        return {
            "name": f"通用任務：{task}",
            "version": "1.0",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "system": """你是一個專業的AI助手，擅長理解和完成各類任務。

## 通用原則
- 準確理解用戶需求
- 提供結構化、清晰的輸出
- 在不確定時主動詢問
- 追求準確性，而非速度""",
            "user_template": """任務：{task}

## 上下文
{context}

## 要求
{requirements}

## 輸入
{input}

## 輸出
""",
            "variables": [
                {"name": "task", "type": "string", "default": task},
                {"name": "context", "type": "text", "description": "任務背景"},
                {"name": "requirements", "type": "list", "default": requirements},
                {"name": "input", "type": "text", "description": "任務輸入"}
            ],
            "evaluation_criteria": [
                "是否完成任務目標",
                "輸出格式是否符合要求",
                "內容質量評估"
            ]
        }

    def test(self, prompt_id: str = None, test_data: dict = None) -> dict:
        """測試提示詞"""
        if prompt_id:
            prompt = self.library.load_prompt(prompt_id)
            if not prompt:
                return {"error": f"Prompt '{prompt_id}' not found"}
        else:
            prompt = test_data

        # 構建測試結果
        results = {
            "test_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "prompt_id": prompt.get("id", "unknown"),
            "tested_at": datetime.now().isoformat(),
            "criteria": prompt.get("evaluation_criteria", []),
            "status": "ready_to_test",
            "note": "需要AI模型執行 actual_test"
        }
        return results

    def optimize(self, prompt_id: str, feedback: dict = None) -> dict:
        """優化提示詞"""
        prompt = self.library.load_prompt(prompt_id)
        if not prompt:
            return {"error": f"Prompt '{prompt_id}' not found"}

        # 生成優化建議
        optimizations = []

        # 基於評估標準的建議
        if "evaluation_criteria" in prompt:
            optimizations.append({
                "area": "evaluation_criteria",
                "suggestion": "確保每個評估標準都是可量化的",
                "priority": "high"
            })

        # 基於優化技巧的建議
        if "optimization_tips" in prompt:
            optimizations.append({
                "area": "optimization_tips",
                "suggestion": prompt["optimization_tips"][0] if prompt["optimization_tips"] else "",
                "priority": "medium"
            })

        # 添加系統提示詞優化建議
        if "system" in prompt:
            system_len = len(prompt["system"])
            if system_len < 200:
                optimizations.append({
                    "area": "system_prompt",
                    "suggestion": "系統提示詞可能太短，建議添加更多上下文和約束",
                    "priority": "high"
                })
            elif system_len > 2000:
                optimizations.append({
                    "area": "system_prompt",
                    "suggestion": "系統提示詞可能太長，考慮簡化並使用變量替換重複內容",
                    "priority": "medium"
                })

        return {
            "prompt_id": prompt_id,
            "optimized_at": datetime.now().strftime("%Y-%m-%d"),
            "suggestions": optimizations,
            "estimated_improvement": "10-20% better consistency"
        }

    def save(self, prompt: dict, category: str = "general"):
        """保存提示詞到庫"""
        if "/" not in prompt.get("id", ""):
            prompt_id = prompt.get("id", f"prompt_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        else:
            prompt_id = prompt.get("id")

        # 根據類別映射
        category_map = {
            "news": "it_news",
            "摘要": "it_news",
            "報告": "report",
            "report": "report",
            "翻譯": "content",
            "翻譯": "content"
        }

        save_category = category_map.get(category, category)
        if save_category not in ["it_news", "report", "content"]:
            save_category = "content"

        filepath = self.library.save_prompt(prompt, save_category, prompt_id)
        return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="Prompt Engineer Agent")
    parser.add_argument("--mode", choices=["design", "test", "optimize", "library", "save"],
                        default="library", help="操作模式")
    parser.add_argument("--task", type=str, help="任務描述")
    parser.add_argument("--prompt", type=str, help="提示詞ID")
    parser.add_argument("--category", type=str, default="general", help="保存類別")
    parser.add_argument("--context", type=str, help="JSON格式的上下文")
    parser.add_argument("--output", type=str, help="輸出文件")

    args = parser.parse_args()
    pe = PromptEngineer()

    if args.mode == "design":
        context = json.loads(args.context) if args.context else {}
        prompt = pe.design(args.task or "通用任務", context)
        print(yaml.dump({"prompt": prompt}, allow_unicode=True, sort_keys=False))

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                yaml.dump({"prompt": prompt}, f, allow_unicode=True, sort_keys=False)
            print(f"已保存到: {args.output}")

    elif args.mode == "test":
        results = pe.test(args.prompt)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.mode == "optimize":
        results = pe.optimize(args.prompt)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.mode == "library":
        prompts = pe.library.list_prompts()
        if RICH_AVAILABLE:
            table = Table(title="Prompt Library")
            table.add_column("ID")
            table.add_column("Name")
            table.add_column("Category")
            table.add_column("Version")

            for p in prompts:
                table.add_row(p.get("id", ""), p.get("name", ""),
                             p.get("category", ""), p.get("version", ""))
            console.print(table)
        else:
            for p in prompts:
                print(f"- {p.get('id')}: {p.get('name')} ({p.get('category')}) v{p.get('version')}")

    elif args.mode == "save":
        if args.output and Path(args.output).exists():
            with open(args.output, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            prompt = data.get("prompt", data)
        else:
            print("請提供有效的 --output 文件路徑")
            return

        filepath = pe.save(prompt, args.category)
        print(f"已保存到: {filepath}")


if __name__ == "__main__":
    main()
