# 技能系統 - 完整文檔
更新時間: 2026-04-06

## 技能清單 (22個)

### 1. PPT 處理 (5個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `ppt_analyzer.py` | PPT 內容分析 | ✅ |
| `ppt_extractor.py` | 通用內容提取 | ✅ |
| `ppt_generator.py` | PPT 生成 v1 | ✅ |
| `ppt_generator_v2.py` | PPT 生成 v2 | ✅ |
| `ppt_generator_v3.py` | PPT 生成 v3 | ✅ |

### 2. 數據分析 (1個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `data_analyzer.py` | 市場數據分析、CAGR計算 | ✅ |

### 3. 報告生成 (2個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `pdf_generator.py` | 直接生成 PDF | ✅ |
| `auto_report.py` | 一鍵自動化報告 | ✅ |

### 4. 圖表生成 (1個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `chart_generator.py` | 柱/線/餅/雷達圖/儀表板 | ✅ |

### 5. 數據讀取 (1個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `excel_reader.py` | Excel/CSV 讀取 | ✅ |

### 6. 批次處理 (1個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `batch_process.py` | 多檔案批次處理 | ✅ |

### 7. 商務工具 (6個) 🆕
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `market_research.py` | 市場研究、行業分析 | ✅ |
| `customer_manager.py` | 客戶管理、CRM | ✅ |
| `business_plan_generator.py` | 商業計劃書生成 | ✅ |
| `meeting_manager.py` | 會議安排、議程管理 | ✅ |
| `decision_analyzer.py` | 決策分析、SWOT、風險評估 | ✅ |
| `translation_tool.py` | 中英文翻譯、專業術語 | ✅ |

### 8. 系統工具 (3個) 🆕
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `data_backup.py` | 數據備份、還原 | ✅ |
| `tag_manager.py` | 文件標籤分類整理 | ✅ |
| `skill_optimizer.py` | 技能使用追蹤優化 | ✅ |

### 9. 技能管理 (2個)
| 腳本 | 功能 | 狀態 |
|------|------|------|
| `agent_skill_hub.py` | 代理技能共享中心 | ✅ |
| `full_analysis.py` | 一鍵分析流程 | ✅ |

---

## 使用方式

### 一鍵生成完整報告
```bash
python .claude/skills/auto_report.py <input_file> --all
```

### 商務工具使用

```bash
# 市場研究
python .claude/skills/market_research.py "儲能市場" "電芯,電動汽車" "BYD,Tesla"

# 客戶管理
python .claude/skills/customer_manager.py add "張三" "ABC公司" "zhang@abc.com" "wx123"

# 商業計劃書
python .claude/skills/business_plan_generator.py "新項目"

# 會議管理
python .claude/skills/meeting_manager.py schedule "項目評審" "2026-04-15" "14:00"

# 決策分析
python .claude/skills/decision_analyzer.py

# 翻譯
python .claude/skills/translation_tool.py

# 數據備份
python .claude/skills/data_backup.py backup <file>

# 標籤管理
python .claude/skills/tag_manager.py auto
```

---

## 聯絡窗口

所有對外商務溝通請使用：
- **Email**: scott365888@gmail.com
- **微信**: PTS9800

---

## Lark 技能（可用的）
- `lark-doc`: 飛書文檔
- `lark-sheets`: 飛書電子表格
- `lark-calendar`: 飛書日曆
- `lark-im`: 飛書消息
- `lark-task`: 飛書任務
- `lark-mail`: 飛書郵箱

---

## 持續改進

### 已完成
- [x] PDF 導出
- [x] 圖表類型
- [x] Excel 讀取
- [x] 一鍵自動化報告
- [x] 商務工具
- [x] 數據備份
- [x] 決策分析

### 待改進
- [ ] 多語言支援
- [ ] Web 界面
- [ ] 雲端同步
