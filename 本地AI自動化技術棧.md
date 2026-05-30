---
title: 本地 AI 自動化技術棧
date: 2026-05-30
tags: [AI, 自動化, 技術架構, Obsidian, n8n, Ollama]
category: 30_研究
status: complete
---

# 本地 AI 自動化：技術棧、架構與部署指南

> 本文件系統性地梳理了在 Windows 本地環境構建 AI 自動化生態的完整方案，涵蓋工具選型、架構設計、部署步驟與運維策略。

---

## 1. 技術棧總覽

### 1.1 核心組件

| 層級 | 工具 | 版本/規格 | 用途 |
|------|------|-----------|------|
| **工作流引擎** | n8n | latest (Docker) | 可視化自動化編排，Cron 觸發，API 串接 |
| **本地 LLM** | Ollama | latest | 本地大模型推理，qwen2.5:7b |
| **知識管理** | Obsidian | v1.x | Markdown 知識庫，雙向連結 |
| **版本備份** | Git + GitHub | git 2.54+ | 文檔版本控制，自動化推送 |
| **AI Agent** | WorkBuddy | 4.24.2 | MCP 協議整合，多模型調度 |
| **通知推送** | 飛書/Lark CLI | lark-cli | 任務完成通知，即時消息 |

### 1.2 基礎設施

| 組件 | 技術 | 說明 |
|------|------|------|
| 容器運行時 | Docker Desktop | WSL2 後端，n8n 容器化部署 |
| 包管理 | npm / npx | Node.js 22.x，MCP Server 安裝 |
| Python 環境 | Python 3.13 + venv | 腳本執行，論文抓取 |
| 通訊協議 | MCP (Model Context Protocol) | AI Agent 與外部工具的標準化接口 |

---

## 2. 系統架構

### 2.1 整體架構圖

```
┌─────────────────────────────────────────────────────────┐
│                    WorkBuddy (AI Agent)                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│   │ Obsidian │  │ GitHub   │  │ n8n-MCP              │  │
│   │ MCP      │  │ MCP      │  │ (工作流創建/管理)     │  │
│   └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │
│        │              │                    │              │
└────────┼──────────────┼────────────────────┼──────────────┘
         │              │                    │
    ┌────▼────┐    ┌─────▼─────┐       ┌─────▼─────┐
    │  C:\    │    │ GitHub    │       │ n8n       │
    │ obsidian│   │ API       │       │ :5678     │
    │ (Vault) │    │ Contents  │       │           │
    └─────────┘    └───────────┘       └─────┬─────┘
                                          │
                                    ┌─────▼─────┐
                                    │ Cron 觸發  │
                                    │ HTTP 請求  │
                                    │ Code 執行  │
                                    └─────┬─────┘
                                          │
                              ┌───────────┼───────────┐
                              │           │           │
                        ┌─────▼───┐ ┌─────▼───┐ ┌────▼────┐
                        │ Ollama  │ │ GitHub  │ │ 飛書    │
                        │ :11434  │ │ Push    │ │ 通知    │
                        │ qwen2.5 │ │         │ │         │
                        └─────────┘ └─────────┘ └─────────┘
```

### 2.2 數據流

```
[觸發源] → [n8n 工作流] → [處理節點] → [輸出目標]

定時 Cron ──→ 掃描 Obsidian ──→ 比對 .backup_state.json ──→ GitHub API Push
手動 Webhook → 接收數據   ──→ LLM 摘要(Ollama)     ──→ 保存 .md
Claude API  ──→ 生成內容   ──→ 格式化 Markdown      ──→ Obsidian Vault
```

### 2.3 MCP 服務架構

```
WorkBuddy MCP Config (mcp.json)
├── obsidian-mcp     → npx mcp-obsidian C:\obsidian
├── github-mcp       → npx @modelcontextprotocol/server-github
├── n8n-mcp          → npx n8n-mcp (N8N_API_URL=http://localhost:5678)
├── connector:qq-mail  → QQ 郵箱 MCP (disabled)
└── connector:notion   → Notion MCP (disabled)
```

---

## 3. 部署步驟

### 3.1 Docker 環境準備

```powershell
# 1. 啟動 Docker Desktop（手動雙擊圖標）

# 2. 創建必要目錄
New-Item -ItemType Directory -Force -Path "D:\待處理文件"
New-Item -ItemType Directory -Force -Path "D:\已處理總結"

# 3. 部署 n8n
cd C:\Users\輝\n8n-docker
docker compose up -d

# 4. 驗證
curl http://localhost:5678/healthz
```

### 3.2 n8n 初始配置

1. 瀏覽器訪問 http://localhost:5678
2. 註冊管理員帳號
3. 生成 API Key：Settings → n8n API → API Keys → Create
4. 將 API Key 填入：
   - `C:\Users\輝\n8n-docker\.env` → `N8N_API_KEY=你的Key`
   - `mcp.json` → `n8n-mcp.env.N8N_API_KEY`

### 3.3 Ollama 本地模型

```powershell
# 安裝 Ollama
winget install Ollama.Ollama

# 拉取中文模型
ollama pull qwen2.5:7b

# 驗證
curl http://localhost:11434/api/tags
```

### 3.4 MCP 服務串接

在 WorkBuddy 設定中啟用已配置的 MCP 服務：
- `obsidian-mcp` — 讀取/搜索 Obsidian 筆記
- `github-mcp` — 操作 GitHub 倉庫（需 PAT）
- `n8n-mcp` — 創建/管理 n8n 工作流

### 3.5 GitHub 倉庫初始化

```powershell
cd C:\obsidian

# 初始化 Git 倉庫
git init
git config user.name "你的用戶名"
git config user.email "你的郵箱"

# 創建 .gitignore
@"
.obsidian/
.claude/
.claude-workspace/
.cludian/
.backup_state.json
"@ | Out-File -Encoding utf8 .gitignore

# 首次提交
git add .
git commit -m "init: Obsidian vault 初始備份"

# 添加遠程倉庫
git remote add origin https://github.com/你的用戶名/你的倉庫.git
git push -u origin main
```

---

## 4. 自動化工作流清單

| # | 工作流 | 觸發方式 | 核心邏輯 |
|---|--------|----------|----------|
| 01 | 每日 AI 新聞 | Cron 9:00 | Claude API → 摘要 → Webhook |
| 02 | 用戶註冊處理 | Webhook | 郵箱驗證 → Google Sheets |
| 03 | AI 獲客助手 | Webhook | Claude ×2 → Gmail → Sheets |
| 04 | 文件摘要器 | Cron 1min | 掃描 D:\待處理文件 → Ollama → .md |
| 05 | Ollama 測試 | Cron 1min | HTTP POST → Code 解析 |
| 06 | Obsidian-Git 備份 | Cron 2:00 | 掃描 Vault → GitHub API Push |

---

## 5. 運維指南

### 5.1 日常操作

```powershell
# 查看容器狀態
docker compose -f C:\Users\輝\n8n-docker\docker-compose.yml ps

# 查看日誌
docker compose -f C:\Users\輝\n8n-docker\docker-compose.yml logs -f n8n

# 重啟服務
docker compose -f C:\Users\輝\n8n-docker\docker-compose.yml restart

# 更新鏡像
docker compose -f C:\Users\輝\n8n-docker\docker-compose.yml pull
docker compose -f C:\Users\輝\n8n-docker\docker-compose.yml up -d
```

### 5.2 備份策略

- **Obsidian Vault**：Git 自動備份至 GitHub（每日 2:00）
- **n8n 工作流**：`n8n_data` 命名卷持久化 + GitHub 備份
- **.backup_state.json**：追蹤每個檔案的最後備份 SHA，避免重複推送

### 5.3 故障排查

| 問題 | 排查方法 |
|------|----------|
| n8n 無法啟動 | `docker compose logs n8n` 查看錯誤 |
| Ollama 超時 | 確認 `http://localhost:11434` 可達 |
| GitHub Push 失敗 | 檢查 PAT 是否過期、倉庫權限 |
| MCP 連接失敗 | 確認 npx 路徑、API Key 正確 |

---

## 6. 技術決策記錄

| 決策 | 選擇 | 原因 |
|------|------|------|
| 工作流引擎 | n8n | 開源、可視化、社區活躍、Docker 友好 |
| 本地 LLM | Ollama + qwen2.5:7b | 中文能力強、CPU 可跑、隱私安全 |
| Git 推送方式 | GitHub Contents API | 不需容器內裝 git，更輕量安全 |
| MCP n8n 連接 | npx 模式 | 不依賴 Docker Desktop，直接本地連接 |
| 通知渠道 | 飛書 Lark CLI | 已認證，支持消息、文檔、日曆等 |
| 知識管理 | Obsidian | Markdown 原生、雙向連結、插件生態 |

---

*文檔生成時間：2026-05-30 13:50 CST*
*生成方式：WorkBuddy AI Agent 自動生成*
*存放位置：C:\obsidian\30_研究\本地AI自動化技術棧.md*
