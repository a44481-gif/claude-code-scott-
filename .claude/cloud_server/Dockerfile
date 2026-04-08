# 雲端 Agent Server Dockerfile
# 構建: docker build -f .claude/cloud_server/Dockerfile -t ai-agent-cloud .claude/
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製應用代碼（構建上下文為 .claude/）
COPY cloud_server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY cloud_server/src/ ./src/
COPY core/ ./core/

ENV PORT=8000
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["uvicorn", "src.run:app", "--host", "0.0.0.0", "--port", "8000"]
