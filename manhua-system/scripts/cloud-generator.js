/**
 * 漫剧出海 - 云端内容生成器
 * 专为 GitHub Actions / n8n Cloud 优化
 */

const fs = require('fs');
const path = require('path');

// ============ 内容模板库（内置，无需外部文件）===========
const THEMES = {
    龙王: [
        '被嘲笑穷鬼上门女婿',
        '工地搬砖被嫌脏',
        '婚礼现场被羞辱',
        '丈母娘要50万彩礼',
        '农村父亲参加家长会',
        '外卖小哥救富二代',
        '修空调被嫌穷',
        '参加同学会被嘲笑',
        '当保安被白富美嘲笑',
        '前女友嫌穷分手'
    ],
    逆袭: [
        '被公司开除收到1个亿',
        '被离婚带三宝宝',
        '火锅店打工被嘲笑',
        '摆地摊被城管追',
        '电子厂拧螺丝十年',
        '摆摊卖红薯被城管收',
        '快递员被投诉丢工作',
        '被亲戚嫌弃寒酸',
        '洗碗工被开除',
        '被相亲对象嫌弃'
    ],
    虐渣: [
        '渣男炫耀新女友',
        '闺蜜抢男友',
        '相亲遇普信男',
        '表妹偷设计稿',
        '室友偷化妆品',
        '同事抢我方案获奖',
        '渣男说怀了双胞胎逼我让位',
        '婆婆嫌我不会生',
        '前男友晒现任多有钱',
        '小三重生我的孩子'
    ],
    重生: [
        '被老公婆婆害死',
        '被妹妹害死',
        '被合伙人背叛',
        '被老板压榨猝死',
        '被养女拔氧气管',
        '被网暴自杀',
        '被扶弟魔老公离婚',
        '被假名媛抢走一切',
        '被闺蜜和老公联手害死',
        '被继母继妹害死'
    ],
    神医: [
        '路边救摔倒老人',
        '飞机上救人',
        '被师父赶下山',
        '医院放弃治疗',
        '治好小乞丐',
        '治好瘫痪老人',
        '救了个晕倒的老人',
        '在医院被排挤',
        '救了快倒闭的医馆',
        '治好癌症晚期患者'
    ],
    系统: [
        '绑定神级篮球系统',
        '绑定神级选择系统',
        '绑定神级投资系统',
        '绑定神级厨神系统',
        '绑定神级美妆系统',
        '绑定神级游戏系统',
        '绑定神级黑客系统',
        '绑定神级rap系统',
        '绑定神级学霸系统',
        '绑定神级养殖系统'
    ]
};

const TITLES = {
    龙王: [
        '下一秒十辆豪车来接！丈母娘当场吓瘫！😭🐉',
        '下一秒大客户来工地找他！工友当场吓傻！😂🐉',
        '下一秒三千亿将士到场！全场吓傻跪地求饶！😭👑',
        '下一秒拿出黑卡全场吓傻！💳🐉',
        '下一秒系统奖励翻倍！渣女跪地求饶！💰🐉'
    ],
    逆袭: [
        '下一秒收到到账1个亿！老板求他回去当董事长！💰💼',
        '三年后我带三个天才宝宝回归！渣夫当场吓哭！😭💪',
        '下一秒服务员喊他老板！😂💪',
        '下一秒商业教父登场！😂💼',
        '下一秒全体员工傻眼了！💪'
    ],
    虐渣: [
        '我发了一张照片！全场炸了！😂🔥',
        '我不动声色让她一无所有！🔥手撕绿茶！',
        '下一秒看到我的劳斯莱斯直接吓傻！😂💳',
        '我拿出原件！她当场崩溃！🔥',
        '我亮出监控！她当场社死！😂🔥'
    ],
    重生: [
        '重生到结婚前一天！我：不嫁了！😭⚡',
        '重生到她出生那天！这一世我要改写命运！😭⚡',
        '重生创业！这一世我要让他血本无归！💰⚡',
        '重生归来告到他破产！⚡',
        '重生归来她跪求原谅！😭⚡'
    ],
    神医: [
        '所有人绕着走！结果他是首富亲爹！🩺💰',
        '三针下去她当场醒来！🩺',
        '下山第一天全世界都震惊了！🩺⚡',
        '三个月后完全康复！🩺',
        '治好他改变了我的一生！🩺💰'
    ],
    系统: [
        '一挑五完胜校队主力！🏀🎮',
        '第一块石头开出帝王绿！前女友后悔！💰🎮',
        '三个月翻100倍！老板求我收购！💰',
        '一份蛋炒饭惊艳全场！🍳🎮',
        '逆袭成女王让前男友后悔！🎮💄'
    ]
};

const TAG_TEMPLATES = {
    龙王: ['#龙王', '#豪门', '#隐藏身份', '#反转', '#逆袭', '#爽剧', '#漫剧', '#全集解锁', '#海外华人', '#爆款'],
    逆袭: ['#逆袭', '#底层翻身', '#打脸', '#人生巅峰', '#爽剧', '#漫剧', '#全集解锁', '#海外华人', '#爆款', '#励志'],
    虐渣: ['#虐渣', '#手撕绿茶', '#复仇', '#打脸', '#女性力量', '#爽剧', '#漫剧', '#全集解锁', '#海外华人', '#爆款'],
    重生: ['#重生', '#改写命运', '#复仇', '#虐渣', '#逆转人生', '#爽剧', '#漫剧', '#全集解锁', '#海外华人', '#爆款'],
    神医: ['#神医', '#中医', '#医术超群', '#救人', '#传承', '#爽剧', '#漫剧', '#全集解锁', '#海外华人', '#爆款'],
    系统: ['#系统流', '#神级选择', '#开挂', '#逆袭', '#爽剧', '#漫剧', '#全集解锁', '#海外华人', '#爆款', '#升级打怪']
};

// ============ 内容生成器 ============
class CloudContentGenerator {
    constructor() {
        this.contents = [];
        this.count = 0;
    }

    generateAll() {
        console.log('\n🚀 云端内容生成开始...\n');

        const themeNames = Object.keys(THEMES);
        const today = new Date().getDay();
        const todayTheme = themeNames[today % themeNames.length];

        // 生成今日主题的5套内容
        const topics = THEMES[todayTheme] || THEMES['龙王'];

        topics.forEach((topic, index) => {
            const content = this.generateContent(todayTheme, topic, index + 1);
            this.contents.push(content);
            this.count++;
            console.log(`  ✅ ${this.count}. ${todayTheme} - ${topic}`);
        });

        // 如果内容量小于5，补充其他题材
        if (this.contents.length < 5) {
            themeNames.forEach(theme => {
                if (theme !== todayTheme && this.contents.length < 10) {
                    const topic = THEMES[theme][Math.floor(Math.random() * THEMES[theme].length)];
                    const content = this.generateContent(theme, topic, this.contents.length + 1);
                    this.contents.push(content);
                    this.count++;
                    console.log(`  ✅ ${this.count}. ${theme} - ${topic}`);
                }
            });
        }

        console.log(`\n✅ 共生成 ${this.count} 条内容`);
        return this.contents;
    }

    generateContent(theme, topic, index) {
        const id = `cloud_${Date.now()}_${index}`;
        const titles = TITLES[theme] || TITLES['龙王'];
        const title = titles[Math.floor(Math.random() * titles.length)];

        return {
            id,
            index: this.count,
            theme: `${theme}-${topic}`,
            themeType: theme,
            topic,
            title: `${topic}！${title}`,
            script: this.generateScript(theme, topic),
            caption: this.generateCaption(theme, topic),
            tags: TAG_TEMPLATES[theme] || TAG_TEMPLATES['龙王'],
            cta: '👇【全集VIP已更新 $1.99】👉 链接在主页！👍 点赞+关注！',
            postTime: this.getPostTime(theme),
            status: 'pending',
            generatedAt: new Date().toISOString()
        };
    }

    generateScript(theme, topic) {
        return `格1: ${topic}...\n格2: 故事发展...\n格3: 冲突升级...\n格4: 反转开始...\n格5: 高潮迭起...\n格6: 全集VIP已更新👑`;
    }

    generateCaption(theme, topic) {
        return `${topic}\n\n精彩故事，不容错过！\n\n👇【全集VIP已更新 $1.99】\n👍 点赞+关注！`;
    }

    getPostTime(theme) {
        const times = {
            龙王: '北京时间 20:00-22:00',
            逆袭: '北京时间 21:00-23:00',
            虐渣: '北京时间 20:30-22:30',
            重生: '北京时间 21:30-23:30',
            神医: '北京时间 12:00-13:00',
            系统: '北京时间 20:00-23:00'
        };
        return times[theme] || '北京时间 20:00-22:00';
    }

    save(outputPath) {
        try {
            fs.writeFileSync(outputPath, JSON.stringify(this.contents, null, 2), 'utf8');
            console.log(`\n✅ 已保存到: ${outputPath}`);
            return true;
        } catch (error) {
            console.error('\n❌ 保存失败:', error.message);
            return false;
        }
    }

    exportMarkdown() {
        let md = `# 🎬 今日发布内容\n\n`;
        md += `> 生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`;

        this.contents.forEach((c, i) => {
            md += `## ${i + 1}. ${c.theme}\n\n`;
            md += `**题材**: ${c.themeType}\n\n`;
            md += `**标题**: ${c.title}\n\n`;
            md += `**正文**: ${c.caption}\n\n`;
            md += `**标签**: ${c.tags.join(' ')}\n\n`;
            md += `**发布时间**: ${c.postTime}\n\n`;
            md += `---\n\n`;
        });

        md += `## 📋 发布清单\n\n`;
        md += `| 序号 | 时间 | 题材 | 标题 |\n`;
        md += `|------|------|------|------|\n`;

        const timeSlots = ['12:00', '20:00', '20:30', '明天12:00', '明天20:00'];
        this.contents.forEach((c, i) => {
            md += `| ${i + 1} | ${timeSlots[i]} | ${c.themeType} | ${c.title.substring(0, 30)}... |\n`;
        });

        return md;
    }
}

// ============ 主程序 ============
function main() {
    console.log('\n☁️ 漫剧出海 - 云端内容生成器');
    console.log('='.repeat(40));

    const generator = new CloudContentGenerator();
    generator.generateAll();

    // 输出路径
    const outputDir = process.env.GITHUB_WORKSPACE || __dirname;
    const jsonPath = path.join(outputDir, 'output', 'daily_content.json');
    const mdPath = path.join(outputDir, 'output', 'daily_publish.md');

    // 确保目录存在
    const outputDirPath = path.join(outputDir, 'output');
    if (!fs.existsSync(outputDirPath)) {
        fs.mkdirSync(outputDirPath, { recursive: true });
    }

    // 保存JSON
    generator.save(jsonPath);

    // 保存Markdown
    fs.writeFileSync(mdPath, generator.exportMarkdown(), 'utf8');
    console.log(`✅ Markdown已保存到: ${mdPath}`);

    console.log('\n☁️ 云端生成完成！');
}

// 运行
main();
