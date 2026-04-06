import pandas as pd
import os

file_path = r'D:\深圳\台灣瑞聲源\副本CoBM产品资料.xlsx'
print(f"File exists: {os.path.exists(file_path)}")

xl = pd.ExcelFile(file_path)
print('Sheets:', xl.sheet_names)

for sheet in xl.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    print(f'\n=== {sheet} ===')
    print(f'Shape: {df.shape}')
    print('Columns:', list(df.columns))
    print(df.to_string())