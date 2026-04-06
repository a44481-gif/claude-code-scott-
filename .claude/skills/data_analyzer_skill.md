# Data Analyzer Skill
# 數據分析、趨勢預測、可視化報告生成

## 使用場景
- 用戶要求「數據分析」、「市場趨勢」、「生成報告」
- 用戶需要從 PPT/Excel 中提取數據進行分析
- 用戶需要 CAGR 計算、佔比分析、預測

## 觸發關鍵詞
- 數據分析
- 市場趨勢
- CAGR 計算
- 生成報告
- 導出數據
- 市場洞察

## 執行方式
```bash
# 基本分析
python .claude/skills/data_analyzer.py <ppt_analysis_json> [output_csv] [output_json]

# 完整流程（自動分析 PPT + 生成報告）
python .claude/skills/full_analysis.py <pptx_file>
```

## 支持的分析類型
1. **市場規模分析** - 5年累計、年度趨勢
2. **增速分析** - CAGR 計算、排名
3. **佔比分析** - 市場份額、分類統計
4. **預測分析** - 未來趨勢推估

## 輸出格式
- CSV: 市場數據表格
- JSON: 結構化分析結果
- 終端: 可讀的分析洞察報告
