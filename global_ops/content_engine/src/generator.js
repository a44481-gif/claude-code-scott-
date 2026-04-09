/**
 * GlobalOPS · 内容生成引擎
 * 改造自 manhua-system/scripts/generator.js
 * 支持输出到 PostgreSQL 数据库（--db 模式）
 */

require('dotenv').config({ path: require('path').join(__dirname, '../../config/.env') });
const { Client } = require('pg');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const path = require('path');

// ============ 题材模板库 ============
const THEMES = {
  龙王: [
    '被嘲笑穷鬼上门女婿，真实身份曝光全场吓傻',
    '工地搬砖被嫌脏，大客户来工地找他',
    '婚礼现场被羞辱，三千亿将士到场',
    '丈母娘要50万彩礼，黑卡打脸',
    '农村父亲参加儿子家长会，校长喊李总',
    '外卖小哥救富二代一命，结果是隐藏大佬',
    '修空调被嫌穷，结果是整栋楼业主',
    '参加同学会被嘲笑，结果全场都是他员工',
    '当保安被白富美嘲笑，结果是她家真正继承人',
    '前女友嫌穷分手，结果他是首富儿子'
  ],
  逆袭: [
    '被公司开除那天，收到通知是公司被收购了',
    '被离婚带三宝宝，三年后渣夫求复合',
    '火锅店打工被嘲笑，服务员喊老板',
    '摆地摊被城管追，商业教父登场',
    '电子厂拧螺丝十年，真实身份是老板',
    '摆摊卖红薯被城管收走，结果是美食博主',
    '快递员被投诉丢工作，结果是集团太子',
    '被亲戚嫌弃寒酸，结果是隐藏富二代',
    '洗碗工被开除，结果是米其林大厨',
    '被相亲对象嫌弃，结果她妈妈是我粉丝'
  ],
  虐渣: [
    '渣男炫耀新女友是富家女，结果是坐台小姐',
    '闺蜜发亲密照炫耀抢男友，我让她一无所有',
    '相亲遇普信男，嫌我工资低，看到我的车吓傻',
    '表妹偷我设计稿获奖，我拿出原件让她身败名裂',
    '室友偷用化妆品还倒打一耙，监控曝光',
    '同事抢我方案获奖，我拿出聊天记录',
    '渣男说怀了双胞胎逼我让位，结果是假孕',
    '婆婆嫌我不会生，结果查出是儿子不行',
    '前男友晒现任多有钱，我晒存款他傻眼',
    '小三重生我的孩子，还说我是小三'
  ],
  重生: [
    '前世被老公和婆婆联手害死，重生到结婚前一天',
    '前世被妹妹害死，重生到她出生那天',
    '前世被合伙人背叛，重生让对方破产',
    '前世被老板压榨猝死，重生告到他破产',
    '前世被养女拔氧气管，重生归来她跪求原谅',
    '前世被闺蜜害死资产被夺，重生手撕闺蜜',
    '前世被渣爹卖女求荣，重生逆袭首富',
    '前世被室友投毒，重生让室友坐牢',
    '前世被未婚夫骗光财产，重生让他身败名裂',
    '前世肺癌晚期，重生后健康生活100年'
  ],
  神医: [
    '农村土郎中一眼看出首富得了癌症，被嘲笑',
    '实习医生被科室主任排挤，结果是医道传承人',
    '被所有人嘲笑的赤脚医生，真实身份是国医圣手',
    '穷小子继承祖传医书，成为绝世神医',
    '女护士被开除，结果是隐藏的中医天才',
    '被赶出医院的废物医生，救活了一个大人物',
    '乡村诊所来大佬求医，全科室都傻眼了',
    '废物赘婿会医术，冷面总裁找上门',
    '针灸技术被质疑，华佗金方震惊医学界',
    '被所有人看不起的村医，真实身份是神医'
  ],
  系统: [
    '高考落榜获得神级选择系统，每次选择都是神级技能',
    '送外卖获得神级厨艺系统，全球名厨拜师',
    '穷小子绑定神级投资系统，小目标一个亿',
    '普通上班族获得神级游戏系统，现实也开挂',
    '被辞退那天获得神级黑客系统，全球我最强',
    '获得神级演技系统，从群演到影帝',
    '获得神级鉴宝系统，一眼看出价值十亿古董',
    '获得神级学霸系统，从学渣到诺奖得主',
    '获得神级养殖系统，养的鱼卖出天价',
    '获得神级外卖系统，逆袭全球首富'
  ]
};

// ============ 标题模板 ============
const TITLE_TEMPLATES = {
  en: [
    "She Lived a Secret Life No One Knew About 💀",
    "He Spent 10 Years Building This... For HER 💔",
    "The Moment That SHOCKED Everyone 😱 [Short Drama]",
    "She Finally Revealed The Truth... I Can't Handle This 💔",
    "What Happened Next Will BLOW Your Mind 😱🔥",
    "The Real Identity REVEALED 😱 I Was Not Ready",
    "She Waited 10 YEARS For This Moment 💀",
    "He Was Homeless... Until THIS Changed Everything ⚡",
    "The Plot Twist That Made Everyone CRY 💔",
    "Don't Watch If You Can't Handle FEELINGS 💔",
    "He Pretended to Be Poor... His Real Status? SHOCKING 😱",
    "This Scene Has 10M+ Views. Here's Why 🎬",
    "She Was NOTHING... Until TODAY ⚡ [Empowering]",
    "The King Went Into Disguise... For 10 YEARS 👑",
    "One Decision Changed EVERYTHING 💥"
  ],
  id: [
    "Kehidupan RAHASIA Yang Tak Orang Tau 💀",
    "10 Tahun Dia Membangun Ini... Untuk DIA 💔",
    "Momen Yang MEMUKAUL Semua Orang 😱",
    "Kebenaran Terungkap... Aku Tidak Siap 💔",
    "Apa Yang Terjadi Kemudian? LUAR BIASA 😱🔥"
  ],
  vi: [
    "Cô Ấy Sống Một Cuộc Đời Bí Mật 😱",
    "Anh Ấy Dành 10 Năm Xây Dựng Điều Này... CHO Cô Ấy 💔",
    "Khoảnh Khắc Khiến Tất Cả Mọi Người KINH NGẠC 😱",
    "Sự Thật Được Tiết Lộ... Tôi Không Thể Chịu Được 💔"
  ],
  th: [
    "เธอใช้ชีวิตลับจากคนทั้งโลก 💀",
    "เขาใช้เวลา 10 ปีสร้างสิ่งนี้... สำหรับเธอ 💔",
    "ช่วงเวลาที่ทำให้ทุกคนตกใจ 😱"
  ]
};

// ============ 脚本模板（6格分镜）============
const SCRIPT_TEMPLATES = {
  开局: [
    { scene: "场景1", action: "展示主角平凡/被欺负的日常", emotion: "压抑" },
    { scene: "场景2", action: "被嘲笑/羞辱的关键时刻", emotion: "愤怒" },
    { scene: "场景3", action: "突发事件（电话/来客/证据出现）", emotion: "震惊" },
    { scene: "场景4", action: "身份开始暴露，小露一手", emotion: "惊讶" },
    { scene: "场景5", action: "对方发现真相，表情崩溃", emotion: "反转" },
    { scene: "场景6", action: "主角微微一笑，淡定离场 / 霸气回应", emotion: "爽" }
  ],
  龙王: [
    { scene: "场景1", action: "主角被嘲笑身份低微", emotion: "委屈" },
    { scene: "场景2", action: "有权势的人出现，对主角恭敬", emotion: "震惊" },
    { scene: "场景3", action: "嘲笑者当场吓傻，脸色发白", emotion: "惊恐" },
    { scene: "场景4", action: "主角微微一笑：你想多了", emotion: "淡定" },
    { scene: "场景5", action: "揭示真实身份（战神/首富/继承人）", emotion: "震撼" },
    { scene: "场景6", action: "对方跪地求饶 / 全场震惊", emotion: "爽" }
  ],
  逆袭: [
    { scene: "场景1", action: "主角处于人生最低谷", emotion: "悲惨" },
    { scene: "场景2", action: "收到意外消息（原来是总裁/继承人）", emotion: "震惊" },
    { scene: "场景3", action: "曾经看不起他的人态度180度转变", emotion: "反转" },
    { scene: "场景4", action: "主角展示真正实力", emotion: "霸气" },
    { scene: "场景5", action: "打脸现场，痛快", emotion: "爽" },
    { scene: "场景6", action: "华丽转身，新的开始", emotion: "希望" }
  ]
};

// ============ 标签库 ============
const TAG_TEMPLATES = {
  en: {
    龙王: ["billionaire", "secretidentity", "dramatic", "plot twist", "richback", "mustwatch", "viral", "short drama", "emotional", "satisfying"],
    逆袭: ["underdog", "rags to riches", "inspiring", "comeback", "never give up", "motivation", "short drama", "plot twist", "viral", "empowering"],
    虐渣: ["revenge", "justice", "badpeople", "karma", "satisfying", "plot twist", "drama", "viral", "short drama", "epic"],
    重生: ["rebirth", "second chance", "change destiny", "dramatic", "plot twist", "short drama", "viral", "emotional", "inspiring", "mustwatch"],
    神医: ["doctordrama", "medical miracle", "genius", "plot twist", "short drama", "viral", "satisfying", "emotional", "mustwatch"],
    系统: ["system", "isekai", "powers", "level up", "short drama", "plot twist", "viral", "exciting", "satisfying", "mustwatch"]
  },
  id: ["drama", "short drama", "viral", "plot twist", "satisfying", "emotional", "indonesia", "trending"],
  vi: ["drama", "phim ngắn", "viral", "xoay chuyển", "thỏa mãn", "cảm xúc", "việt nam", "xu hướng"],
  th: ["ละครสั้น", "วังวน", "ไวรัล", "พล็อตบิด", "น่าพอใจ", "อารมณ์", "ไทย", "เทรนด์"]
};

// ============ CTA 文案 ============
const CTA_TEMPLATES = [
  "▶ Watch Part 2 — Link in Bio!",
  "❤️ Like + Follow for Part 2",
  "💬 Comment 'DRAMA' for Part 3",
  "🔁 Repost if this shocked you",
  "▶️ Full episode link in bio (FREE)",
  "💬 Tag someone who needs this energy!",
  "Follow for daily drama content ✨",
  "❤️ Like if you want Part 2",
  "▶ Watch how it ends — click the link!",
  "💬 Drop a ❤️ if you relate!"
];

// ============ 情绪词库 ============
const EMOTION_WORDS = {
  en: ["SHOCKING", "EMOTIONAL", "INSANE", "CRAZY", "EPIC", "BEAUTIFUL", "HEARTBREAKING", "UNEXPECTED", "LEGENDARY", "WILD"],
  id: ["MENGHARUKAN", "MEMUKAULKAN", "LUAR BIASA", "GANJIL", "EPIC", "BEAUTIFUL"],
  vi: ["KINH DỊ", "CẢM ĐỘNG", "ĐIÊN RỒ", "BẤT NGỜ", " Huy hoàng", "Tan vỡ"],
  th: ["ตกใจ", "สะเทือนใจ", "บ้าคลั่ง", "ไม่คาดคิด", "สุดยอด"]
};

// ============ 工具函数 ============
function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function shuffleArray(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function buildTitleEN(theme, topic) {
  const templates = TITLE_TEMPLATES.en;
  const template = pickRandom(templates);
  return template
    .replace("She", pickRandom(["She", "He", "This Girl", "This Guy", "The Woman", "The Man"]))
    .replace("she", pickRandom(["she", "he", "she", "the woman", "the man"]))
    .replace("she's", pickRandom(["she's", "he's", "she's"]));
}

function buildCaptionEN(theme, topic, title) {
  const cta = pickRandom(CTA_TEMPLATES);
  return `${title}\n\nThis story is everything 💔🔥\n\nFollow @manhua_sharing for daily drama content!\n\n#shortdrama #dramacontent #${theme.toLowerCase()} #plot #emotional #viral #mustwatch\n\n${cta}`;
}

function buildTagsEN(theme, count = 15) {
  const base = TAG_TEMPLATES.en[theme] || TAG_TEMPLATES.en["龙王"];
  const shuffled = shuffleArray([...base]);
  const emotionTags = shuffleArray(EMOTION_WORDS.en).slice(0, 3);
  return [...shuffled.slice(0, count - 3), ...emotionTags, "followforcontent"];
}

function buildScript6Panel(theme, topic) {
  const template = SCRIPT_TEMPLATES[theme] || SCRIPT_TEMPLATES["开局"];
  return template.map((panel, i) => ({
    panel: i + 1,
    scene: panel.scene,
    action: panel.action,
    emotion: panel.emotion,
    narration: `${panel.emotion} moment in the ${theme} story`
  }));
}

function buildThumbnailPrompt(theme, topic) {
  const prompts = {
    龙王: "dramatic dark scene, shocked crowd, spotlight on mysterious figure, red and gold theme, epic scale, manga style, high contrast",
    逆袭: "underdog transformation, before and after contrast, golden light from above, inspiring composition, anime art style, cinematic",
    虐渣: "revenge scene, satisfying karma moment, dramatic lighting, confident pose, cool attitude, manga panel style",
    重生: "time rewind effect, clock fragments, mystical glow, rebirth atmosphere, blue and white theme, anime style",
    神医: "medical drama, sophisticated hospital setting, wise doctor figure, green and white theme, serious yet warm atmosphere",
    系统: "futuristic HUD interface, glowing system screen, character with supernatural aura, tech meets fantasy, vibrant colors"
  };
  return prompts[theme] || prompts["龙王"];
}

function generateContentId(theme) {
  const date = new Date();
  const dateStr = date.toISOString().slice(0, 10).replace(/-/g, "");
  const short = uuidv4().slice(0, 8);
  return `${theme.slice(0, 2)}_${dateStr}_${short}`;
}

// ============ 数据库连接 ============
function getDbClient() {
  return new Client({
    host: process.env.POSTGRES_HOST || 'localhost',
    port: process.env.POSTGRES_PORT || 5432,
    database: process.env.POSTGRES_DB || 'global_ops',
    user: process.env.POSTGRES_USER || 'postgres',
    password: process.env.POSTGRES_PASSWORD || '',
  });
}

// ============ 单条生成 ============
function generateSingleContent(theme, topic, options = {}) {
  const lang = options.lang || 'en';
  const region = options.region || 'southeast_asia';
  const script = buildScript6Panel(theme, topic);
  const title = buildTitleEN(theme, topic);
  const caption = buildCaptionEN(theme, topic, title);
  const tags = buildTagsEN(theme);
  const thumbnail_prompt = buildThumbnailPrompt(theme, topic);
  const cta = pickRandom(CTA_TEMPLATES);

  const content = {
    content_id: generateContentId(theme),
    theme_type: theme,
    topic: topic,
    title: title,
    title_en: title,
    caption: caption,
    caption_en: caption,
    script_6panel: JSON.stringify(script),
    tags: tags,
    cta_text: cta,
    thumbnail_prompt: thumbnail_prompt,
    target_lang: lang,
    target_region: region,
    status: 'pending',
    copyright_risk: theme === '龙王' ? 'high' : theme === '逆袭' ? 'medium' : 'low',
    priority: theme === '龙王' ? 8 : theme === '逆袭' ? 7 : theme === '虐渣' ? 7 : 5,
    best_post_time: region === 'southeast_asia' ? '19:00-22:00 ICT' : '15:00-18:00 UTC',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  return content;
}

// ============ 批量生成 ============
function generateBatch(options = {}) {
  const count = options.count || 10;
  const theme = options.theme || null;
  const lang = options.lang || 'en';
  const region = options.region || 'southeast_asia';
  const outputFile = options.outputFile || null;

  const themes = theme ? [theme] : Object.keys(THEMES);
  const allContents = [];

  for (const t of themes) {
    const topics = THEMES[t];
    for (let i = 0; i < Math.ceil(count / themes.length); i++) {
      const topic = topics[i % topics.length];
      const content = generateSingleContent(t, topic, { lang, region });
      allContents.push(content);
      if (allContents.length >= count) break;
    }
    if (allContents.length >= count) break;
  }

  return allContents.slice(0, count);
}

// ============ 写入数据库 ============
async function saveToDatabase(contents) {
  const client = getDbClient();
  await client.connect();

  let saved = 0;
  let skipped = 0;

  for (const content of contents) {
    try {
      const sql = `
        INSERT INTO content_items (
          content_id, theme_type, topic, title, title_en,
          caption, caption_en, script_6panel, tags, cta_text,
          thumbnail_prompt, target_lang, target_region,
          status, copyright_risk, priority, best_post_time
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)
        ON CONFLICT (content_id) DO UPDATE SET updated_at = NOW()
      `;
      await client.query(sql, [
        content.content_id, content.theme_type, content.topic,
        content.title, content.title_en, content.caption, content.caption_en,
        content.script_6panel, content.tags, content.cta_text,
        content.thumbnail_prompt, content.target_lang, content.target_region,
        content.status, content.copyright_risk, content.priority, content.best_post_time
      ]);
      saved++;
      process.stdout.write(`  ✅ ${content.content_id} [${content.theme_type}]\n`);
    } catch (err) {
      console.error(`  ❌ 写入失败 ${content.content_id}: ${err.message}`);
      skipped++;
    }
  }

  await client.end();
  return { saved, skipped };
}

// ============ 主程序 ============
async function main() {
  const args = process.argv.slice(2);
  const useDb = args.includes('--db');
  const countArg = args.find(a => a.startsWith('--count='));
  const count = countArg ? parseInt(countArg.split('=')[1]) : 10;
  const themeArg = args.find(a => a.startsWith('--theme='));
  const theme = themeArg ? themeArg.split('=')[1] : null;

  console.log(`\n🎬 GlobalOPS Content Generator`);
  console.log(`   Mode: ${useDb ? 'DATABASE' : 'JSON FILE'}`);
  console.log(`   Count: ${count}`);
  console.log(`   Theme: ${theme || 'ALL'}\n`);

  const contents = generateBatch({ count, theme });

  if (useDb) {
    console.log(`📤 写入 PostgreSQL 数据库...\n`);
    const { saved, skipped } = await saveToDatabase(contents);
    console.log(`\n✅ 完成！保存: ${saved} | 跳过: ${skipped}`);
  } else {
    const outputPath = path.join(__dirname, `../../output/content_batch_${Date.now()}.json`);
    fs.ensureDirSync(path.dirname(outputPath));
    fs.writeFileSync(outputPath, JSON.stringify(contents, null, 2), 'utf-8');
    console.log(`✅ 生成完成！${contents.length} 条内容已保存至 ${outputPath}`);

    // 打印前3条预览
    console.log(`\n📋 预览（前3条）:`);
    contents.slice(0, 3).forEach((c, i) => {
      console.log(`\n--- 内容 ${i + 1} ---`);
      console.log(`ID: ${c.content_id}`);
      console.log(`题材: ${c.theme_type} | ${c.topic}`);
      console.log(`标题: ${c.title}`);
      console.log(`标签: ${c.tags.slice(0, 5).join(', ')}...`);
    });
  }
}

main().catch(console.error);
