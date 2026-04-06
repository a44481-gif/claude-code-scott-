/**
 * 漫剧出海 - 每日内容自动发送
 * 每天自动生成并发送内容到邮箱
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// ============ 配置 ============
const CONFIG = {
    contentFile: path.join(__dirname, '../content/batch_60_sets.json'),
    outputDir: path.join(__dirname, '../output'),
    emailApiUrl: 'https://api.telegram.org/bot',
    // 请设置你的 Telegram Bot Token
    telegramToken: 'YOUR_TELEGRAM_BOT_TOKEN',
    chatId: 'YOUR_CHAT_ID'
};

// ============ 加载内容 ============
let contents = [];

function loadContents() {
    try {
        const file = CONFIG.contentFile;
        if (fs.existsSync(file)) {
            const data = fs.readFileSync(file, 'utf8');
            contents = JSON.parse(data);
        }
    } catch (e) {
        console.error('加载失败:', e.message);
    }
}

// ============ 生成今日内容 ============
function generateTodayContent() {
    loadContents();

    const dayOfWeek = new Date().getDay();
    const themes = ['龙王', '逆袭', '虐渣', '重生', '神医', '系统'];
    const todayTheme = themes[dayOfWeek % themes.length];

    let output = `🎬 漫剧出海 - 今日发布内容\n`;
    output += `📅 ${new Date().toLocaleDateString('zh-CN')}\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    // 生成3条内容
    for (let i = 0; i < 3; i++) {
        const item = contents[i % contents.length];
        const timeSlots = ['12:00', '20:00', '20:30'];

        output += `【第${i + 1}条】⏰ ${timeSlots[i]}\n`;
        output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        output += `📌 题材：${item.themeType}\n`;
        output += `📝 标题：${item.title}\n\n`;
        output += `📖 正文：\n${item.caption}\n\n`;
        output += `🏷️ 标签：${item.tags.join(' ')}\n\n`;
        output += `💬 评论置顶：\n👇【全集VIP已更新 $1.99】👉 链接在主页！👍 点赞+关注！\n\n`;
        output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
    }

    output += `💰 变现提示：\n`;
    output += `1. 发布后引导点击主页链接\n`;
    output += `2. Linktree设置付费解锁\n`;
    output += `3. 收款到PayPal/微信\n\n`;

    output += `🎯 坚持30天，粉丝破千，月入$500+！\n`;

    return output;
}

// ============ 保存到文件 ============
function saveToFile() {
    const content = generateTodayContent();
    const today = new Date().toISOString().split('T')[0];
    const file = path.join(CONFIG.outputDir, `daily_${today}.txt`);

    fs.writeFileSync(file, content, 'utf8');
    console.log(`✅ 今日内容已保存: ${file}`);

    return content;
}

// ============ 发送到 Telegram ============
function sendToTelegram(message) {
    return new Promise((resolve, reject) => {
        const token = CONFIG.telegramToken;
        const chatId = CONFIG.chatId;

        if (token === 'YOUR_TELEGRAM_BOT_TOKEN') {
            console.log('⚠️  请先设置 Telegram Bot Token');
            console.log('📖 教程：');
            console.log('1. 搜索 @BotFather');
            console.log('2. 发送 /newbot');
            console.log('3. 获取 Token');
            console.log('4. 替换脚本中的 YOUR_TELEGRAM_BOT_TOKEN');
            resolve(false);
            return;
        }

        const postData = JSON.stringify({
            chat_id: chatId,
            text: message,
            parse_mode: 'HTML'
        });

        const options = {
            hostname: 'api.telegram.org',
            path: `/bot${token}/sendMessage`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    if (result.ok) {
                        console.log('✅ 已发送到 Telegram');
                        resolve(true);
                    } else {
                        console.log('❌ Telegram发送失败:', result.description);
                        resolve(false);
                    }
                } catch (e) {
                    resolve(false);
                }
            });
        });

        req.on('error', (e) => {
            console.log('❌ Telegram发送错误:', e.message);
            resolve(false);
        });

        req.write(postData);
        req.end();
    });
}

// ============ 创建 Windows 定时任务 ============
function createDailyTask() {
    const { exec } = require('child_process');
    const taskName = 'ManhuaDailyContent';
    const scriptPath = path.join(__dirname, 'daily-sender.bat').replace(/\\/g, '\\');
    const outputPath = path.join(CONFIG.outputDir).replace(/\\/g, '\\');

    // 创建批处理脚本
    let bat = '@echo off\n';
    bat += `chcp 65001 >nul\n`;
    bat += `cd /d "${outputPath}"\n`;
    bat += `echo. > daily_${new Date().toISOString().split('T')[0]}_sent.txt\n`;
    bat += `echo 今日内容已更新！\n`;
    bat += `start notepad daily_${new Date().toISOString().split('T')[0]}.txt\n`;

    const batFile = path.join(CONFIG.outputDir, 'daily-sender.bat');
    fs.writeFileSync(batFile, bat, 'utf8');

    // 删除旧任务
    const deleteCmd = `schtasks /delete /tn "${taskName}" /f 2>nul`;

    // 创建新任务 - 每天早上8点
    const createCmd = `schtasks /create /tn "${taskName}" /tr "notepad ${path.join(outputPath, `daily_${new Date().toISOString().split('T')[0]}.txt`)}" /sc daily /st 08:00 /f`;

    exec(deleteCmd, () => {
        exec(createCmd, (err) => {
            if (err) {
                console.log('⚠️  定时任务创建失败，请用管理员权限运行');
            } else {
                console.log('✅ 定时任务创建成功！');
                console.log('每天 08:00 会自动打开今日内容');
            }
        });
    });
}

// ============ 主程序 ============
async function main() {
    console.log('\n🎬 漫剧出海 - 每日自动发送\n');
    console.log('='.repeat(40) + '\n');

    // 生成内容
    const content = saveToFile();
    console.log('\n' + content);

    // 保存发送记录
    const sentFile = path.join(CONFIG.outputDir, `daily_${new Date().toISOString().split('T')[0]}_sent.txt`);
    fs.writeFileSync(sentFile, new Date().toISOString(), 'utf8');

    // 尝试发送到 Telegram
    await sendToTelegram(content);

    console.log('\n' + '='.repeat(40));
    console.log('✅ 今日内容生成完成！');
    console.log('📁 查看文件: output/daily_*.txt');
    console.log('\n💡 提示：打开文件复制内容到抖音发布');
}

// 运行
main();
