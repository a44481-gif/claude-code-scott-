# 技能系統 - 完整文檔
更新時間: 2026-04-07

## 統一啟動器

現在使用 `skill.py` 一個命令啟動所有技能：

```bash
python .claude/skills/skill.py <skill-id> [args...]

# 範例
python .claude/skills/skill.py ppt-analyze report.pptx
python .claude/skills/skill.py auto-report data.xlsx --all
python .claude/skills/skill.py skill-opt stats
```

---

## 技能清單 (23個)

### PPT/資料處理 (7個)
| 快捷命令 | 腳本 | 功能 |
|----------|------|------|
| `ppt-analyze` | ppt_analyzer.py | PPT 內容分析 |
| `ppt-gen` | ppt_generator_v3.py | 生成 PPT 報告 |
| `data-analyze` | data_analyzer.py | 分析市場數據、CAGR |
| `excel-read` | excel_reader.py | 讀取 Excel/CSV |
| `chart` | chart_generator.py | 生成圖表 |
| `pdf` | pdf_generator.py | 生成 PDF 報告 |
| `auto-report` | auto_report.py | 一鍵自動化報告 |

### 商務工具 (6個)
| 快捷命令 | 腳本 | 功能 |
|----------|------|------|
| `market` | market_research.py | 市場研究、行業分析 |
| `customer` | customer_manager.py | 客戶管理 CRM |
| `business-plan` | business_plan_generator.py | 商業計劃書 |
| `meeting` | meeting_manager.py | 會議管理 |
| `decision` | decision_analyzer.py | 決策分析、SWOT |
| `translate` | translation_tool.py | 中英翻譯、術語 |

### 系統工具 (8個)
| 快捷命令 | 腳本 | 功能 |
|----------|------|------|
| `backup` | data_backup.py | 數據備份 |
| `tag` | tag_manager.py | 文件標籤 |
| `batch` | batch_process.py | 批次處理 |
| `skill-hub` | agent_skill_hub.py | 技能共享中心 |
| `skill-opt` | skill_optimizer.py | 技能優化追蹤 |
| - | skill.py | **統一啟動器** |
| - | ppt_extractor.py | PPT 內容提取 |
| - | ppt_generator.py | PPT 生成 v1 |
| - | ppt_generator_v2.py | PPT 生成 v2 |

---

## Lark 技能（可用的）

| 技能 | 功能 |
|------|------|
| `lark-doc` | 飛書雲文檔 |
| `lark-sheets` | 飛書電子表格 |
| `lark-calendar` | 飛書日曆 |
| `lark-im` | 飛書即時通訊 |
| `lark-mail` | 飛書郵箱 |
| `lark-task` | 飛書任務 |
| `lark-wiki` | 飛書知識庫 |
| `lark-contact` | 飛書通訊錄 |
| `lark-vc` | 飛書視頻會議 |

---

## 對外聯絡窗口

- **Email**: scott365888@gmail.com
- **微信**: PTS9800

---

## 持續改進

### 已完成
- [x] 統一啟動器
- [x] 23 個技能腳本
- [x] 一鍵自動化報告
- [x] 商務工具
- [x] 決策分析

### 待改進
- [ ] 雲端同步
- [ ] Web 界面
- [ ] 使用統計追蹤
