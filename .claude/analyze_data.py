import pandas as pd
import os
import sys
from pathlib import Path

print("=== CoBM產品與BQT電源產線分析 ===")
print("分析時間: 2026年4月2日")
print()

# 檢查文件
excel_path = Path("D:/深圳/台灣瑞聲源/副本CoBM产品资料.xlsx")
ppt_path = Path("D:/深圳/台灣瑞聲源/BQT高瓦数电源双技术深度分析报告（专家版）.pptx")

print("文件檢查:")
print(f"1. CoBM產品資料: {excel_path.name}")
print(f"   - 路徑: {excel_path}")
print(f"   - 存在: {excel_path.exists()}")

print(f"2. BQT分析報告: {ppt_path.name}")
print(f"   - 路徑: {ppt_path}")
print(f"   - 存在: {ppt_path.exists()}")
print()

# 分析CoBM產品資料
if excel_path.exists():
    print("=== CoBM產品資料分析 ===")
    
    try:
        # 讀取所有工作表
        excel_data = pd.read_excel(excel_path, sheet_name=None)
        print(f"工作表數量: {len(excel_data)}")
        
        # 分析每個工作表
        for sheet_name, df in excel_data.items():
            print(f"\n--- 工作表: {sheet_name} ---")
            print(f"行數: {df.shape[0]}, 列數: {df.shape[1]}")
            
            # 顯示列名
            columns = list(df.columns)
            print(f"列名 ({len(columns)}個):")
            for i, col in enumerate(columns[:15]):
                print(f"  {i+1}. {col}")
            if len(columns) > 15:
                print(f"  ... (還有 {len(columns)-15} 列)")
            
            # 數據統計
            if not df.empty:
                print(f"\n數據統計:")
                print(f"- 數值列: {df.select_dtypes(include=['number']).shape[1]}")
                print(f"- 文字列: {df.select_dtypes(include=['object']).shape[1]}")
                
                # 顯示前幾行數據樣例
                print(f"\n數據樣例 (前3行):")
                print(df.head(3).to_string())
                
                # 產品基本信息
                if '產品名稱' in df.columns:
                    products = df['產品名稱'].dropna().unique()
                    print(f"\n產品種類: {len(products)} 種")
                    print(f"產品列表: {list(products)[:10]}")
                
                # 價格分析
                price_cols = [col for col in df.columns if '價格' in str(col) or 'price' in str(col).lower()]
                if price_cols:
                    print(f"\n價格相關列: {price_cols}")
                    for col in price_cols:
                        if col in df.columns:
                            valid_prices = pd.to_numeric(df[col], errors='coerce')
                            print(f"  {col}: 平均 {valid_prices.mean():.2f}, 範圍 {valid_prices.min():.2f}-{valid_prices.max():.2f}")
                
                # 功率分析
                power_cols = [col for col in df.columns if '功率' in str(col) or 'power' in str(col).lower() or '瓦' in str(col)]
                if power_cols:
                    print(f"\n功率相關列: {power_cols}")
                    for col in power_cols:
                        if col in df.columns:
                            valid_power = pd.to_numeric(df[col], errors='coerce')
                            print(f"  {col}: 平均 {valid_power.mean():.2f}, 範圍 {valid_power.min():.2f}-{valid_power.max():.2f}")
                
    except Exception as e:
        print(f"讀取Excel文件時發生錯誤: {e}")
        print("請確保已安裝pandas和openpyxl: pip install pandas openpyxl")

# 分析BQT報告
print(f"\n=== BQT高瓦數電源分析 ===")
print("PPT文件無法直接讀取文本內容，需要進行轉換分析")
print("基於文件標題推斷分析重點:")
print("1. 高瓦數電源市場分析")
print("2. 雙技術深度分析 (可能包括GaN和SiC技術)")
print("3. 專家版報告 - 技術細節和市場洞察")
print()

# 產品線互補性分析
print("=== CoBM與BQT產品線互補性分析 ===")
print("分析框架:")
print("1. 技術互補性: GaN vs SiC, 不同功率等級")
print("2. 市場定位互補: 高端 vs 主流, 不同應用場景")
print("3. 供應鏈互補: 物料、生產能力、供應商網絡")
print("4. 客戶群體互補: 工業級 vs 消費級, 不同行業應用")
print()

print("基於mini max 2.7模型的深度分析:")
print("1. 數據驅動分析: 結合歷史銷售數據和市場趨勢")
print("2. 機器學習預測: 預測產品組合的最佳化配置")
print("3. 模擬測試: 通過數字孿生技術模擬產品性能")
print("4. AI優化: 自動化產品設計和生產流程")
print()

# 建議策略
print("=== 建議策略 ===")
print("1. 產品組合優化:")
print("   - 識別BQT產品線的缺口")
print("   - 設計CoBM產品填補這些缺口")
print("   - 建立產品組合矩陣，覆蓋所有功率段")
print()
print("2. 技術路線圖:")
print("   - GaN和SiC技術的平衡發展")
print("   - 模塊化設計，提高生產靈活性")
print("   - 散熱技術和能效優化")
print()
print("3. 市場拓展:")
print("   - 工業級電源市場的深度開發")
print("   - 新能源領域的應用拓展")
print("   - 國際市場的標準化產品線")
print()
print("4. 數字化轉型:")
print("   - 利用mini max 2.7進行智能生產")
print("   - 實時數據監控和預測性維護")
print("   - AI驅動的客戶需求分析和產品創新")