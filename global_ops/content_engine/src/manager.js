/**
 * GlobalOPS · 内容管理器
 * 用法: node manager.js stats | list | schedule | reminder
 */

require('dotenv').config({ path: require('path').join(__dirname, '../../config/.env') });
const { Client } = require('pg');

function getDbClient() {
  return new Client({
    host: process.env.POSTGRES_HOST || 'localhost',
    port: process.env.POSTGRES_PORT || 5432,
    database: process.env.POSTGRES_DB || 'global_ops',
    user: process.env.POSTGRES_USER || 'postgres',
    password: process.env.POSTGRES_PASSWORD || '',
  });
}

async function cmdStats() {
  const client = getDbClient();
  await client.connect();

  // 按状态统计
  const { rows: statusRows } = await client.query(`
    SELECT status, COUNT(*) as count FROM content_items GROUP BY status
  `);
  const { rows: themeRows } = await client.query(`
    SELECT theme_type, COUNT(*) as count FROM content_items GROUP BY theme_type ORDER BY count DESC
  `);
  const { rows: regionRows } = await client.query(`
    SELECT target_region, COUNT(*) as count FROM content_items GROUP BY target_region
  `);
  const { rows: publishRows } = await client.query(`
    SELECT platform, COUNT(*) as count, SUM(views_total) as total_views
    FROM publish_log GROUP BY platform ORDER BY count DESC
  `);
  const { rows: revenueRows } = await client.query(`
    SELECT SUM(gross_revenue) as total FROM daily_revenue
    WHERE date >= CURRENT_DATE - INTERVAL '30 days'
  `);

  await client.end();

  console.log('\n📊 GlobalOPS 内容库统计\n');
  console.log('【内容状态】');
  statusRows.forEach(r => console.log(`   ${r.status}: ${r.count}`));
  console.log('\n【题材分布】');
  themeRows.forEach(r => console.log(`   ${r.theme_type}: ${r.count}`));
  console.log('\n【地区分布】');
  regionRows.forEach(r => console.log(`   ${r.target_region}: ${r.count}`));
  console.log('\n【发布记录】');
  publishRows.forEach(r => console.log(`   ${r.platform}: ${r.count}条 | 总播放 ${Number(r.total_views || 0).toLocaleString()}`));
  const totalRev = revenueRows[0]?.total || 0;
  console.log(`\n【月收益】 $${Number(totalRev).toFixed(2)}`);
}

async function cmdList() {
  const client = getDbClient();
  await client.connect();
  const { rows } = await client.query(`
    SELECT content_id, theme_type, topic, status, target_lang, created_at
    FROM content_items ORDER BY created_at DESC LIMIT 20
  `);
  await client.end();
  console.log('\n📋 最近20条内容:\n');
  rows.forEach(r => {
    console.log(`  [${r.status}] ${r.content_id} | ${r.theme_type} | ${r.topic.slice(0, 30)}... | ${r.target_lang} | ${r.created_at.toISOString().slice(0, 10)}`);
  });
}

async function cmdSchedule() {
  const client = getDbClient();
  await client.connect();
  const { rows } = await client.query(`
    SELECT content_id, theme_type, topic, status, best_post_time
    FROM content_items
    WHERE status IN ('generated', 'pending')
    ORDER BY priority DESC, created_at ASC LIMIT 14
  `);
  await client.end();

  console.log('\n📅 未来7天发布排期（每天2条）:\n');
  const days = ['周一','周二','周三','周四','周五','周六','周日'];
  const now = new Date();
  for (let i = 0; i < 7; i++) {
    const d = new Date(now);
    d.setDate(d.getDate() + i);
    const dayName = days[d.getDay() === 0 ? 6 : d.getDay() - 1];
    const dateStr = d.toISOString().slice(0, 10);
    const am = rows[i * 2];
    const pm = rows[i * 2 + 1];
    console.log(`  ${dateStr} (${dayName})`);
    if (am) console.log(`    🌅 ${am.content_id} | ${am.theme_type} | ${am.best_post_time}`);
    if (pm) console.log(`    🌙 ${pm?.content_id || '-'} | ${pm?.theme_type || '-'} | ${pm?.best_post_time || '-'}`);
    console.log();
  }
}

async function cmdPending() {
  const client = getDbClient();
  await client.connect();
  const { rows } = await client.query(`
    SELECT content_id, theme_type, topic, priority, best_post_time
    FROM content_items WHERE status = 'pending' ORDER BY priority DESC LIMIT 10
  `);
  await client.end();
  console.log('\n⏳ 待处理内容（Top 10）:\n');
  rows.forEach(r => {
    console.log(`  P${r.priority} | ${r.content_id} | ${r.theme_type} | ${r.best_post_time}`);
  });
}

async function main() {
  const cmd = process.argv[2] || 'stats';
  switch (cmd) {
    case 'stats': await cmdStats(); break;
    case 'list': await cmdList(); break;
    case 'schedule': await cmdSchedule(); break;
    case 'pending': await cmdPending(); break;
    default: console.log('用法: node manager.js stats | list | schedule | pending');
  }
}

main().catch(console.error);
