# 🎬 漫剧出海AI变现系统

> Windows版 | 零成本 | 自动化运营

---

## 📁 项目结构

```
manhua-system/
├── scripts/
│   ├── manager.js      # 内容管理器
│   ├── generator.js   # 内容生成器
│   ├── exporter.js    # 导出工具
│   └── merge.js       # 合并脚本
├── content/
│   ├── batch_60_sets_part1.json  # 内容库1
│   └── batch_60_sets_part2.json  # 内容库2
├── output/
│   ├── pending/       # 待发布
│   └── published/     # 已发布
├── n8n/
│   └── manhua-workflow.json  # n8n工作流
├── run.bat           # Windows启动脚本
└── README.md         # 说明文档
```

---

## 🚀 快速开始

### 方法1：使用图形界面

```batch
双击 run.bat
```

### 方法2：命令行运行

```batch
cd manhua-system
node scripts/manager.js stats
node scripts/manager.js schedule
```

---

## 📋 功能列表

| 功能 | 命令 | 说明 |
|------|------|------|
| 生成内容 | `node scripts/generator.js` | 生成60套内容 |
| 查看统计 | `node scripts/manager.js stats` | 查看内容统计 |
| 发布计划 | `node scripts/manager.js schedule` | 生成7天计划 |
| 提醒脚本 | `node scripts/manager.js reminder` | 生成Windows提醒 |
| 导出CSV | `node scripts/exporter.js csv` | 导出CSV |
| 导出MD | `node scripts/exporter.js md` | 导出Markdown |
| 列出内容 | `node scripts/manager.js list` | 列出所有内容 |

---

## 📊 内容统计

| 题材 | 数量 |
|------|------|
| 🐉 龙王 | 10套 |
| 💪 逆袭 | 10套 |
| 🔥 虐渣 | 10套 |
| ⚡ 重生 | 10套 |
| 🩺 神医 | 10套 |
| 🎮 系统 | 10套 |
| **总计** | **60套** |

---

## 💰 变现流程

```
1. 内容 → 2. 制作视频 → 3. 发布TikTok → 4. 引导付费 → 5. 收款
```

### 付费平台

| 平台 | 网址 | 费用 |
|------|------|------|
| Linktree | linktr.ee | 免费 |
| Gumroad | gumroad.com | 免费 |
| BuyMeACoffee | buymyacoffee.com | 免费 |

---

## 🔧 运行环境

- Node.js 16+
- Windows 10/11
- 免费工具：无

---

## 📞 帮助

有问题？请说"帮助"或"help"
