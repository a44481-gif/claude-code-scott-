#!/bin/bash
# GlobalOPS · 数据库迁移脚本
# 用法: ./scripts/migrate_content.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-global_ops}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASS="${POSTGRES_PASSWORD:-}"

echo "🔄 GlobalOPS 数据库迁移"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo ""

export PGPASSWORD="$DB_PASS"

# 等待数据库就绪
echo "⏳ 等待数据库..."
until psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c '\q' 2>/dev/null; do
  sleep 2
done
echo "✅ 数据库已就绪"

# 运行迁移
echo "📄 运行迁移脚本..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$BASE_DIR/database/migrations/001_initial_schema.sql"
echo ""
echo "✅ 迁移完成！"

# 验证表
echo "📋 验证表结构..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;"
