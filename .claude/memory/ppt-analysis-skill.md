---
name: ppt-data-analysis-skill
description: PPT分析和數據分析技能，可用於市場報告、數據提取、CAGR計算
type: reference
---

# PPT 數據分析技能

## 位置
- 腳本: `.claude/skills/full_analysis.py`
- Skill 文件: `.claude/skills/ppt-analysis.md`

## 使用方式
```bash
python .claude/skills/full_analysis.py <pptx_file>
```

## 功能
1. 讀取 PPT 內容（頁數、標題、表格、圖表）
2. 提取市場數據
3. 計算 CAGR 成長率
4. 生成 CSV 和 TXT 報告

## 依賴
- python-pptx (已安裝)
