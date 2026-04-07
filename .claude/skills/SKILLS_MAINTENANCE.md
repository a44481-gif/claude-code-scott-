# 技能系統 - 完整文檔
更新時間: 2026-04-06

## 技能清單 (15個)

### 1. PPT 處理 (5個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `ppt_analyzer.py` | PPT 內容分析 | ✅ 穩定 |
| `ppt_extractor.py` | 通用內容提取 | ✅ 穩定 |
| `ppt_generator.py` | PPT 生成 v1 | ✅ 穩定 |
| `ppt_generator_v2.py` | PPT 生成 v2 | ✅ 優化 |
| `ppt_generator_v3.py` | PPT 生成 v3 增強版 | ✅ 最新 |

### 2. 數據分析 (1個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `data_analyzer.py` | 市場數據分析 | ✅ 穩定 |

### 3. 報告生成 (2個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `pdf_generator.py` | 直接生成 PDF | ✅ **新增/修復** |
| `auto_report.py` | 一鍵自動化報告 | ✅ **新增** |

### 4. 圖表生成 (1個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `chart_generator.py` | 柱/線/餅/雷達圖 | ✅ **新增** |

### 5. 數據讀取 (1個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `excel_reader.py` | Excel/CSV 讀取 | ✅ **新增** |

### 6. 批次處理 (1個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `batch_process.py` | 多檔案批次處理 | ✅ 穩定 |

### 7. 技能管理 (3個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `skill_optimizer.py` | 技能使用追蹤 | ✅ |
| `agent_skill_hub.py` | 代理技能共享 | ✅ |
| `full_analysis.py` | 一鍵分析流程 | ✅ |

---

## 使用方式

### 一鍵生成完整報告
```bash
python .claude/skills/auto_report.py <input_file> [options]

# 範例
python .claude/skills/auto_report.py "data.pptx" --all
python .claude/skills/auto_report.py "data.xlsx" --pdf --charts
python .claude/skills/auto_report.py "market.json" --pptx
```

### 單獨使用各技能
```bash
# 分析 PPT
python .claude/skills/ppt_analyzer.py data.pptx

# 分析數據
python .claude/skills/data_analyzer.py data.json

# 生成 PDF
python .claude/skills/pdf_generator.py market.json report.pdf

# 生成圖表
python .claude/skills/chart_generator.py market.json

# 讀取 Excel
python .claude/skills/excel_reader.py data.xlsx output.json

# 生成 PPT
python .claude/skills/ppt_generator_v3.py market.json output.pptx
```

---

## 輸出格式

### auto_report.py 輸出
```
reports/
├── *_analysis.json      # 原始分析數據
├── *_report.pdf         # PDF 報告
├── *_report.pptx        # PPT 報告
├── *_bar.png           # 柱狀圖
├── *_line.png          # 折線圖
├── *_pie.png           # 餅圖
├── *_cagr.png          # CAGR 排名圖
├── *_comparison.png     # 對比圖
└── *_dashboard.png      # 儀表板
```

---

## 持續改進

### 已完成改進
- [x] PDF 導出功能（使用 reportlab 直接生成）
- [x] 圖表類型（柱狀圖、折線圖、餅圖、CAGR排名圖、對比圖、儀表板）
- [x] Excel 讀取支援
- [x] 一鍵自動化報告生成

### 待改進
- [ ] 多語言支援
- [ ] 更多圖表自定義選項
- [ ] Web 界面

---

## 反饋與建議

如有問題或建議，請告訴我：
- 功能是否正常？
- 需要增加什麼新功能？
- 哪些可以改進？
