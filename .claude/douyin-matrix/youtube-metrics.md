# YouTube 數據監控腳本

## API 申請方式

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新項目
3. 啟用 **YouTube Data API v3**
4. 創建 API Key (Credentials)
5. 複製 API Key 到下方 `config.yaml`

## 配置

```yaml
# config.yaml
youtube:
  api_key: "YOUR_YOUTUBE_API_KEY"
  channel_id: "YOUR_CHANNEL_ID"
  
# 可選：多個頻道
channels:
  - id: "UCxxxxx"
    name: "頻道1"
  - id: "UCyyyyy"
    name: "頻道2"
```

## 腳本功能

### 1. 獲取頻道統計
```bash
node youtube-metrics.js --stats
```

返回：
- 訂閱者數
- 總觀看次數
- 視頻數量

### 2. 獲取視頻列表
```bash
node youtube-metrics.js --videos
```

返回：
- 視頻 ID、標題
- 發布日期
- 觀看次數、按讚數
- 評論數

### 3. 獲取實時數據
```bash
node youtube-metrics.js --realtime
```

返回：
- 當前觀看人數
- 今日新增訂閱
- 過去 7 天統計

### 4. 導出為 JSON
```bash
node youtube-metrics.js --export
```

## 完整腳本

```javascript
// youtube-metrics.js
import fs from 'fs';
import https from 'https';
import yaml from 'js-yaml';

// 讀取配置
const config = yaml.load(fs.readFileSync('./config.yaml', 'utf8'));

// YouTube API 請求函數
async function youtubeAPI(endpoint, params = {}) {
  const queryParams = new URLSearchParams({
    ...params,
    key: config.youtube.api_key
  });
  
  const url = `https://www.googleapis.com/youtube/v3/${endpoint}?${queryParams}`;
  
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

// 獲取頻道統計
async function getChannelStats() {
  const response = await youtubeAPI('channels', {
    part: 'statistics,snippet',
    id: config.youtube.channel_id
  });
  
  const channel = response.items[0];
  return {
    channelName: channel.snippet.title,
    subscribers: parseInt(channel.statistics.subscriberCount),
    totalViews: parseInt(channel.statistics.viewCount),
    videoCount: parseInt(channel.statistics.videoCount),
    publishedAt: channel.snippet.publishedAt
  };
}

// 獲取視頻列表
async function getVideos() {
  const response = await youtubeAPI('search', {
    part: 'snippet',
    channelId: config.youtube.channel_id,
    type: 'video',
    order: 'date',
    maxResults: 20
  });
  
  const videoIds = response.items.map(item => item.id.videoId);
  
  // 獲取視頻統計
  const statsResponse = await youtubeAPI('videos', {
    part: 'statistics,contentDetails',
    id: videoIds.join(',')
  });
  
  return response.items.map((item, index) => ({
    videoId: item.id.videoId,
    title: item.snippet.title,
    publishedAt: item.snippet.publishedAt,
    thumbnail: item.snippet.thumbnails?.medium?.url,
    views: parseInt(statsResponse.items[index].statistics.viewCount || 0),
    likes: parseInt(statsResponse.items[index].statistics.likeCount || 0),
    comments: parseInt(statsResponse.items[index].statistics.commentCount || 0)
  }));
}

// 格式化輸出
function formatOutput(data) {
  return JSON.stringify(data, null, 2);
}

// 主函數
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || '--stats';
  
  try {
    let result;
    
    switch (command) {
      case '--stats':
        result = await getChannelStats();
        console.log('📊 頻道統計:');
        console.log(formatOutput(result));
        break;
        
      case '--videos':
        result = await getVideos();
        console.log('📹 視頻列表:');
        console.log(formatOutput(result));
        break;
        
      case '--export':
        const [stats, videos] = await Promise.all([
          getChannelStats(),
          getVideos()
        ]);
        result = { timestamp: new Date().toISOString(), stats, videos };
        
        // 保存到文件
        const filename = `youtube_data_${Date.now()}.json`;
        fs.writeFileSync(filename, formatOutput(result));
        console.log(`✅ 數據已導出至 ${filename}`);
        break;
        
      default:
        console.log('未知命令，可用: --stats, --videos, --export');
    }
  } catch (error) {
    console.error('❌ 錯誤:', error.message);
  }
}

main();
```

## Cron 自動化

```bash
# 每小時抓取一次
0 * * * * cd /path/to/douyin-matrix && node youtube-metrics.js --export >> logs/youtube_cron.log 2>&1
```

## 依賴安裝

```bash
npm install js-yaml
```
