# 全球 DIY PC 電源品牌 關鍵人聯絡收集

## 任務目標
收集 PSU (Power Supply Unit) 品牌商的 RD/PM/採購 關鍵聯絡人資訊

---

## 目標品牌清單

### 一線國際品牌

| # | 品牌 | 公司 | 國家 | 官網 | 備註 |
|---|------|------|------|------|------|
| 1 | Corsair | Corsair Components | 美國 | corsair.com | 那斯達克上市 |
| 2 | Seasonic | 海韻電子 | 台灣 | seasonic.com | 40年歷史，旗艦代工 |
| 3 | be quiet! | be quiet! GmbH | 德國 | be-quiet.com | 歐洲第一靜音品牌 |
| 4 | EVGA | EVGA Corporation | 美國 | evga.com | NVIDIA嫡系 |
| 5 | Thermaltake | 曜越科技 | 台灣 | thermaltake.com | 上市櫃公司 |
| 6 | Cooler Master | 酷碼科技 | 台灣 | coolermaster.com | 全球最大散熱廠 |
| 7 | ASUS ROG | 華碩電腦 | 台灣 | asus.com/rog | 子公司 |
| 8 | MSI | 微星科技 | 台灣 | msi.com | 上市櫃公司 |

### 中高端品牌

| # | 品牌 | 公司 | 國家 | 官網 | 備註 |
|---|------|------|------|------|------|
| 9 | Super Flower | 振華電子的 | 台灣 | super-flower.com.tw | 領導品牌 |
| 10 | FSP | 全漢實業 | 台灣 | fspsp.com | 上市櫃公司 |
| 11 | Silverstone | 銀欣科技 | 台灣 | silverstonetek.com | 迷你ITX專家 |
| 12 | Enermax | 保銳科技 | 台灣 | enermax.com | 電競專精 |
| 13 | Phanteks | Phanteks B.V. | 荷蘭 | phanteks.com | 高端玩家 |

### 中國品牌

| # | 品牌 | 公司 | 國家 | 官網 | 備註 |
|---|------|------|------|------|------|
| 14 | Great Wall | 長城電源 | 中國 | greatwall.com | 聯想供應商 |
| 15 | Huntkey | 航嘉馳源 | 中國 | huntkey.com | 大陸領導品牌 |
| 16 | Delta | 台達電子 | 台灣/中國 | delta.com.tw | 全球電源龍頭 |
| 17 | Chicony | 群光電子 | 台灣 | chicony.com | 多品牌代工 |
| 18 | Cougar | 脈衝電競 | 德國/台灣 | cougar-gaming.com | 電競品牌 |

---

## 聯絡人收集模板

請按以下格式填寫每個品牌的聯絡人：

### 模板格式 (JSON)

```json
{
  "brand": "品牌名稱",
  "company": "公司名稱",
  "country": "國家",
  "contacts": [
    {
      "name": "姓名（已知填寫，不知留空）",
      "title": "職位",
      "department": "部門",
      "contact_type": "RD | PM | Purchasing | General",
      "linkedin": "LinkedIn URL",
      "email": "email@example.com",
      "source": "官網 | LinkedIn | 新聞稿 | Computex | 展會名片 | 其他",
      "last_verified": "YYYY-MM-DD",
      "notes": "備註"
    }
  ],
  "company_info": {
    "headquarters": "總部地址",
    "employee_count": "員工人數",
    "revenue": "年營收",
    "established": "成立年份"
  },
  "social_media": {
    "linkedin": "公司LinkedIn",
    "facebook": "公司Facebook",
    "twitter": "公司Twitter"
  },
  "research_status": "待收集 | 收集中 | 已完成",
  "researcher": "負責人",
  "research_date": "YYYY-MM-DD"
}
```

### 職位關鍵詞參考

**RD/研發:**
- VP of Engineering / 工程副總
- Director of R&D / 研發總監
- Hardware Engineering Manager / 硬體工程經理
- Power Supply Engineer / 電源工程師
- Senior RD Engineer / 高級研發工程師

**PM/產品:**
- Product Manager / 產品經理
- Senior Product Manager / 高級產品經理
- Director of Product Management / 產品總監
- Product Marketing Manager / 產品行銷經理
- Business Development Manager / 業務開發經理

**採購/供應鏈:**
- Procurement Manager / 採購經理
- Supply Chain Manager / 供應鏈經理
- Purchasing Director / 採購總監
- Supplier Quality Engineer / 供應商品質工程師
- Sourcing Manager / 採購開發經理

---

## 研究來源

### 1. 公司官網
- 團隊/關於我們頁面
- 新聞稿/媒體中心
- 投資者關係

### 2. LinkedIn
- 公司頁面 → 員工
- 搜尋關鍵詞: `site:linkedin.com/in "Power Supply" + "品牌名"`
- 搜尋關鍵詞: `site:linkedin.com/in "PSU" + "公司名"`

### 3. 展會
- Computex Taipei (台灣)
- CES Las Vegas (美國)
- IFA Berlin (德國)

### 4. 新聞稿
- PR Newswire
- Business Wire
- 公司官網新聞室

---

## 輸出檔案

請將收集結果保存為:
- `psu_contacts/[品牌]_contacts.json`
- `psu_contacts/all_contacts.json` (合併)

---

## 備注

- 請定期更新，最少每季度驗證一次
- 優先收集有 LinkedIn 的專業人士
- 採購部門通常在供應商評估季節較活躍
- RD 在新產品發布期間較容易聯繫
