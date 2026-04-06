# 技能系統 - 每日持續優化

## 當前技能清單

### 1. PPT 處理技能
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `ppt_analyzer.py` | PPT 內容分析 | ✅ 穩定 |
| `ppt_extractor.py` | 通用內容提取 | ✅ 穩定 |
| `ppt_generator.py` | PPT 生成 v1 | ✅ 穩定 |
| `ppt_generator_v2.py` | PPT 生成 v2 | ✅ 優化 |
| `ppt_generator_v3.py` | PPT 生成 v3 增強版 | ✅ 最新 |
| `full_analysis.py` | 一鍵分析流程 | ✅ 穩定 |
| `batch_process.py` | 批次處理 | ✅ 穩定 |

### 2. 數據分析技能
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `data_analyzer.py` | 市場數據分析 | ✅ 穩定 |

### 3. PDF 導出技能
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `pdf_exporter.py` | PDF 導出 | ⚠️ 待優化 |

### 4. 技能優化系統
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `skill_optimizer.py` | 技能追蹤優化 | ✅ 新增 |

---

## 持續優化計劃

### 每日任務
1. 記錄技能使用情況
2. 收集用戶反饋
3. 分析成功率
4. 識別改進點

### 每週任務
1. 審視使用統計
2. 部署新功能
3. 更新技能文檔
4. 優化腳本性能

### 待改進項目
1. PDF 導出功能（需要 PowerPoint COM 環境）
2. 增加更多圖表類型
3. 支援更多數據源
4. 自動化報告生成

---

## 使用方式

```bash
# 記錄使用
python .claude/skills/skill_optimizer.py use success ppt_generator

# 添加反饋
python .claude/skills/skill_optimizer.py feedback ppt_generator "需要支援更多圖表"

# 查看統計
python .claude/skills/skill_optimizer.py stats

# 記錄學習
python .claude/skills/skill_optimizer.py learn "避免在 f-string 中使用反斜槓"
```

---

## 反饋收集

如有任何問題或建議，請告訴我：
- 哪些功能最有用？
- 哪些需要改進？
- 需要增加什麼新功能？
