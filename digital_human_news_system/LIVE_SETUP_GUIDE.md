# AI數字人直播完整配置指南

## 第一步：抖音推流地址獲取

### 1.1 電腦端抖音直播
1. 打開抖音創作服務平台: https://creator.douyin.com/
2. 登錄你的抖音帳號
3. 點擊「直播間管理」
4. 點擊「電腦直播」
5. 複製「推流地址」

### 1.2 將推流地址填入配置
```
打開: config/live_config.json

找到:
"douyin": {
    "stream_server": "rtmp://push.toutiao.com/live",
    "stream_key": "填入你的stream key"
}

stream_key = 推流地址中 /live/ 後面的部分
例如: rtmp://push.toutiao.com/live/xxxx-xxxx-xxxx
stream_key = xxxx-xxxx-xxxx
```

---

## 第二步：下載安裝OBS

### 2.1 下載OBS
- 官網: https://obsproject.com/
- 選擇Windows版本下載

### 2.2 一鍵安裝腳本
```bash
# 以管理員身份運行以下命令
winget install OBSProject.OBSStudio
# 或
choco install obs-studio -y
```

### 2.3 OBS基本設置
1. **設置解析度**: 設置 → 通用 → 設置解析度 1920x1080
2. **設置語言**: 設置 → 一般 → 語言 → 繁體中文
3. **關閉自動推流**: 設置 → 推流 → 取消勾選「自動推流」

---

## 第三步：數字人視頻生成

### 3.1 運行腳本生成預渲染視頻
```bash
cd "d:\claude mini max 2.7\digital_human_news_system"

# 生成一批直播用視頻
python generate_live_videos.py
```

### 3.2 視頻生成腳本
