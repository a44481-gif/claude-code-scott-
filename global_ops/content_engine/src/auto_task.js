/**
 * GlobalOPS · 自动运营主程序
 * 定时生成 + 发布调度 + 通知
 */

require('dotenv').config({ path: require('path').join(__dirname, '../../config/.env') });
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const LOG_DIR = path.join(__dirname, '../../logs');
fs.mkdirSync(LOG_DIR, { recursive: true });
const logFile = path.join(LOG_DIR, `auto_task_${new Date().toISOString().slice(0, 10)}.log`);

function log(msg) {
  const ts = new Date().toISOString();
  const line = `${ts} [AUTO] ${msg}`;
  console.log(line);
  fs.appendFileSync(logFile, line + '\n');
}

function runCommand(cmd, args) {
  return new Promise((resolve, reject) => {
    log(`运行: ${cmd} ${args.join(' ')}`);
    const proc = spawn(cmd, args, { shell: true });
    let stdout = '', stderr = '';
    proc.stdout.on('data', d => stdout += d);
    proc.stderr.on('data', d => stderr += d);
    proc.on('close', code => {
      if (code === 0) {
        log(`✅ 完成: ${cmd}`);
        resolve(stdout);
      } else {
        log(`❌ 失败 (code ${code}): ${stderr || stdout}`);
        reject(new Error(stderr || `exit ${code}`));
      }
    });
  });
}

async function dailyContentGeneration() {
  log('=== 开始每日内容生成 ===');
  // 每天生成10条新内容
  await runCommand('node', [
    path.join(__dirname, 'generator.js'),
    '--db', '--count=10'
  ]);
  log('=== 内容生成完成 ===');
}

async function triggerPublish() {
  log('=== 触发 YouTube 发布 ===');
  await runCommand('python', [
    path.join(__dirname, '../../python_engine/main.py'),
    'publish', '--platform', 'youtube', '--limit', '3'
  ]);
  log('=== 发布触发完成 ===');
}

async function analyticsReport() {
  log('=== 生成数据报告 ===');
  await runCommand('python', [
    path.join(__dirname, '../../python_engine/main.py'),
    'analytics', '--days', '7'
  ]);
  log('=== 报告完成 ===');
}

async function notify(message) {
  const webhook = process.env.LARK_WEBHOOK;
  if (!webhook) return;
  try {
    await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ msg_type: 'text', content: { text: `[GlobalOPS] ${message}` } })
    });
    log(`📬 飞书通知已发送`);
  } catch (e) {
    log(`⚠️ 通知发送失败: ${e.message}`);
  }
}

async function main() {
  const mode = process.argv[2] || 'now';
  log(`启动自动运营 [mode=${mode}]`);

  try {
    if (mode === 'now') {
      await dailyContentGeneration();
      await triggerPublish();
      await analyticsReport();
      await notify('✅ 每日运营任务完成');
    } else if (mode === 'generate') {
      await dailyContentGeneration();
    } else if (mode === 'publish') {
      await triggerPublish();
    } else if (mode === 'report') {
      await analyticsReport();
    }
    log('✅ 所有任务完成');
    process.exit(0);
  } catch (e) {
    log(`❌ 任务失败: ${e.message}`);
    await notify(`❌ 运营任务失败: ${e.message}`);
    process.exit(1);
  }
}

main();
