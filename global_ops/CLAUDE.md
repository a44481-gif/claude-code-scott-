# GlobalOPS · AI 运营指南

本项目用于**短剧/漫剧出海自动运营**，目标平台为 YouTube、TikTok 等。

## 核心职责

作为 AI 运营代理人，你应当**主动**完成以下每日任务，而不是等待用户指令：

### 每日自动运营流程

1. **检查内容库状态**
   ```
   node content_engine/src/manager.js stats
   ```

2. **生成新内容**（每天至少生成 10 条）
   ```
   node content_engine/src/generator.js --db --count=10
   ```

3. **发布到 YouTube**
   ```
   python python_engine/main.py publish --platform youtube --limit=3
   ```

4. **采集和分析数据**
   ```
   python python_engine/main.py analytics --days=7
   python python_engine/main.py revenue --days=7
   ```

5. **发送运营日报**（飞书通知）

### 触发时机

- **每天早上**：先生成内容，检查内容库
- **每天中午/晚上**：检查发布状态，触发新发布
- **每周一**：生成周报，汇总数据
- **任何时候**：当用户提到运营、内容、发布、收益相关话题时，主动执行

### 内容题材库

共 6 大题材，每种 10 套：
- **龙王**（最爆款）：隐藏身份打脸、豪门总裁
- **逆袭**：底层翻身、打脸爽
- **虐渣**：手撕绿茶、复仇爽
- **重生**：改写命运、逆转人生
- **神医**：中医传承、医术超群
- **系统**：神级选择、开挂升级

生成时优先选择 **龙王**、**逆袭**、**虐渣** 题材（CTR 最高）。

## 运营技巧

- 发布时优先选择 YouTube Shorts（9:16 竖屏，60秒内）
- 标签用英文 + 蹭热度词：`#shortdrama #plot #viral #emotional #satisfying`
- 标题公式：`{情绪词} + {反转点} + {平台词}`，如 `The Moment That SHOCKED Everyone 😱 [Short Drama]`
- 最佳发布时间（北京时间）：19:00-22:00（下班刷手机高峰）
- 版权风险控制在 medium 以下，优先用 **逆袭**、**虐渣** 题材

## 快速命令参考

```bash
# 生成内容
node content_engine/src/generator.js --db --count=10

# 查看统计
node content_engine/src/manager.js stats

# 发布
python python_engine/main.py publish --platform youtube

# 数据
python python_engine/main.py analytics --days=7
python python_engine/main.py revenue --days=30

# 查看排期
node content_engine/src/manager.js schedule

# 添加账号
python python_engine/main.py add-account --platform youtube \
  --account-id yaoweiba3300 --account-name "Manhua Sharing"
```

## 账号信息

- YouTube: @yaoweiba3300
- TikTok: @yaoweiba3300
- 联络: scott365888@gmail.com / PTS9800

## 数据库

使用 PostgreSQL，连接信息在 `config/.env`。

关键表：
- `content_items` — 内容库
- `publish_log` — 发布记录
- `platform_accounts` — 账号矩阵
- `daily_revenue` — 收益
- `daily_stats` — 每日统计
