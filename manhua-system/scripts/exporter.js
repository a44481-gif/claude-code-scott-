/**
 * 漫剧内容导出器
 * Manhua Content Exporter
 *
 * 功能：
 * - 导出为CSV格式
 * - 导出为Markdown格式
 * - 导出为Excel格式
 */

const fs = require('fs');
const path = require('path');

// ============ 配置 ============
const CONFIG = {
    inputFile: path.join(__dirname, '../content/batch_60_sets.json'),
    outputDir: path.join(__dirname, '../output')
};

// ============ 导出器类 ============
class ContentExporter {
    constructor() {
        this.contents = [];
        this.load();
    }

    // 加载内容
    load() {
        try {
            if (fs.existsSync(CONFIG.inputFile)) {
                const data = fs.readFileSync(CONFIG.inputFile, 'utf8');
                this.contents = JSON.parse(data);
                console.log(`✅ 已加载 ${this.contents.length} 条内容`);
            }
        } catch (error) {
            console.error('❌ 加载失败:', error.message);
        }
    }

    // 导出CSV
    exportCSV() {
        const headers = ['ID', '题材', '主题', '标题', '标签', '发布时间', '状态'];
        let csv = headers.join(',') + '\n';

        this.contents.forEach(c => {
            const row = [
                c.id,
                c.themeType,
                c.topic,
                `"${c.title.replace(/"/g, '""')}"`,
                `"${c.tags.join(' ')}"`,
                c.postTime,
                c.status
            ];
            csv += row.join(',') + '\n';
        });

        const file = path.join(CONFIG.outputDir, 'content_export.csv');
        fs.writeFileSync(file, '\ufeff' + csv, 'utf8'); // BOM for Excel
        console.log(`✅ CSV已导出: ${file}`);
        return file;
    }

    // 导出Markdown
    exportMarkdown() {
        let md = '# 漫剧出海内容库\n\n';
        md += `> 导出时间: ${new Date().toLocaleString('zh-CN')}\n`;
        md += `> 共 ${this.contents.length} 条内容\n\n`;

        // 按题材分组
        const themes = ['龙王', '逆袭', '虐渣', '重生', '神医', '系统'];

        themes.forEach(theme => {
            const items = this.contents.filter(c => c.themeType === theme);
            if (items.length > 0) {
                md += `## 🐉 ${theme} (${items.length}条)\n\n`;

                items.forEach((item, index) => {
                    md += `### ${index + 1}. ${item.topic}\n\n`;
                    md += `**标题**: ${item.title}\n\n`;
                    md += `**分镜**: \n\`\`\`\n${item.script}\n\`\`\`\n\n`;
                    md += `**文案**: ${item.caption}\n\n`;
                    md += `**标签**: ${item.tags.join(' ')}\n\n`;
                    md += `**发布时间**: ${item.postTime}\n\n`;
                    md += `**状态**: ${item.status}\n\n`;
                    md += `---\n\n`;
                });
            }
        });

        const file = path.join(CONFIG.outputDir, 'content_export.md');
        fs.writeFileSync(file, md, 'utf8');
        console.log(`✅ Markdown已导出: ${file}`);
        return file;
    }

    // 导出每日发布清单
    exportDailyList() {
        const times = ['12:00', '20:00', '20:30'];

        let md = '# 📅 每日发布清单\n\n';
        md += `> 生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`;

        this.contents.forEach((c, index) => {
            const dayIndex = Math.floor(index / 3);
            const slotIndex = index % 3;

            md += `## Day ${dayIndex + 1} - ${times[slotIndex]}\n\n`;
            md += `**题材**: ${c.themeType}\n`;
            md += `**主题**: ${c.topic}\n`;
            md += `**标题**: ${c.title}\n`;
            md += `**标签**: ${c.tags.join(' ')}\n\n`;
            md += `---\n\n`;
        });

        const file = path.join(CONFIG.outputDir, 'daily_publish_list.md');
        fs.writeFileSync(file, md, 'utf8');
        console.log(`✅ 每日发布清单已导出: ${file}`);
        return file;
    }

    // 导出全部
    exportAll() {
        console.log('\n📤 开始导出...\n');

        this.exportCSV();
        this.exportMarkdown();
        this.exportDailyList();

        console.log('\n✅ 全部导出完成！');
    }
}

// ============ 主程序 ============
function main() {
    console.log('\n📤 漫剧内容导出器');
    console.log('='.repeat(40));

    const exporter = new ContentExporter();

    if (exporter.contents.length === 0) {
        console.log('\n⚠️  没有内容可导出，请先运行 generator.js');
        return;
    }

    const format = process.argv[2] || 'all';

    switch (format) {
        case 'csv':
            exporter.exportCSV();
            break;
        case 'md':
            exporter.exportMarkdown();
            break;
        case 'list':
            exporter.exportDailyList();
            break;
        default:
            exporter.exportAll();
    }
}

// 运行
if (require.main === module) {
    main();
}

module.exports = { ContentExporter };
