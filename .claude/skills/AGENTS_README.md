# Claude Code Agent - PPT 數據分析技能共享

## 技能位置
所有 PPT 分析腳本位於專案根目錄的 `.claude/skills/` 資料夾：

```
.claude/skills/
├── full_analysis.py    # 一鍵分析 PPT（主要入口）
├── ppt_analyzer.py    # PPT 內容讀取
├── data_analyzer.py   # 數據分析
├── ppt-analysis.md    # 技能說明文件
├── ppt_analyzer_skill.md
└── data_analyzer_skill.md
```

## 快速使用
```bash
python .claude/skills/full_analysis.py <pptx_file>
```

## 觸發關鍵詞
- 「分析 PPT」「分析簡報」
- 「市場分析」「數據提取」
- 「CAGR 計算」「生成報告」

## 功能
1. 讀取 PPT 頁面、標題、表格、圖表、圖片
2. 自動識別市場數據表格
3. 計算 CAGR 年複合成長率
4. 生成 CSV + TXT 分析報告

## 依賴
- python-pptx（已安裝）
- Python 3.7+
