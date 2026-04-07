# YouTube OAuth 設置指南（5分鐘完成）

**這是唯一阻礙全自動上傳的步驟。完成後，未來所有上傳都自動完成。**

---

## 步驟 1：打開 Google Cloud Console

在瀏覽器訪問：
```
https://console.cloud.google.com
```

---

## 步驟 2：新建項目

1. 點擊右上角「選擇項目」
2. 點擊「新建項目」
3. 項目名稱填：`anime-ops`
4. 位置選「無組織」
5. 點擊「創建」

---

## 步驟 3：啟用 YouTube API

1. 左側菜單：點「API和服務」→「啟用 API 和服務」
2. 搜索框輸入：`YouTube Data API v3`
3. 點擊結果 → 點「啟用」

---

## 步驟 4：創建 OAuth 憑證

1. 左側：點「憑證」→「+ 創建憑證」→「OAuth 用戶端 ID」
2. 應用程式類型：選擇「桌面應用」
3. 名稱填：`anime-ops`
4. 點擊「創建」

---

## 步驟 5：下載並放置文件

1. 看到「您的 OAuth 用戶端」彈窗，點擊「下載 JSON」
2. 把下載的文件**改名**為：`client_secrets.json`
3. 把這個文件移動到：
   ```
   D:\claude mini max 2.7\anime_overseas\client_secrets.json
   ```

---

## 步驟 6：完成！測試連接

回來告訴我，我運行測試：

```bash
cd d:\claude mini max 2.7\anime_overseas
python youtube_auto_uploader.py --auth-only
```

---

## 完成後的效果

```
✅ 運行 python agent.py upload
✅ 自動登入你的 YouTube 頻道
✅ 自動填寫標題/描述/標籤
✅ 自動選擇封面
✅ 自動發布
✅ 完全不需要你動手
```

---

## 聯絡窗口（所有對外溝通用）

- **Email**: scott365888@gmail.com
- **微信**: PTS9800
