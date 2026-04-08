# TikTok 數據監控腳本

## API 申請方式

### TikTok 企業號 API (免費)

1. 前往 [TikTok for Developers](https://developers.tiktok.com/)
2. 登入 TikTok 帳號
3. 創建應用 (Create App)
4. 選擇 "企業號" 類型
5. 申請權限：
   - `video.list` - 視頻列表
   - `video.data` - 視頻數據
   - `user.info.basic` - 用戶基本信息
6. 等待審核 (3-5 個工作日)

### 獲取 Access Token

```bash
# OAuth 2.0 授權流程
https://open.tiktokapis.com/v2/oauth/authorize/
  ?client_key=YOUR_CLIENT_KEY
  &response_type=code
  &scope=video.list,video.data,user.info.basic
  &redirect_uri=YOUR_REDIRECT_URI
```

## 配置

```yaml
# config.yaml
tiktok:
  client_key: "YOUR_CLIENT_KEY"
  client_secret: "YOUR_CLIENT_SECRET"
  access_token: "YOUR_ACCESS_TOKEN"
  open_id: "USER_OPEN_ID"
```

## 腳本功能

### 1. 獲取視頻列表
```bash
node tiktok-metrics.js --videos
```

返回：
- 視頻 ID、標題
- 發布日期
- 觀看次數、按讚數
- 分享數、評論數

### 2. 獲取視頻詳情
```bash
node tiktok-metrics.js --video VIDEO_ID
```

### 3. 獲取用戶信息
```bash
node tiktok-metrics.js --user
```

### 4. 導出為 JSON
```bash
node tiktok-metrics.js --export
```

## 完整腳本

```javascript
// tiktok-metrics.js
import fs from 'fs';
import https from 'https';
import yaml from 'js-yaml';
import crypto from 'crypto';

// 讀取配置
let config;
try {
  config = yaml.load(fs.readFileSync('./config.yaml', 'utf8'));
} catch (e) {
  console.log('⚠️ 請先配置 config.yaml');
  process.exit(1);
}

// TikTok API 請求函數
async function tiktokAPI(endpoint, method = 'GET', body = null) {
  const options = {
    hostname: 'open.tiktokapis.com',
    path: `/v2/${endpoint}`,
    method: method,
    headers: {
      'Authorization': `Bearer ${config.tiktok.access_token}`,
      'Content-Type': 'application/json'
    }
  };
  
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) {
            reject(new Error(parsed.error.message));
          } else {
            resolve(parsed);
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    
    if (body) {
      req.write(JSON.stringify(body));
    }
    
    req.end();
  });
}

// 獲取視頻列表
async function getVideos() {
  const response = await tiktokAPI('video/list/', 'POST', {
    "max_count": 20,
    "fields": [
      "id",
      "title",
      "create_time",
      "cover_image_url",
      "share_url",
      "video_description",
      "like_count",
      "comment_count",
      "share_count",
      "view_count"
    ]
  });
  
  return response.data?.videos || [];
}

// 獲取視頻詳情
async function getVideoDetail(videoId) {
  const response = await tiktokAPI('video/', 'POST', {
    "video_ids": [videoId],
    "fields": [
      "id",
      "title",
      "create_time",
      "cover_image_url",
      "share_url",
      "video_description",
      "like_count",
      "comment_count",
      "share_count",
      "view_count"
    ]
  });
  
  return response.data?.videos?.[0] || null;
}

// 獲取用戶信息
async function getUserInfo() {
  const response = await tiktokAPI('user/info/', 'GET');
  return response.data || {};
}

// 格式化輸出
function formatOutput(data) {
  return JSON.stringify(data, null, 2);
}

// 主函數
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || '--user';
  
  try {
    let result;
    
    switch (command) {
      case '--videos':
        result = await getVideos();
        console.log('📹 TikTok 視頻列表:');
        console.log(formatOutput(result));
        break;
        
      case '--video':
        const videoId = args[1];
        if (!videoId) {
          console.log('❌ 請提供視頻 ID');
          process.exit(1);
        }
        result = await getVideoDetail(videoId);
        console.log('🎬 視頻詳情:');
        console.log(formatOutput(result));
        break;
        
      case '--user':
        result = await getUserInfo();
        console.log('👤 TikTok 用戶信息:');
        console.log(formatOutput(result));
        break;
        
      case '--export':
        const [user, videos] = await Promise.all([
          getUserInfo(),
          getVideos()
        ]);
        result = { 
          timestamp: new Date().toISOString(), 
          user, 
          videos,
          summary: {
            totalVideos: videos.length,
            totalViews: videos.reduce((sum, v) => sum + (v.view_count || 0), 0),
            totalLikes: videos.reduce((sum, v) => sum + (v.like_count || 0), 0),
            totalComments: videos.reduce((sum, v) => sum + (v.comment_count || 0), 0),
            totalShares: videos.reduce((sum, v) => sum + (v.share_count || 0), 0)
          }
        };
        
        // 保存到文件
        const filename = `tiktok_data_${Date.now()}.json`;
        fs.writeFileSync(filename, formatOutput(result));
        console.log(`✅ 數據已導出至 ${filename}`);
        break;
        
      default:
        console.log('未知命令，可用: --videos, --video [ID], --user, --export');
    }
  } catch (error) {
    console.error('❌ 錯誤:', error.message);
  }
}

main();
```

## 模擬數據模式 (無 API Key)

如果還沒有 TikTok API Key，可以使用模擬數據模式：

```javascript
// 模擬 TikTok API 響應
function getMockTikTokData() {
  return {
    timestamp: new Date().toISOString(),
    user: {
      open_id: "mock_user_123",
      display_name: "測試用戶",
      avatar_url: "https://example.com/avatar.jpg",
      follower_count: Math.floor(Math.random() * 50000) + 10000,
      following_count: Math.floor(Math.random() * 500) + 100,
      likes_count: Math.floor(Math.random() * 100000) + 50000
    },
    videos: [
      {
        id: "mock_video_1",
        title: "測試視頻 1",
        create_time: new Date(Date.now() - 86400000).toISOString(),
        view_count: Math.floor(Math.random() * 50000) + 10000,
        like_count: Math.floor(Math.random() * 5000) + 1000,
        comment_count: Math.floor(Math.random() * 500) + 100,
        share_count: Math.floor(Math.random() * 200) + 50
      },
      // ... 更多視頻
    ]
  };
}
```

## Cron 自動化

```bash
# 每小時抓取一次
0 * * * * cd /path/to/douyin-matrix && node tiktok-metrics.js --export >> logs/tiktok_cron.log 2>&1
```

## 依賴安裝

```bash
npm install js-yaml
```

## 注意事項

1. **API 限流**: TikTok API 有 Rate Limit，免費版每分鐘 100 請求
2. **Token 刷新**: Access Token 有效期約 24 小時，需要定期刷新
3. **企業號要求**: 部分高級數據需要 TikTok 企業號才能訪問
