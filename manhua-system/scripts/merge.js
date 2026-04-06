/**
 * 漫剧内容合并脚本
 * 合并所有内容到一个JSON文件
 */

const fs = require('fs');
const path = require('path');

const CONFIG = {
    contentDir: path.join(__dirname, '../content'),
    outputFile: path.join(__dirname, '../content/batch_60_sets.json')
};

function mergeContent() {
    console.log('\n🔄 合并内容文件...\n');

    const part1 = path.join(CONFIG.contentDir, 'batch_60_sets_part1.json');
    const part2 = path.join(CONFIG.contentDir, 'batch_60_sets_part2.json');

    try {
        // 读取第一部分
        const data1 = JSON.parse(fs.readFileSync(part1, 'utf8'));
        console.log(`✅ 读取第1部分: ${data1.length} 条`);

        // 读取第二部分
        const data2 = JSON.parse(fs.readFileSync(part2, 'utf8'));
        console.log(`✅ 读取第2部分: ${data2.length} 条`);

        // 合并
        const merged = [...data1, ...data2];
        console.log(`\n✅ 合并完成: ${merged.length} 条内容`);

        // 保存
        fs.writeFileSync(CONFIG.outputFile, JSON.stringify(merged, null, 2), 'utf8');
        console.log(`✅ 已保存到: ${CONFIG.outputFile}`);

        // 统计
        const stats = {};
        merged.forEach(c => {
            if (!stats[c.themeType]) {
                stats[c.themeType] = 0;
            }
            stats[c.themeType]++;
        });

        console.log('\n📊 统计：');
        for (const [theme, count] of Object.entries(stats)) {
            console.log(`   ${theme}: ${count} 条`);
        }

        return merged;
    } catch (error) {
        console.error('❌ 合并失败:', error.message);
        return null;
    }
}

if (require.main === module) {
    mergeContent();
}

module.exports = { mergeContent };
