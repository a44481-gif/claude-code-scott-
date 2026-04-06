# PowerPoint Analysis Skill
# PPT 檔案分析、數據提取、市場報告生成

## 觸發時機
- 用戶說「分析 PPT」、「分析簡報」、「讀取 PPT」
- 用戶打開 .pptx 檔案並要求分析內容
- 用戶需要「市場分析報告」、「數據提取」

## 使用命令
```bash
python .claude/skills/full_analysis.py <pptx_file_path>
```

## 功能說明
1. **PPT 內容分析** - 讀取所有頁面、提取文字、表格、圖表、圖片
2. **市場數據提取** - 自動識別並提取市場數據表格
3. **CAGR 計算** - 計算各賽道年複合成長率
4. **報告生成** - 生成結構化分析報告 (CSV + TXT)

## 輸出檔案
- `*_analysis.json` - PPT 完整分析結果
- `*_market.csv` - 市場數據表格
- `*_report_*.txt` - 分析報告

## 範例使用
```
python .claude/skills/full_analysis.py "d:/李總項目/市場報告.pptx"
python .claude/skills/full_analysis.py Global_Storage_Market_2025_2030.pptx
```

## 依賴套件
- python-pptx
