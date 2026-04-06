import pandas as pd
import os

# 讀取Excel文件
excel_path = 'D:/深圳/台灣瑞聲源/副本CoBM产品资料.xlsx'
print(f"文件路徑: {excel_path}")
print(f"文件是否存在: {os.path.exists(excel_path)}")

# 讀取所有工作表
data = pd.read_excel(excel_path, sheet_name=None)

# 顯示工作表信息
print(f"\n=== Excel文件分析 ===")
print(f"工作表數量: {len(data)}")

for sheet_name, df in data.items():
    print(f"\n--- 工作表: {sheet_name} ---")
    print(f"形狀: {df.shape} (行數: {df.shape[0]}, 列數: {df.shape[1]})")
    
    # 顯示列名
    print(f"列名: {list(df.columns)}")
    
    # 顯示前幾行數據
    if len(df) > 0:
        print("\n前5行數據:")
        print(df.head().to_string())
    
    # 數據類型
    print(f"\n數據類型:")
    print(df.dtypes.head(10))
    
    # 缺失值統計
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        print(f"\n缺失值統計:")
        print(missing_values[missing_values > 0])

print(f"\n=== 文件讀取完成 ===")