# CoBM 雲端 AI 自動化系統架構方案

**版本：v1.0 | 日期：2026-04-06**

---

## 一、系統架構總覽

```
┌─────────────────────────────────────────────────────────────────┐
│                        本地客戶端                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │ 任務觸發器   │───▶│ 結果接收器   │◀───│ 本地存儲     │       │
│  │ (腳本/API)  │    │ (Webhook)   │    │ (文件夾)    │       │
│  └──────┬──────┘    └─────────────┘    └─────────────┘       │
│         │ 觸發指令                                               │
└─────────┼───────────────────────────────────────────────────────┘
          │ HTTPS
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        雲端 API Gateway                          │
│              ┌─────────────────────────┐                        │
│              │  Flask / FastAPI 伺服器  │                        │
│              │  (阿里雲函數/騰訊雲SCF)   │                        │
│              └───────────┬─────────────┘                        │
└──────────────────────────┼──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  任務佇列    │   │  AI API     │   │  雲端存儲    │
│  Redis      │   │  Claude     │   │  OSS/S3     │
│  (定時/排程) │   │  Groq       │   │  報告/PPT   │
└─────────────┘   └─────────────┘   └──────┬──────┘
                                           │
                          ┌────────────────┼────────────────┐
                          ▼                ▼                ▼
                   ┌────────────┐   ┌────────────┐   ┌────────────┐
                   │ 報告生成器  │   │ 郵件發送    │   │ 爬蟲引擎   │
                   │ python-pptx│   │ SMTP 163   │   │ 數據采集   │
                   └────────────┘   └────────────┘   └────────────┘
```

---

## 二、核心模組設計

### 2.1 雲端 API 服務 (app.py)

```python
# -*- coding: utf-8 -*-
"""
CoBM 雲端 AI 自動化系統 - 主程式
使用 FastAPI + Redis 佇列 + Claude API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
import uuid
from datetime import datetime

app = FastAPI(title="CoBM Cloud Agent API", version="1.0")

# CORS 允許本地訪問
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 任務模型 ============

class TaskRequest(BaseModel):
    task_type: str  # "report" | "crawl" | "full_pipeline"
    params: dict = {}
    callback_url: Optional[str] = None  # 完成後回撥本地

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

# ============ 任務佇列 (記憶體實現，生產環境用 Redis) ============

tasks_db = {}

@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(req: TaskRequest, background_tasks: BackgroundTasks):
    """創建新任務"""
    task_id = str(uuid.uuid4())

    tasks_db[task_id] = {
        "id": task_id,
        "type": req.task_type,
        "params": req.params,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "result": None
    }

    # 後台執行
    background_tasks.add_task(execute_task, task_id, req)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"任務已創建，任務ID: {task_id}"
    )

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """查詢任務狀態"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任務不存在")

    task = tasks_db[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "created_at": task["created_at"],
        "result": task.get("result")
    }

async def execute_task(task_id: str, req: TaskRequest):
    """執行任務邏輯"""
    try:
        tasks_db[task_id]["status"] = "running"

        if req.task_type == "full_pipeline":
            # 全流程：爬蟲 -> 分析 -> 報告 -> 郵件
            result = await run_full_pipeline(req.params)
        elif req.task_type == "report":
            result = await generate_report(req.params)
        elif req.task_type == "crawl":
            result = await crawl_data(req.params)
        else:
            result = {"error": "未知任務類型"}

        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["result"] = result

        # 回調本地
        if req.callback_url:
            await send_callback(req.callback_url, result)

    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["result"] = {"error": str(e)}

async def run_full_pipeline(params: dict):
    """全流程自動化"""
    # Step 1: 爬蟲數據采集
    crawl_data = await crawl_data(params.get("crawl", {}))

    # Step 2: AI 分析
    analysis = await analyze_data(crawl_data)

    # Step 3: 生成報告
    report_path = await generate_report({
        "type": params.get("report_type", "CoBM分析"),
        "data": analysis
    })

    # Step 4: 發送郵件
    email_result = await send_email_report(report_path)

    return {
        "crawl": crawl_data,
        "analysis": analysis,
        "report": report_path,
        "email": email_result
    }

async def crawl_data(params: dict) -> dict:
    """爬蟲數據采集"""
    # TODO: 實現具體爬蟲邏輯
    return {
        "timestamp": datetime.now().isoformat(),
        "sources": ["GPU數據", "處理器數據", "電源市場數據"],
        "records": []
    }

async def analyze_data(data: dict) -> dict:
    """調用 AI API 分析數據"""
    # TODO: 調用 Claude API
    return {"summary": "分析結果", "insights": []}

async def generate_report(params: dict) -> str:
    """生成 PPT/文檔報告"""
    # TODO: 調用 python-pptx 生成報告
    return "/reports/report_20260406.pptx"

async def send_email_report(report_path: str) -> dict:
    """發送郵件報告"""
    # TODO: SMTP 發送
    return {"status": "sent", "to": "h13751019800@163.com"}

async def send_callback(url: str, result: dict):
    """回調本地系統"""
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post(url, json=result)

# ============ 健康檢查 ============

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {
        "name": "CoBM Cloud Agent API",
        "version": "1.0",
        "endpoints": {
            "create_task": "POST /api/v1/tasks",
            "check_status": "GET /api/v1/tasks/{task_id}",
            "health": "GET /health"
        }
    }
```

### 2.2 本地觸發器 (local_trigger.py)

```python
# -*- coding: utf-8 -*-
"""
本地任務觸發器 - 向雲端發起任務並接收結果
"""

import requests
import time
import json
import os
from datetime import datetime

# 雲端 API 地址（部署後替換）
CLOUD_API_URL = "https://your-cloud-api.example.com"
LOCAL_CALLBACK_PORT = 8080
LOCAL_CALLBACK_URL = f"http://localhost:{LOCAL_CALLBACK_PORT}/callback"

class CloudAgent:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")

    def create_task(self, task_type: str, params: dict = None) -> str:
        """向雲端發起任務"""
        response = requests.post(
            f"{self.api_url}/api/v1/tasks",
            json={
                "task_type": task_type,
                "params": params or {},
                "callback_url": LOCAL_CALLBACK_URL
            }
        )
        response.raise_for_status()
        result = response.json()
        print(f"任務已創建: {result['task_id']}")
        return result["task_id"]

    def wait_for_result(self, task_id: str, poll_interval: int = 5, timeout: int = 600) -> dict:
        """輪詢等待任務完成"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = requests.get(f"{self.api_url}/api/v1/tasks/{task_id}")
            response.raise_for_status()
            status = response.json()

            print(f"任務狀態: {status['status']}")

            if status["status"] == "completed":
                return status["result"]
            elif status["status"] == "failed":
                raise Exception(f"任務失敗: {status['result']}")

            time.sleep(poll_interval)

        raise TimeoutError("任務執行超時")

    def run_full_pipeline(self, params: dict = None) -> dict:
        """一鍵運行全流程"""
        print("=" * 50)
        print("開始向雲端提交全流程任務...")
        print("=" * 50)

        # 1. 創建任務
        task_id = self.create_task("full_pipeline", params or {})

        # 2. 等待結果
        print("等待雲端處理中...")
        result = self.wait_for_result(task_id)

        # 3. 保存結果到本地
        self.save_result(result)

        print("=" * 50)
        print("全流程完成！")
        print("=" * 50)

        return result

    def save_result(self, result: dict):
        """保存結果到本地文件"""
        output_dir = r"D:\claude mini max 2.7\.claude\cloud_results"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(output_dir, f"result_{timestamp}.json")
        report_file = os.path.join(output_dir, f"report_{timestamp}.pptx")

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"結果已保存: {result_file}")
        if result.get("report"):
            print(f"報告已生成: {result.get('report')}")

# ============ 使用示例 ============

if __name__ == "__main__":
    agent = CloudAgent(CLOUD_API_URL)

    # 觸發全流程
    result = agent.run_full_pipeline({
        "report_type": "CoBM分析",
        "crawl": {
            "gpu_data": True,
            "psu_market": True
        }
    })

    print("\n最終結果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 2.3 定時任務調度器 (scheduler.py)

```python
# -*- coding: utf-8 -*-
"""
雲端定時任務調度器 - 自動化報告生成
"""

import schedule
import time
import requests
import json
from datetime import datetime

CLOUD_API_URL = "https://your-cloud-api.example.com"

def job_daily_report():
    """每日報告任務"""
    print(f"[{datetime.now()}] 觸發每日報告任務...")

    try:
        response = requests.post(
            f"{CLOUD_API_URL}/api/v1/tasks",
            json={
                "task_type": "full_pipeline",
                "params": {
                    "report_type": "每日CoBM分析",
                    "crawl": {"gpu_data": True, "psu_market": True}
                }
            }
        )
        result = response.json()
        print(f"任務已提交: {result['task_id']}")
    except Exception as e:
        print(f"任務提交失敗: {e}")

def job_weekly_report():
    """每週報告任務"""
    print(f"[{datetime.now()}] 觸發每週報告任務...")

    try:
        response = requests.post(
            f"{CLOUD_API_URL}/api/v1/tasks",
            json={
                "task_type": "full_pipeline",
                "params": {
                    "report_type": "每週CoBM深度分析",
                    "deep_analysis": True
                }
            }
        )
        result = response.json()
        print(f"任務已提交: {result['task_id']}")
    except Exception as e:
        print(f"任務提交失敗: {e}")

def run_scheduler():
    """運行調度器"""
    # 每天早上 9:00 自動生成報告
    schedule.every().day.at("09:00").do(job_daily_report)

    # 每週一早上 9:30 生成週報
    schedule.every().monday.at("09:30").do(job_weekly_report)

    # 每小時爬取一次市場數據
    schedule.every().hour.do(lambda: requests.post(
        f"{CLOUD_API_URL}/api/v1/tasks",
        json={"task_type": "crawl", "params": {"market_data": True}}
    ))

    print("調度器已啟動...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
```

---

## 三、部署方案

### 3.1 方案一：阿里雲函數計算 (SCF) - 推薦

```yaml
# serverless.yml (騰訊雲無伺服器函數配置)
component: serverless
name: cobm-cloud-agent
inputs:
  name: cobm-cloud-agent
  code: ./
  handler: index.main
  runtime: Python3.9
  region: ap-guangzhou
  memorySize: 512
  timeout: 300
  environment:
    variables:
      CLAUDE_API_KEY: your-claude-api-key
      SMTP_AUTH_CODE: your-smtp-auth-code
      CLOUD_STORAGE_BUCKET: cobm-reports
  triggers:
    - type: timer
      parameters:
        cronExpression: "0 9 * * *"
        enable: true
        argument: daily_report
    - type: http
      parameters:
        methods:
          - GET
          - POST
        name: http_trigger
```

### 3.2 方案二：Docker + VPS 部署

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 複製應用代碼
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  cloud-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - SMTP_AUTH_CODE=${SMTP_AUTH_CODE}
    restart: always
    volumes:
      - ./reports:/app/reports

  redis:
    image: redis:alpine
    restart: always

  scheduler:
    build: .
    command: python scheduler.py
    environment:
      - CLOUD_API_URL=http://cloud-agent:8000
    depends_on:
      - cloud-agent
```

### 3.3 requirements.txt

```
fastapi>=0.100.0
uvicorn>=0.23.0
httpx>=0.24.0
python-pptx>=0.6.21
requests>=2.31.0
schedule>=1.2.0
redis>=4.5.0
python-multipart>=0.0.6
apscheduler>=3.10.0
```

---

## 四、工作流程時序圖

```
本地觸發                              雲端                            外部服務
   │                                 │                               │
   │──── POST /api/v1/tasks ───────▶│                               │
   │◀─── task_id ───────────────────│                               │
   │                                 │                               │
   │                                 │  爬蟲模組                      │
   │                                 │────▶ 爬取 GPU/電源市場數據    │
   │                                 │◀─── raw_data ────────────────│
   │                                 │                               │
   │                                 │  AI 分析                      │
   │                                 │────▶ Claude API ─────────────▶│
   │                                 │◀─── analysis_result ─────────│
   │                                 │                               │
   │                                 │  報告生成                      │
   │                                 │────▶ python-pptx ────────────▶│
   │                                 │◀─── report.pptx ─────────────│
   │                                 │                               │
   │                                 │  郵件發送                     │
   │                                 │────▶ SMTP 163 ──────────────▶│
   │                                 │◀─── sent ─────────────────────│
   │                                 │                               │
   │◀─── result + report ───────────│                               │
   │                                 │                               │
```

---

## 五、安全配置

### 5.1 API 認證

```python
# 加入 API Key 認證
from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.environ.get("API_SECRET_KEY"):
        raise HTTPException(status_code=403, detail="無效的 API Key")
    return api_key

@app.post("/api/v1/tasks", dependencies=[Depends(verify_api_key)])
async def create_task(req: TaskRequest, background_tasks: BackgroundTasks):
    ...
```

### 5.2 環境變量管理

```bash
# .env 文件（不上傳 Git）
CLAUDE_API_KEY=sk-xxxxx
SMTP_AUTH_CODE=JWxaQXzrCQCWtPu3
API_SECRET_KEY=your-random-secret-key
CLOUD_STORAGE_BUCKET=cobm-reports
```

---

## 六、部署檢查清單

| 步驟 | 操作 | 狀態 |
|-----|------|------|
| 1 | 購買雲伺服器/VPS 或開通函數計算 | ☐ |
| 2 | 安裝 Docker 或配置 Python 環境 | ☐ |
| 3 | 配置環境變量 (API Key/SMTP) | ☐ |
| 4 | 部署 cloud-agent API 服務 | ☐ |
| 5 | 配置域名和 HTTPS | ☐ |
| 6 | 測試 API 端點 | ☐ |
| 7 | 配置定時任務調度 | ☐ |
| 8 | 配置本地觸發腳本 | ☐ |
| 9 | 測試完整流程 | ☐ |
| 10 | 配置監控和告警 | ☐ |

---

## 七、成本估算

| 方案 | 月費 (USD) | 適用場景 |
|------|-----------|---------|
| 阿里雲函數計算 | $5-20 | 輕量級，按需調用 |
| 騰訊雲 SCF | $5-15 | 輕量級，國內訪問快 |
| 騰訊雲 CVM 2核4G | $20-30 | 中等負載，常駐服務 |
| AWS Lambda | $10-30 | 企業級，全球分佈 |
| VPS (DigitalOcean) | $6-24 | 預算有限 |
| VPS (阿里雲/騰訊雲) | $15-40 | 穩定性要求高 |

**推薦方案：騰訊雲 SCF（函數計算）或 騰訊雲 CVM**

---

## 八、下一步行動

1. **確認部署平台**：阿里雲/騰訊雲/AWS/VPS？
2. **準備 API Key**：Claude API Key 已經有了嗎？
3. **配置 SMTP**：確認 163.com SMTP 配置
4. **選擇監控方案**：需要日誌/告警嗎？

確認後我可以幫您寫完整的部署腳本，一鍵部署到雲端。
