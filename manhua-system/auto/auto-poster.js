/**
 * 漫剧出海 - 自动运营脚本
 * 每日定时生成发布内容 + 提醒
 */

const fs = require('fs');
const path = require('path');

// ============ 配置 ============
const CONFIG = {
    contentFile: path.join(__dirname, '../content/batch_60_sets.json'),
    outputDir: path.join(__dirname, '../output'),
    contentDir: path.join(__dirname, '../content')
};

// ============ 内容加载 ============
let contents = [];

function loadContents() {
    try {
        const file = path.join(CONFIG.contentFile);
        if (fs.existsSync(file)) {
            const data = fs.readFileSync(file, 'utf8');
            contents = JSON.parse(data);
        }
    } catch (e) {
        console.error('加载失败:', e.message);
    }
}

// ============ 今日内容 ============
function getTodayContent() {
    const dayOfWeek = new Date().getDay();
    const themes = ['龙王', '逆袭', '虐渣', '重生', '神医', '系统'];
    const todayTheme = themes[dayOfWeek % themes.length];

    // 获取今日主题的内容
    const themeContents = contents.filter(c => c.themeType === todayTheme);

    if (themeContents.length > 0) {
        const index = Math.floor(Math.random() * themeContents.length);
        return themeContents[index];
    }

    // 如果没有，返回第一条
    return contents[0];
}

// ============ 生成发布内容 ============
function generatePublishContent() {
    loadContents();

    const content = getTodayContent();
    const today = new Date().toLocaleDateString('zh-CN');
    const timeSlots = [
        { time: '12:00', label: '午休' },
        { time: '20:00', label: '晚间' },
        { time: '20:30', label: '黄金档' }
    ];

    let output = `╔══════════════════════════════════════════════════════════╗\n`;
    output += `║          🎬 漫剧出海 - 今日发布内容                       ║\n`;
    output += `║          📅 ${today}                                    ║\n`;
    output += `╚══════════════════════════════════════════════════════════╝\n\n`;

    // 生成3条内容
    for (let i = 0; i < 3; i++) {
        const slot = timeSlots[i];
        const item = contents[i % contents.length];

        output += `┌─────────────────────────────────────────────────────────┐\n`;
        output += `│ 第${i + 1}条 - ${slot.time} (${slot.label})                      │\n`;
        output += `├─────────────────────────────────────────────────────────┤\n`;
        output += `│                                                         │\n`;
        output += `│ 📌 题材：${item.themeType}                                       │\n`;
        output += `│ 📝 标题：                                               │\n`;
        output += `│ ${item.title.substring(0, 50)}                          │\n`;
        output += `│                                                         │\n`;
        output += `│ 🏷️ 标签：                                               │\n`;
        output += `│ ${item.tags.slice(0, 5).join(' ')}     │\n`;
        output += `│                                                         │\n`;
        output += `│ 💬 发布文案：                                           │\n`;
        output += `│ ${item.caption.substring(0, 60)}         │\n`;
        output += `│                                                         │\n`;
        output += `│ ⏰ 发布时间：${slot.time}                                  │\n`;
        output += `│                                                         │\n`;
        output += `└─────────────────────────────────────────────────────────┘\n\n`;
    }

    // 完整内容
    output += `╔══════════════════════════════════════════════════════════╗\n`;
    output += `║                    📋 完整内容                            ║\n`;
    output += `╚══════════════════════════════════════════════════════════╝\n\n`;

    for (let i = 0; i < 3; i++) {
        const item = contents[i % contents.length];
        output += `【第${i + 1}条】\n`;
        output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        output += `标题：${item.title}\n\n`;
        output += `正文：\n${item.caption}\n\n`;
        output += `标签：${item.tags.join(' ')}\n\n`;
        output += `评论置顶：👇【全集VIP已更新 $1.99】👉 链接在主页！👍 点赞+关注！\n\n`;
    }

    return output;
}

// ============ 保存发布内容 ============
function saveTodayContent() {
    const content = generatePublishContent();
    const file = path.join(CONFIG.outputDir, 'today_content.txt');
    const date = new Date().toISOString().split('T')[0];
    const mdFile = path.join(CONFIG.outputDir, `publish_${date}.md`);

    fs.writeFileSync(file, content, 'utf8');
    fs.writeFileSync(mdFile, content, 'utf8');

    console.log(content);
    console.log(`\n✅ 今日内容已保存到: ${file}`);
    console.log(`✅ Markdown版本: ${mdFile}`);

    return file;
}

// ============ 生成Windows提醒脚本 ============
function generateReminderScript() {
    const content = generatePublishContent();

    let script = `@echo off\n`;
    script += `chcp 65001 >nul\n`;
    script += `color 0A\n\n`;
    script += `echo.\n`;
    script += `echo  ╔══════════════════════════════════════════════════╗\n`;
    script += `echo  ║                                                  ║\n`;
    script += `echo  ║     🎬 漫剧出海 - 今日发布提醒                   ║\n`;
    script += `echo  ║     📅 ${new Date().toLocaleDateString('zh-CN')}                              ║\n`;
    script += `echo  ║                                                  ║\n`;
    script += `echo  ╚══════════════════════════════════════════════════╝\n`;
    script += `echo.\n`;
    script += `echo  📋 今日发布内容：\n`;
    script += `echo.\n`;
    script += `echo  ⏰ 12:00 - 第1条 (${contents[0]?.themeType || '龙王'})\n`;
    script += `echo  ⏰ 20:00 - 第2条 (${contents[1]?.themeType || '虐渣'})\n`;
    script += `echo  ⏰ 20:30 - 第3条 (${contents[2]?.themeType || '逆袭'})\n`;
    script += `echo.\n`;
    script += `echo  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    script += `echo.\n`;
    script += `echo  📝 立即发布：douyin.com / 抖音App\n`;
    script += `echo.\n`;
    script += `echo  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    script += `echo.\n`;
    script += `echo  💡 提示：打开 today_content.txt 获取完整内容\n`;
    script += `echo.\n`;
    script += `echo  按任意键打开内容文件...\n`;
    script += `pause >nul\n`;
    script += `start notepad today_content.txt\n`;

    const scriptFile = path.join(CONFIG.outputDir, 'reminder.bat');
    fs.writeFileSync(scriptFile, script, 'utf8');

    console.log(`\n✅ 提醒脚本已保存: ${scriptFile}`);
    return scriptFile;
}

// ============ 创建Windows任务计划 ============
function createScheduledTask() {
    const { exec } = require('child_process');

    // 删除旧任务
    const deleteCmd = `schtasks /delete /tn "漫剧出海每日提醒" /f 2>nul`;

    // 创建新任务 - 每天早上8点运行
    const createCmd = `schtasks /create /tn "漫剧出海每日提醒" /tr "cmd /c cd /d ${path.resolve(CONFIG.outputDir).replace(/\\/g, '\\') && path.resolve(CONFIG.outputDir).replace(/\\/g, '\\') && path.resolve(CONFIG.outputDir)} && start reminder.bat" /sc daily /st 08:00 /f`;

    console.log('\n📅 创建Windows定时任务...');
    console.log('任务：每天 08:00 自动提醒发布\n');

    exec(deleteCmd, (err) => {
        exec(createCmd, (err, stdout, stderr) => {
            if (err) {
                console.log('⚠️  任务创建可能需要管理员权限');
                console.log('请手动运行以下命令（管理员）：');
                console.log(createCmd);
            } else {
                console.log('✅ 定时任务创建成功！');
                console.log('每天 08:00 会自动提醒你发布内容');
            }
        });
    });
}

// ============ 主程序 ============
function main() {
    console.log('\n🎬 漫剧出海 - 自动运营系统');
    console.log('='.repeat(50));
    console.log('');

    // 加载内容
    loadContents();
    console.log(`📦 已加载 ${contents.length} 条内容\n`);

    // 生成今日内容
    saveTodayContent();

    // 生成提醒脚本
    generateReminderScript();

    // 创建定时任务
    createScheduledTask();

    console.log('\n🎉 自动运营系统已启动！');
    console.log('每天 08:00 自动提醒发布');
}

// 运行
main();
