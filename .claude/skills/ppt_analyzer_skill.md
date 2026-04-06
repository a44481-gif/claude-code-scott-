# PPT Analyzer Skill
# 分析 PowerPoint 檔案內容、提取數據、生成報告

## 使用場景
- 用戶要求「分析 PPT」、「讀取 PPT 內容」、「PPT 數據提取」
- 用戶打開 .pptx 檔案並要求分析
- 用戶需要從 PPT 中提取表格數據

## 觸發關鍵詞
- 分析 PPT
- 讀取 PPT
- PPT 內容
- 提取 PPT 數據
- 市場分析報告

## 執行方式
```bash
python .claude/skills/ppt_analyzer.py <pptx_file_path> [output_json_path]
```

## 輸出格式
- JSON 格式的完整 PPT 分析結果
- 包含：頁數、標題、表格、圖表、圖片統計
- 支持導出為 CSV/Excel

## 範例輸出
```
Total Slides: 18
Total Tables: 12
Total Images: 3

[Slide 3] 市場規模總覽
  - 包含 1 個表格
```
