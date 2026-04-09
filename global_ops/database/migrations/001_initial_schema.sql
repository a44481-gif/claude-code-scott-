-- ============================================================
--  统一短剧出海自动运营系统 · 数据库迁移脚本
--  GlobalOPS · PostgreSQL Schema
--  基于 n8n-ai/db/init.sql 扩展
-- ============================================================

-- 扩展 uuid 生成
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 表 1: content_items    统一内容库
-- ============================================================
CREATE TABLE IF NOT EXISTS content_items (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(100) UNIQUE NOT NULL,
    theme_type VARCHAR(50) NOT NULL,          -- 龙王/逆袭/虐渣/重生/神医/系统
    topic TEXT NOT NULL,                       -- 具体主题
    title TEXT,
    title_en TEXT,
    title_id TEXT,
    title_vi TEXT,
    title_th TEXT,
    title_es TEXT,
    title_ar TEXT,
    script_6panel TEXT,                        -- JSON 格式分镜
    caption TEXT,
    caption_en TEXT,
    tags TEXT[],
    cta_text VARCHAR(255),
    best_post_time VARCHAR(100),
    target_region VARCHAR(50) DEFAULT 'southeast_asia',
    target_lang VARCHAR(10) DEFAULT 'en',
    status VARCHAR(20) DEFAULT 'pending',      -- pending/generated/clipping/ready/published
    source_file VARCHAR(500),
    video_output VARCHAR(500),
    thumbnail_output VARCHAR(500),
    thumbnail_prompt TEXT,
    duration_seconds INT DEFAULT 90,
    aspect_ratio VARCHAR(10) DEFAULT '9:16',
    copyright_risk VARCHAR(20) DEFAULT 'medium',
    views_24h INT DEFAULT 0,
    views_7d INT DEFAULT 0,
    likes INT DEFAULT 0,
    comments_count INT DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    priority INT DEFAULT 5,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 表 2: publish_log    发布记录
-- ============================================================
CREATE TABLE IF NOT EXISTS publish_log (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(100),
    platform VARCHAR(30) NOT NULL,            -- youtube/tiktok/instagram/facebook/pinterest
    account_id VARCHAR(100),
    account_name VARCHAR(200),
    video_url TEXT,
    video_id VARCHAR(200),
    title VARCHAR(500),
    description TEXT,
    tags_applied TEXT[],
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'scheduled',   -- scheduled/published/failed/removed
    views_24h INT DEFAULT 0,
    views_7d INT DEFAULT 0,
    views_total BIGINT DEFAULT 0,
    likes INT DEFAULT 0,
    comments_count INT DEFAULT 0,
    shares INT DEFAULT 0,
    subscribers_gained INT DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    cpm DECIMAL(10,2) DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 表 3: platform_accounts    账号矩阵
-- ============================================================
CREATE TABLE IF NOT EXISTS platform_accounts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(30) NOT NULL,             -- youtube/tiktok/instagram/facebook/pinterest
    account_id VARCHAR(100) NOT NULL UNIQUE,
    account_name VARCHAR(200),
    account_handle VARCHAR(200),
    region VARCHAR(50) DEFAULT 'global',
    language VARCHAR(10) DEFAULT 'en',
    status VARCHAR(20) DEFAULT 'active',      -- active/suspended/throttled/dormant
    credentials JSONB,                         -- encrypted tokens/secrets
    cookies TEXT,
    api_key VARCHAR(500),
    proxy_url VARCHAR(500),
    total_uploads INT DEFAULT 0,
    total_views BIGINT DEFAULT 0,
    total_subscribers INT DEFAULT 0,
    avg_cpm DECIMAL(10,2) DEFAULT 0,
    last_upload_at TIMESTAMP,
    last_check_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 表 4: scheduled_tasks    调度任务队列
-- ============================================================
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id SERIAL PRIMARY KEY,
    task_uuid VARCHAR(100) UNIQUE DEFAULT uuid_generate_v4()::text,
    content_id VARCHAR(100),
    platform VARCHAR(30),
    account_id VARCHAR(100),
    task_type VARCHAR(30) NOT NULL,           -- generate/clip/translate/thumb/publish/analytics
    priority INT DEFAULT 5,                   -- 1=highest, 10=lowest
    status VARCHAR(20) DEFAULT 'pending',     -- pending/running/completed/failed/skipped
    scheduled_time TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    params JSONB,                             -- task-specific parameters
    result JSONB,                              -- task output/result
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 表 5: daily_revenue    每日收益
-- ============================================================
CREATE TABLE IF NOT EXISTS daily_revenue (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(30) NOT NULL,
    account_id VARCHAR(100),
    content_id VARCHAR(100),
    gross_revenue DECIMAL(10,2) DEFAULT 0,
    net_revenue DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    revenue_type VARCHAR(50),                  -- ad_revenue/affiliate/sponsorship/bonus
    impressions BIGINT DEFAULT 0,
    clicks INT DEFAULT 0,
    ctr DECIMAL(6,4) DEFAULT 0,
    rpm DECIMAL(10,4) DEFAULT 0,
    estimated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 表 6: copyright_risks    版权风险记录
-- ============================================================
CREATE TABLE IF NOT EXISTS copyright_risks (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(100),
    source_file VARCHAR(500),
    risk_level VARCHAR(20) NOT NULL,          -- low/medium/high/critical
    risk_type VARCHAR(50),                    -- music/video/character/audio
    matched_content VARCHAR(255),
    matched_percentage INT,
    matched_source VARCHAR(100),              -- youtube_content_id/p3_api
    action_taken VARCHAR(100),                -- none/clipped/removed/claimed
    revenue_claimed DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 表 7: content_themes    题材模板库（静态数据）
-- ============================================================
CREATE TABLE IF NOT EXISTS content_themes (
    id SERIAL PRIMARY KEY,
    theme_type VARCHAR(50) NOT NULL,
    theme_order INT,
    topic TEXT NOT NULL,
    hot_level VARCHAR(20) DEFAULT 'medium',   -- low/medium/high/viral
    best_regions TEXT[],                       -- 适合地区
    best_languages TEXT[],                    -- 适合语言
    avg_views_bucket VARCHAR(20),             -- low/mid/high
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 表 8: daily_stats    每日运营数据快照
-- ============================================================
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_videos_published INT DEFAULT 0,
    total_views BIGINT DEFAULT 0,
    total_likes INT DEFAULT 0,
    total_comments INT DEFAULT 0,
    total_revenue DECIMAL(10,2) DEFAULT 0,
    new_subscribers INT DEFAULT 0,
    platform_breakdown JSONB,                 -- {youtube: {views:0}, tiktok:{views:0}}
    top_content JSONB,                        -- top 5 content by views
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 索引
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_content_status ON content_items(status);
CREATE INDEX IF NOT EXISTS idx_content_theme ON content_items(theme_type);
CREATE INDEX IF NOT EXISTS idx_content_region ON content_items(target_region);
CREATE INDEX IF NOT EXISTS idx_content_created ON content_items(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_publish_platform ON publish_log(platform);
CREATE INDEX IF NOT EXISTS idx_publish_account ON publish_log(account_id);
CREATE INDEX IF NOT EXISTS idx_publish_date ON publish_log(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_publish_status ON publish_log(status);

CREATE INDEX IF NOT EXISTS idx_accounts_platform ON platform_accounts(platform);
CREATE INDEX IF NOT EXISTS idx_accounts_status ON platform_accounts(status);

CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON scheduled_tasks(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON scheduled_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON scheduled_tasks(task_type);

CREATE INDEX IF NOT EXISTS idx_revenue_date ON daily_revenue(date DESC);
CREATE INDEX IF NOT EXISTS idx_revenue_platform ON daily_revenue(platform);

CREATE INDEX IF NOT EXISTS idx_copyright_level ON copyright_risks(risk_level);

-- ============================================================
-- 触发器：updated_at 自动更新
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_content_items_updated_at BEFORE UPDATE ON content_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_publish_log_updated_at BEFORE UPDATE ON publish_log
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_platform_accounts_updated_at BEFORE UPDATE ON platform_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 种子数据：content_themes（从 generator.js 的 THEMES 迁移）
-- ============================================================
INSERT INTO content_themes (theme_type, topic) VALUES
-- 龙王 (10)
('龙王','被嘲笑穷鬼上门女婿，真实身份曝光全场吓傻'),
('龙王','工地搬砖被嫌脏，大客户来工地找他'),
('龙王','婚礼现场被羞辱，三千亿将士到场'),
('龙王','丈母娘要50万彩礼，黑卡打脸'),
('龙王','农村父亲参加儿子家长会，校长喊李总'),
('龙王','外卖小哥救富二代一命，结果是隐藏大佬'),
('龙王','修空调被嫌穷，结果是整栋楼业主'),
('龙王','参加同学会被嘲笑，结果全场都是他员工'),
('龙王','当保安被白富美嘲笑，结果是她家真正继承人'),
('龙王','前女友嫌穷分手，结果他是首富儿子'),
-- 逆袭 (10)
('逆袭','被公司开除那天，收到通知是公司被收购了'),
('逆袭','被离婚带三宝宝，三年后渣夫求复合'),
('逆袭','火锅店打工被嘲笑，服务员喊老板'),
('逆袭','摆地摊被城管追，商业教父登场'),
('逆袭','电子厂拧螺丝十年，真实身份是老板'),
('逆袭','摆摊卖红薯被城管收走，结果是美食博主'),
('逆袭','快递员被投诉丢工作，结果是集团太子'),
('逆袭','被亲戚嫌弃寒酸，结果是隐藏富二代'),
('逆袭','洗碗工被开除，结果是米其林大厨'),
('逆袭','被相亲对象嫌弃，结果她妈妈是我粉丝'),
-- 虐渣 (10)
('虐渣','渣男炫耀新女友是富家女，结果是坐台小姐'),
('虐渣','闺蜜发亲密照炫耀抢男友，我让她一无所有'),
('虐渣','相亲遇普信男，嫌我工资低，看到我的车吓傻'),
('虐渣','表妹偷我设计稿获奖，我拿出原件让她身败名裂'),
('虐渣','室友偷用化妆品还倒打一耙，监控曝光'),
('虐渣','同事抢我方案获奖，我拿出聊天记录'),
('虐渣','渣男说怀了双胞胎逼我让位，结果是假孕'),
('虐渣','婆婆嫌我不会生，结果查出是儿子不行'),
('虐渣','前男友晒现任多有钱，我晒存款他傻眼'),
('虐渣','小三重生我的孩子，还说我是小三'),
-- 重生 (5+)
('重生','前世被老公和婆婆联手害死，重生到结婚前一天'),
('重生','前世被妹妹害死，重生到她出生那天'),
('重生','前世被合伙人背叛，重生让对方破产'),
('重生','前世被老板压榨猝死，重生告到他破产'),
('重生','前世被养女拔氧气管，重生归来她跪求原谅'),
-- 神医 (5+)
('神医','农村土郎中一眼看出首富得了癌症，被嘲笑'),
('神医','实习医生被科室主任排挤，结果是医道传承人'),
('神医','被所有人嘲笑的赤脚医生，真实身份是国医圣手'),
('神医','穷小子继承祖传医书，成为绝世神医'),
('神医','女护士被开除，结果是隐藏的中医天才'),
-- 系统 (5+)
('系统','高考落榜获得神级选择系统，每次选择都是神级技能'),
('系统','送外卖获得神级厨艺系统，全球名厨拜师'),
('系统','穷小子绑定神级投资系统，小目标一个亿'),
('系统','普通上班族获得神级游戏系统，现实也开挂'),
('系统','被辞退那天获得神级黑客系统，全球我最强')
ON CONFLICT DO NOTHING;
