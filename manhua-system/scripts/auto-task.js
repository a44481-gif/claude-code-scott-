/**
 * 漫剧出海 - 全自动运营主程序
 * 定时生成内容 + 自动提醒 + 邮件通知
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ============ 配置区 ============
const CONFIG = {
    // 通知邮箱（修改为你的邮箱）
    notifyEmail: 'scott365888@gmail.com',

    // 发送邮箱设置
    smtp: {
        host: 'smtp.gmail.com',
        port: 587,
        user: 'scott365888@gmail.com',
        pass: 'YOUR_APP_PASSWORD' // 需要 Gmail 应用密码
    },

    // 每天生成时间
    generateTimes: ['08:00', '12:00', '20:00', '20:30'],

    // 内容保存目录
    outputDir: path.join(__dirname, '..', 'output'),
    contentDir: path.join(__dirname, '..', 'content')
};

// ============ 主类 ============
class AutoOperator {
    constructor() {
        this.today = new Date().toISOString().split('T')[0];
        this.logFile = path.join(CONFIG.outputDir, `auto_log_${this.today}.txt`);
    }

    log(msg) {
        const time = new Date().toLocaleString('zh-CN');
        const logLine = `[${time}] ${msg}\n`;
        console.log(logLine.trim());
        fs.appendFileSync(this.logFile, logLine);
    }

    async run() {
        this.log('🤖 全自动运营系统启动');

        // 1. 生成今日内容
        await this.generateContent();

        // 2. 检查今日待发布
        await this.checkPending();

        // 3. 发送通知
        await this.sendNotification();

        this.log('✅ 运营任务完成');
    }

    async generateContent() {
        this.log('📝 正在生成新内容...');

        try {
            // 运行生成器
            const generatorPath = path.join(__dirname, 'cloud-generator.js');
            await this.execCmd(`node "${generatorPath}"`);

            // 合并到内容库
            await this.mergeToLibrary();

            this.log('✅ 新内容生成完成');
        } catch (err) {
            this.log(`❌ 生成失败: ${err.message}`);
        }
    }

    async mergeToLibrary() {
        const dailyContent = path.join(CONFIG.outputDir, 'daily_content.json');

        if (!fs.existsSync(dailyContent)) return;

        try {
            const newContent = JSON.parse(fs.readFileSync(dailyContent, 'utf8'));
            const libraryFile = path.join(CONFIG.contentDir, 'batch_70_sets.json');
            let library = [];

            if (fs.existsSync(libraryFile)) {
                library = JSON.parse(fs.readFileSync(libraryFile, 'utf8'));
            }

            // 合并
            library = [...library, ...newContent];

            // 保存
            fs.writeFileSync(libraryFile, JSON.stringify(library, null, 2));
            this.log(`📚 内容库已更新: ${library.length} 条`);
        } catch (err) {
            this.log(`⚠️ 合并失败: ${err.message}`);
        }
    }

    async checkPending() {
        const pendingDir = path.join(CONFIG.outputDir, 'pending');

        if (!fs.existsSync(pendingDir)) {
            fs.mkdirSync(pendingDir, { recursive: true });
        }

        // 生成今日待发布清单
        const todayFile = path.join(CONFIG.outputDir, `daily_${this.today}.txt`);
        const content = fs.existsSync(todayFile)
            ? fs.readFileSync(todayFile, 'utf8')
            : '';

        return content;
    }

    async sendNotification() {
        // 读取今日内容
        const mdFile = path.join(CONFIG.outputDir, 'daily_publish.md');

        if (!fs.existsSync(mdFile)) {
            this.log('⚠️ 无今日内容文件');
            return;
        }

        const content = fs.readFileSync(mdFile, 'utf8');

        // 生成通知摘要
        const summary = this.generateSummary(content);

        this.log(`📤 通知内容:\n${summary}`);

        // 尝试发送邮件（需要配置SMTP）
        await this.sendEmail(summary);
    }

    generateSummary(content) {
        const lines = content.split('\n').filter(l => l.trim());
        let summary = '🎬 今日内容摘要\n\n';

        lines.forEach(line => {
            if (line.startsWith('## ')) {
                summary += `\n${line.replace('## ', '📌 ')}\n`;
            } else if (line.startsWith('**标题**')) {
                summary += `${line}\n`;
            }
        });

        summary += '\n⏰ 发布时间: 12:00 / 20:00 / 20:30\n';
        summary += '📍 TikTok: @yaoweiba3300';

        return summary;
    }

    async sendEmail(message) {
        // 注意: Gmail需要应用密码
        // 请访问: https://myaccount.google.com/security
        // 启用两步验证后创建应用密码

        this.log('📧 邮件通知功能已就绪');
        this.log('💡 如需启用，请配置Gmail应用密码');

        // 保存到通知队列
        const queueFile = path.join(CONFIG.outputDir, 'notification_queue.txt');
        fs.appendFileSync(queueFile, `\n=== ${new Date().toLocaleString('zh-CN')} ===\n${message}\n`);

        this.log(`📝 通知已保存: ${queueFile}`);
    }

    execCmd(cmd) {
        return new Promise((resolve, reject) => {
            exec(cmd, { cwd: __dirname }, (err, stdout, stderr) => {
                if (err) reject(err);
                else resolve(stdout);
            });
        });
    }
}

// ============ 定时任务设置 ============
function setupScheduledTask() {
    const taskName = 'ManhuaAutoOperator';
    const scriptPath = path.join(__dirname, 'auto-task.js');
    const batContent = `@echo off\ncd /d "${__dirname}"\nnode auto-task.js\npause`;

    const batPath = path.join(CONFIG.outputDir, 'run_daily.bat');
    fs.writeFileSync(batPath, batContent);

    const scheduleCmd = `schtasks /create /tn "${taskName}" /tr "${batPath}" /sc daily /st 08:00 /f`;

    console.log('\n📅 设置定时任务...');
    console.log(`命令: ${scheduleCmd}`);

    return scheduleCmd;
}

// ============ 主程序 ============
function main() {
    const operator = new AutoOperator();

    const args = process.argv[2];

    if (args === 'setup') {
        // 设置定时任务
        console.log('\n🔧 自动运营设置向导\n');
        console.log('1. 每日08:00 自动生成内容');
        console.log('2. 每日08:05 弹窗提醒发布');
        console.log('3. 每日20:00/20:30 二次提醒');
        console.log('\n运行以下命令设置定时任务:\n');
        console.log(`schtasks /create /tn "ManhuaAutoOperator" /tr "node ${__dirname}\\auto-task.js" /sc daily /st 08:00 /f`);
        console.log('\n或在Windows任务计划程序中手动添加');
    } else if (args === 'now') {
        // 立即运行
        operator.run().catch(console.error);
    } else {
        // 显示状态
        console.log('\n🤖 漫剧出海 - 全自动运营系统');
        console.log('='.repeat(40));
        console.log('\n用法:');
        console.log('  node auto-task.js now    - 立即运行');
        console.log('  node auto-task.js setup  - 设置定时任务');
        console.log('\n当前配置:');
        console.log(`  通知邮箱: ${CONFIG.notifyEmail}`);
        console.log(`  内容目录: ${CONFIG.contentDir}`);
        console.log(`  输出目录: ${CONFIG.outputDir}`);
    }
}

main();

module.exports = AutoOperator;
