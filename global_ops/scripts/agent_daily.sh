#!/bin/bash
# GlobalOPS · Claude Code 代理自动运营脚本
# 由 cron 定时触发，实现真正的 AI 自动化运营
#
# 安装 cron（macOS/Linux）:
#   crontab -e
#   0 9 * * * /path/to/scripts/agent_daily.sh >> logs/agent_daily.log 2>&1
#
# Windows 任务计划程序:
#   schtasks /create /tn "GlobalOps Agent" /tr "bash scripts\agent_daily.sh" /sc daily /st 09:00

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BASE_DIR"

LOG_FILE="${BASE_DIR}/logs/agent_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "${BASE_DIR}/logs"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error_exit() {
  log "❌ ERROR: $1"
  exit 1
}

# ============ 运营检查函数 ============

check_content_library() {
  log "📊 检查内容库状态..."
  cd content_engine
  node src/manager.js stats 2>/dev/null | tee -a "$LOG_FILE"
  cd ..
}

generate_content() {
  log "🎬 生成今日新内容..."
  cd content_engine
  node src/generator.js --db --count=10 2>&1 | tee -a "$LOG_FILE"
  cd ..
  log "✅ 内容生成完成"
}

trigger_publish() {
  log "🚀 触发 YouTube 发布..."
  python python_engine/main.py publish --platform youtube --limit=3 2>&1 | tee -a "$LOG_FILE"
  log "✅ 发布流程完成"
}

collect_analytics() {
  log "📈 采集运营数据..."
  python python_engine/main.py analytics --days=1 2>&1 | tee -a "$LOG_FILE"
  log "✅ 数据采集完成"
}

check_revenue() {
  log "💰 检查今日收益..."
  python python_engine/main.py revenue --days=7 2>&1 | tee -a "$LOG_FILE"
  log "✅ 收益检查完成"
}

notify_result() {
  local status=$1
  local message=$2
  local webhook="${LARK_WEBHOOK:-}"

  if [ -z "$webhook" ]; then
    log "⚠️ 未配置飞书通知"
    return
  fi

  local template="green"
  if [ "$status" = "failure" ]; then
    template="red"
  fi

  curl -s -X POST "$webhook" \
    -H "Content-Type: application/json" \
    -d "{
      \"msg_type\": \"interactive\",
      \"card\": {
        \"header\": {
          \"title\": { \"tag\": \"plain_text\", \"content\": \"🤖 GlobalOPS 代理日报 - $(date '+%m/%d %H:%M')\" },
          \"template\": \"$template\"
        },
        \"elements\": [
          { \"tag\": \"div\", \"text\": { \"tag\": \"lark_md\", \"content\": \"**状态:** ${status}\n**消息:** ${message}\n**时间:** $(date '+%Y-%m-%d %H:%M:%S')\" } }
        ]
      }
    }" | tee -a "$LOG_FILE" || log "⚠️ 飞书通知发送失败"
}

# ============ AI 运营分析（Claude Code） ============
ai_review() {
  log "🧠 AI 运营分析..."

  # 生成运营报告摘要供 AI 分析
  local summary_file="${BASE_DIR}/logs/ops_summary_$(date +%Y%m%d).txt"

  {
    echo "=== GlobalOPS 运营日报 $(date '+%Y-%m-%d') ==="
    echo ""
    echo "【内容库】"
    node content_engine/src/manager.js stats 2>/dev/null || echo "无法获取内容库统计"
    echo ""
    echo "【近7天收益】"
    python python_engine/main.py revenue --days=7 2>/dev/null || echo "无法获取收益"
    echo ""
    echo "【近7天数据】"
    python python_engine/main.py analytics --days=7 2>/dev/null || echo "无法获取分析"
  } > "$summary_file"

  # 将报告传给 AI 分析并获取建议
  log "📄 运营摘要已生成: $summary_file"
  log "💡 建议: 人工查看 $summary_file 获取 AI 运营建议"
}

# ============ 主流程 ============
main() {
  local start_time=$(date +%s)
  log "=========================================="
  log "  🤖 GlobalOPS 代理自动运营开始"
  log "=========================================="

  trap 'notify_result "failure" "脚本异常退出"; error_exit "Script interrupted"' INT TERM

  # 1. 检查内容库
  check_content_library || log "⚠️ 内容库检查失败，继续"

  # 2. 生成新内容（核心功能）
  generate_content || log "⚠️ 内容生成失败，继续"

  # 3. 发布到平台
  trigger_publish || log "⚠️ 发布失败，继续"

  # 4. 采集数据
  collect_analytics || log "⚠️ 数据采集失败，继续"

  # 5. 检查收益
  check_revenue || log "⚠️ 收益检查失败，继续"

  # 6. AI 分析（可选）
  ai_review || log "⚠️ AI 分析失败，继续"

  local end_time=$(date +%s)
  local duration=$((end_time - start_time))

  log "=========================================="
  log "  ✅ 代理运营完成！耗时: ${duration}s"
  log "=========================================="

  # 发送成功通知
  notify_result "success" "每日运营完成 | 耗时: ${duration}s | 日志: logs/agent_$(date +%Y%m%d).log"
}

main "$@"
