/**
 * 漫剧出海内容管理系统
 * Manhua Content Management System
 *
 * 功能：
 * 1. 内容管理 - 管理60套内容
 * 2. 发布排期 - 自动生成每日发布计划
 * 3. 状态追踪 - 记录发布状态
 * 4. 提醒功能 - 定时提醒发布
 */

const fs = require('fs');
const path = require('path');

// ============ 配置 ============
const CONFIG = {
    contentDir: path.join(__dirname, '../content'),
    outputDir: path.join(__dirname, '../output'),
    dataFile: path.join(__dirname, '../data/publish_log.json'),
    themes: ['龙王', '逆袭', '虐渣', '重生', '神医', '系统'],
    publishTimes: [
        { time: '12:00', label: '午休' },
        { time: '20:00', label: '晚间' },
        { time: '20:30', label: '黄金档' }
    ]
};

// ============ 内容类 ============
class ContentManager {
    constructor() {
        this.contents = [];
        this.schedule = [];
        this.loadContents();
    }

    // 加载内容
    loadContents() {
        try {
            const contentFile = path.join(CONFIG.contentDir, 'batch_60_sets.json');
            if (fs.existsSync(contentFile)) {
                const data = fs.readFileSync(contentFile, 'utf8');
                this.contents = JSON.parse(data);
                console.log(`✅ 已加载 ${this.contents.length} 条内容`);
            } else {
                console.log('⚠️  未找到内容文件，请先生成内容');
            }
        } catch (error) {
            console.error('❌ 加载内容失败:', error.message);
        }
    }

    // 按题材筛选
    filterByTheme(theme) {
        return this.contents.filter(c => c.theme.startsWith(theme));
    }

    // 获取待发布内容
    getPendingContent() {
        return this.contents.filter(c => c.status === 'pending');
    }

    // 获取已发布内容
    getPublishedContent() {
        return this.contents.filter(c => c.status === 'published');
    }

    // 标记已发布
    markAsPublished(contentId) {
        const content = this.contents.find(c => c.id === contentId);
        if (content) {
            content.status = 'published';
            content.publishedAt = new Date().toISOString();
            this.save();
            return true;
        }
        return false;
    }
}

// ============ 排期管理类 ============
class ScheduleManager {
    constructor(contentManager) {
        this.cm = contentManager;
    }

    // 生成发布计划
    generateSchedule(days = 7) {
        const schedule = [];
        const themes = CONFIG.themes;

        for (let day = 0; day < days; day++) {
            const date = new Date();
            date.setDate(date.getDate() + day);

            const daySchedule = {
                date: date.toISOString().split('T')[0],
                dayName: this.getDayName(date.getDay()),
                items: []
            };

            // 每天3条
            for (let slot = 0; slot < 3; slot++) {
                const theme = themes[(day * 3 + slot) % themes.length];
                const pending = this.cm.filterByTheme(theme).find(c => c.status === 'pending');

                if (pending) {
                    daySchedule.items.push({
                        slot: slot,
                        time: CONFIG.publishTimes[slot].time,
                        theme: theme,
                        content: pending,
                        status: 'pending'
                    });
                }
            }

            schedule.push(daySchedule);
        }

        return schedule;
    }

    // 获取星期名称
    getDayName(day) {
        const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        return days[day];
    }

    // 获取今日待发布
    getTodaySchedule() {
        const today = new Date().toISOString().split('T')[0];
        const schedule = this.generateSchedule();
        return schedule.find(s => s.date === today);
    }

    // 导出排期表
    exportSchedule(schedule) {
        let md = `# 📅 发布排期表\n\n`;
        md += `生成时间：${new Date().toLocaleString('zh-CN')}\n\n`;

        schedule.forEach(day => {
            md += `## ${day.dayName} (${day.date})\n\n`;

            if (day.items.length === 0) {
                md += `>暂无待发布内容\n\n`;
            } else {
                day.items.forEach((item, index) => {
                    md += `### ${index + 1}. ${item.time} - ${item.theme}\n\n`;
                    md += `- **标题**: ${item.content.title}\n`;
                    md += `- **主题**: ${item.content.theme}\n`;
                    md += `- **标签**: ${item.content.tags}\n`;
                    md += `- **发布时间**: ${item.time}\n`;
                    md += `- **状态**: ${item.status}\n\n`;
                });
            }
        });

        return md;
    }
}

// ============ 提醒系统 ============
class ReminderSystem {
    constructor() {
        this.reminders = [];
    }

    // 生成Windows提醒脚本
    generateReminderScript(schedule) {
        let content = `@echo off\n`;
        content += `chcp 65001 >nul\n`;
        content += `echo ========================================\n`;
        content += `echo    漫剧出海 - 发布提醒\n`;
        content += `echo ========================================\n`;
        content += `echo.\n\n`;

        schedule.forEach(day => {
            content += `echo [${day.dayName} ${day.date}]\n`;
            day.items.forEach(item => {
                content += `echo --------------------------------\n`;
                content += `echo   ${item.time} - ${item.theme}\n`;
                content += `echo   ${item.content.title}\n`;
                content += `echo.\n`;
            });
        });

        content += `\necho ========================================\n`;
        content += `echo 按任意键退出...\n`;
        content += `pause >nul\n`;

        return content;
    }

    // 生成任务计划程序命令
    generateTaskCommands(schedule) {
        const commands = [];

        schedule.forEach(day => {
            day.items.forEach(item => {
                const [hour, minute] = item.time.split(':');
                const dateStr = day.date.replace(/-/g, '');

                // schtasks 命令
                const cmd = `schtasks /create /tn "漫剧发布_${day.date}_${item.time.replace(':', '')}" ` +
                           `/tr "cmd /c start https://www.tiktok.com/@yaoweiba3300" ` +
                           `/sc daily /st ${hour}:${minute} /d ${dateStr.slice(-2)} /f`;

                commands.push({
                    date: day.date,
                    time: item.time,
                    theme: item.theme,
                    title: item.content.title,
                    command: cmd
                });
            });
        });

        return commands;
    }
}

// ============ 统计系统 ============
class Statistics {
    constructor(contentManager) {
        this.cm = contentManager;
    }

    // 获取统计数据
    getStats() {
        const total = this.cm.contents.length;
        const published = this.cm.getPublishedContent().length;
        const pending = this.getPendingCount();

        return {
            total,
            published,
            pending,
            publishedRate: total > 0 ? ((published / total) * 100).toFixed(1) + '%' : '0%',
            byTheme: this.getStatsByTheme()
        };
    }

    // 按题材统计
    getStatsByTheme() {
        const stats = {};
        CONFIG.themes.forEach(theme => {
            const all = this.cm.contents.filter(c => c.theme.startsWith(theme));
            const published = all.filter(c => c.status === 'published').length;
            stats[theme] = { total: all.length, published, pending: all.length - published };
        });
        return stats;
    }

    // 待发布数量
    getPendingCount() {
        return this.cm.getPendingContent().length;
    }

    // 生成统计报告
    generateReport() {
        const stats = this.getStats();

        let md = `# 📊 发布统计报告\n\n`;
        md += `生成时间：${new Date().toLocaleString('zh-CN')}\n\n`;

        md += `## 总体概览\n\n`;
        md += `| 指标 | 数值 |\n`;
        md += `|------|------|\n`;
        md += `| 总内容 | ${stats.total} |\n`;
        md += `| 已发布 | ${stats.published} |\n`;
        md += `| 待发布 | ${stats.pending} |\n`;
        md += `| 发布率 | ${stats.publishedRate} |\n\n`;

        md += `## 题材分布\n\n`;
        md += `| 题材 | 总数 | 已发布 | 待发布 |\n`;
        md += `|------|------|--------|--------|\n`;

        for (const [theme, data] of Object.entries(stats.byTheme)) {
            md += `| ${theme} | ${data.total} | ${data.published} | ${data.pending} |\n`;
        }

        return md;
    }
}

// ============ 主程序 ============
class ManhuaSystem {
    constructor() {
        this.cm = new ContentManager();
        this.sm = new ScheduleManager(this.cm);
        this.rs = new ReminderSystem();
        this.stats = new Statistics(this.cm);
    }

    // 初始化
    init() {
        console.log('\n🔧 漫剧出海内容管理系统');
        console.log('='.repeat(40));

        // 确保目录存在
        this.ensureDirs();
    }

    // 确保目录存在
    ensureDirs() {
        const dirs = [
            path.join(CONFIG.contentDir, '..'),
            CONFIG.outputDir,
            path.join(CONFIG.outputDir, 'pending'),
            path.join(CONFIG.outputDir, 'published'),
            path.join(CONFIG.contentDir, '..', 'data')
        ];

        dirs.forEach(dir => {
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
        });
    }

    // 运行
    run(command) {
        switch (command) {
            case 'stats':
                console.log(this.stats.generateReport());
                break;
            case 'schedule':
                const schedule = this.sm.generateSchedule(7);
                console.log(this.sm.exportSchedule(schedule));
                this.saveSchedule(schedule);
                break;
            case 'reminder':
                const scheduleForReminder = this.sm.generateSchedule(7);
                const reminderScript = this.rs.generateReminderScript(scheduleForReminder);
                this.saveReminderScript(reminderScript);
                break;
            case 'tasks':
                const scheduleForTasks = this.sm.generateSchedule(7);
                const commands = this.rs.generateTaskCommands(scheduleForTasks);
                this.saveTaskCommands(commands);
                break;
            case 'list':
                this.listContents();
                break;
            default:
                this.showHelp();
        }
    }

    // 显示帮助
    showHelp() {
        console.log(`
📖 使用说明：

  node manager.js stats      - 查看统计数据
  node manager.js schedule  - 生成7天发布计划
  node manager.js reminder  - 生成提醒脚本
  node manager.js tasks    - 生成Windows任务计划命令
  node manager.js list     - 列出所有内容
        `);
    }

    // 保存排期
    saveSchedule(schedule) {
        const file = path.join(CONFIG.outputDir, 'schedule.md');
        fs.writeFileSync(file, this.sm.exportSchedule(schedule), 'utf8');
        console.log(`✅ 排期已保存到: ${file}`);
    }

    // 保存提醒脚本
    saveReminderScript(script) {
        const file = path.join(CONFIG.outputDir, 'reminder.bat');
        fs.writeFileSync(file, script, 'utf8');
        console.log(`✅ 提醒脚本已保存到: ${file}`);
        console.log(`   双击运行即可查看今日发布计划`);
    }

    // 保存任务命令
    saveTaskCommands(commands) {
        let content = `# Windows任务计划命令\n\n`;
        content += `复制以下命令到命令提示符(管理员)执行：\n\n`;

        commands.forEach(cmd => {
            content += `## ${cmd.date} ${cmd.time} - ${cmd.theme}\n`;
            content += `\`\`\`\n${cmd.command}\n\`\`\`\n\n`;
        });

        const file = path.join(CONFIG.outputDir, 'task_commands.md');
        fs.writeFileSync(file, content, 'utf8');
        console.log(`✅ 任务命令已保存到: ${file}`);
    }

    // 列出内容
    listContents() {
        console.log('\n📋 内容列表：\n');
        this.cm.contents.forEach((c, i) => {
            const status = c.status === 'published' ? '✅' : '⏳';
            console.log(`${status} ${i + 1}. ${c.theme}`);
            console.log(`   标题: ${c.title}\n`);
        });
    }
}

// ============ 导出 ============
module.exports = { ManhuaSystem, ContentManager, ScheduleManager, Statistics };

// ============ 主入口 ============
if (require.main === module) {
    const system = new ManhuaSystem();
    system.init();
    system.run(process.argv[2] || 'help');
}
