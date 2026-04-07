# -*- coding: utf-8 -*-
"""
Excel 讀取器 - 讀取和分析 Excel 數據
支援：.xlsx, .xls, .csv
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime


class ExcelReader:
    """Excel 讀取器"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.extension = os.path.splitext(file_path)[1].lower()
        self.data = None
        self.metadata = {}

    def read(self, sheet_name=None, header=0):
        """讀取 Excel/CSV 文件"""
        try:
            if self.extension == '.csv':
                self.data = pd.read_csv(self.file_path, encoding='utf-8-sig')
            elif self.extension in ['.xlsx', '.xls']:
                if sheet_name:
                    self.data = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl' if self.extension == '.xlsx' else None)
                else:
                    # 讀取所有工作表
                    self.data = pd.read_excel(self.file_path, sheet_name=None, engine='openpyxl' if self.extension == '.xlsx' else None)
            else:
                raise ValueError(f"Unsupported file format: {self.extension}")

            self._extract_metadata()
            return self.data

        except Exception as e:
            print(f"[ERROR] Failed to read file: {e}")
            return None

    def _extract_metadata(self):
        """提取元數據"""
        if isinstance(self.data, dict):
            # 多個工作表
            self.metadata = {
                "file": self.file_path,
                "sheets": list(self.data.keys()),
                "sheet_count": len(self.data),
                "read_at": datetime.now().isoformat()
            }
        elif isinstance(self.data, pd.DataFrame):
            self.metadata = {
                "file": self.file_path,
                "rows": len(self.data),
                "columns": len(self.data.columns),
                "column_names": list(self.data.columns),
                "dtypes": {str(k): str(v) for k, v in self.data.dtypes.items()},
                "read_at": datetime.now().isoformat()
            }

    def to_json(self, output_path=None):
        """導出為 JSON"""
        if self.data is None:
            return None

        if isinstance(self.data, dict):
            result = {}
            for sheet_name, df in self.data.items():
                result[sheet_name] = {
                    "columns": list(df.columns),
                    "rows": len(df),
                    "data": df.fillna("").to_dict(orient='records')
                }
        else:
            result = {
                "metadata": self.metadata,
                "data": self.data.fillna("").to_dict(orient='records')
            }

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            print(f"[OK] JSON saved: {output_path}")

        return result

    def to_csv(self, output_path=None, sheet_name=None):
        """導出為 CSV"""
        if self.data is None:
            return None

        if isinstance(self.data, dict):
            if sheet_name and sheet_name in self.data:
                df = self.data[sheet_name]
            else:
                df = self.data[list(self.data.keys())[0]]
        else:
            df = self.data

        if output_path:
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"[OK] CSV saved: {output_path}")

        return df

    def summary(self):
        """生成摘要"""
        if self.data is None:
            return "No data loaded"

        summary = []
        summary.append("=" * 50)
        summary.append("Excel Data Summary")
        summary.append("=" * 50)
        summary.append(f"File: {os.path.basename(self.file_path)}")
        summary.append(f"Type: {self.extension}")

        if isinstance(self.data, dict):
            summary.append(f"Sheets: {len(self.data)}")
            for name, df in self.data.items():
                summary.append(f"\n[{name}]")
                summary.append(f"  Rows: {len(df)}")
                summary.append(f"  Columns: {len(df.columns)}")
                summary.append(f"  Headers: {', '.join(list(df.columns)[:5])}...")
        else:
            summary.append(f"Rows: {len(self.data)}")
            summary.append(f"Columns: {len(self.data.columns)}")
            summary.append(f"\nColumn Names:")
            for col in self.data.columns:
                summary.append(f"  - {col} ({self.data[col].dtype})")

        return "\n".join(summary)

    def print_summary(self):
        """打印摘要"""
        print(self.summary())

    def get_column_stats(self, column_name):
        """獲取列統計"""
        if self.data is None or isinstance(self.data, dict):
            return None

        if column_name not in self.data.columns:
            return None

        col = self.data[column_name]

        if pd.api.types.is_numeric_dtype(col):
            return {
                "column": column_name,
                "type": "numeric",
                "count": int(col.count()),
                "mean": float(col.mean()),
                "std": float(col.std()),
                "min": float(col.min()),
                "max": float(col.max()),
                "sum": float(col.sum())
            }
        else:
            return {
                "column": column_name,
                "type": "text",
                "count": int(col.count()),
                "unique": int(col.nunique()),
                "top_values": col.value_counts().head(5).to_dict()
            }


def read_excel_file(file_path, output_json=None, output_csv=None):
    """快速讀取函數"""
    reader = ExcelReader(file_path)
    data = reader.read()

    if data is None:
        print(f"[ERROR] Failed to read: {file_path}")
        return None

    reader.print_summary()

    if output_json:
        reader.to_json(output_json)

    if output_csv:
        reader.to_csv(output_csv)

    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python excel_reader.py <file.xlsx> [output_json] [output_csv]")
        print("")
        print("Examples:")
        print("  python excel_reader.py data.xlsx")
        print("  python excel_reader.py data.xlsx result.json")
        print("  python excel_reader.py data.csv result.json result.csv")
        sys.exit(1)

    file_path = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    output_csv = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    read_excel_file(file_path, output_json, output_csv)
