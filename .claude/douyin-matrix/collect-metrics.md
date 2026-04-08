# 自動化數據監控腳本

## 功能說明

自動從 YouTube 和 TikTok 抓取數據，並寫入飛書表格。

## 配置

```yaml
# config.yaml
feishu:
  spreadsheet_token: "J3yCsmJRhhTQTntGNA2cuTFGnVf"
  sheet_id: "0"  # 第一個工作表

youtube:
  api_key: "YOUR_YOUTUBE_API_KEY"
  channel_id: "YOUR_CHANNEL_ID"

tiktok:
  client_key: "YOUR_TIKTOK_CLIENT_KEY"
  client_secret: "YOUR_TIKTOK_CLIENT_SECRET"
  access_token: "YOUR_ACCESS_TOKEN"
```

## 使用方式

```bash
# 立即執行一次數據抓取
node collect-metrics.js

# 持續監控（每小時自動抓取）
npm run monitor
```

## Cron 任務設定

```bash
# 每小時抓取一次
0 * * * * cd /path/to/douyin-matrix && node collect-metrics.js >> logs/metrics.log 2>&1
```

## 整合腳本

```javascript
// collect-metrics.js
import fs from 'fs';
import https from 'https';
import yaml from 'js-yaml';

// 讀取配置
let config;
try {
  config = yaml.load(fs.readFileSync('./config.yaml', 'utf8'));
} catch (e) {
  console.log('⚠️ 請先配置 config.yaml');
  process.exit(1);
}

// ============ YouTube API ============
async function getYouTubeData() {
  // 實現見 youtube-metrics.md
  // 返回格式: { views, likes, comments, shares }
}

// ============ TikTok API ============
async function getTikTokData() {
  // 實現見 tiktok-metrics.md
  // 返回格式: { views, likes, comments, shares }
}

// ============ 飛書寫入 ============
async function writeToFeishu(data) {
  const timestamp = new Date().toLocaleString('zh-TW', { 
    timeZone: 'Asia/Taipei',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });

  const row = [
    timestamp,
    data.platform,
    data.views.toString(),
    data.likes.toString(),
    data.shares.toString(),
    data.ctaClicks.toString(),
    data.note || ''
  ];

  // 調用飛書 API 追加行
  const response = await fetch(`https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/${config.feishu.spreadsheet_token}/values`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.feishu.access_token}`
    },
    body: JSON.stringify({
      valueRange: {
        range: `${config.feishu.sheet_id}!A${getNextRow()}:G${getNextRow()}`,
        values: [row]
      }
    })
  });

  return response.json();
}

// ============ 主函數 ============
async function main() {
  console.log('📊 開始抓取數據...');
  
  const results = [];
  
  // 抓取 YouTube
  try {
    const ytData = await getYouTubeData();
    results.push({ platform: 'YouTube', ...ytData });
    console.log(`✅ YouTube: ${ytData.views} 播放`);
  } catch (e) {
    console.log(`❌ YouTube: ${e.message}`);
  }
  
  // 抓取 TikTok
  try {
    const ttData = await getTikTokData();
    results.push({ platform: 'TikTok', ...ttData });
    console.log(`✅ TikTok: ${ttData.views} 播放`);
  } catch (e) {
    console.log(`❌ TikTok: ${e.message}`);
  }
  
  // 寫入飛書
  for (const data of results) {
    try {
      await writeToFeishu(data);
      console.log(`✅ 已寫入飛書: ${data.platform}`);
    } catch (e) {
      console.log(`❌ 飛書寫入失敗: ${e.message}`);
    }
  }
  
  console.log('📊 數據抓取完成!');
}

main();
```

## 查看數據

打開飛書表格查看數據：
https://mcnfdtq58j2s.feishu.cn/sheets/J3yCsmJRhhTQTntGNA2cuTFGnVf

## 下一步

1. 填入你的 YouTube API Key
2. 填入你的 TikTok Access Token
3. 運行 `node collect-metrics.js` 測試
