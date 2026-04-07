# -*- coding: utf-8 -*-
"""
一鍵自動化報告生成器
輸入：PPT、Excel、JSON
輸出：完整的市場分析報告（PDF + PPT + 圖表）
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


class AutoReportGenerator:
    """自動化報告生成器"""

    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.skills_dir = self.base_dir / ".claude" / "skills"
        self.output_dir = self.base_dir / "reports"
        self.output_dir.mkdir(exist_ok=True)

        self.steps = []
        self.results = {}

    def log(self, message, status="INFO"):
        """日誌記錄"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] [{status}] {message}"
        print(log_msg)
        self.steps.append(log_msg)

    def step(self, name, func, *args, **kwargs):
        """執行步驟"""
        self.log(f"Starting: {name}")
        try:
            result = func(*args, **kwargs)
            self.results[name] = {"status": "success", "result": result}
            self.log(f"Completed: {name}", "OK")
            return result
        except Exception as e:
            self.log(f"Failed: {name} - {e}", "ERROR")
            self.results[name] = {"status": "error", "error": str(e)}
            return None

    def detect_data_source(self, input_path):
        """檢測數據源"""
        ext = Path(input_path).suffix.lower()
        if ext == '.pptx':
            return 'pptx'
        elif ext in ['.xlsx', '.xls', '.csv']:
            return 'excel'
        elif ext == '.json':
            return 'json'
        return 'unknown'

    def run_ppt_analysis(self, pptx_path):
        """分析 PPT"""
        analysis_json = self.output_dir / f"{Path(pptx_path).stem}_analysis.json"
        script = self.skills_dir / "ppt_analyzer.py"

        cmd = [sys.executable, str(script), str(pptx_path), str(analysis_json)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and analysis_json.exists():
            return str(analysis_json)
        return None

    def run_data_analysis(self, analysis_json):
        """分析數據"""
        market_json = self.output_dir / f"{Path(analysis_json).stem}_market.json"
        market_csv = self.output_dir / f"{Path(analysis_json).stem}_market.csv"
        script = self.skills_dir / "data_analyzer.py"

        cmd = [sys.executable, str(analysis_json), str(market_csv), str(market_json)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and market_json.exists():
            return str(market_json)
        return None

    def run_pdf_generation(self, market_json):
        """生成 PDF"""
        script = self.skills_dir / "pdf_generator.py"
        pdf_path = self.output_dir / f"{Path(market_json).stem}_report.pdf"

        cmd = [sys.executable, str(script), str(market_json), str(pdf_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and pdf_path.exists():
            return str(pdf_path)
        return None

    def run_ppt_generation(self, market_json):
        """生成 PPT"""
        script = self.skills_dir / "ppt_generator_v3.py"
        pptx_path = self.output_dir / f"{Path(market_json).stem}_report.pptx"

        cmd = [sys.executable, str(script), str(market_json), str(pptx_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and pptx_path.exists():
            return str(pptx_path)
        return None

    def run_chart_generation(self, market_json):
        """生成圖表"""
        script = self.skills_dir / "chart_generator.py"

        cmd = [sys.executable, str(script), str(market_json), str(self.output_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            charts = list(self.output_dir.glob(f"{Path(market_json).stem}_*.png"))
            if charts:
                return [str(c) for c in charts]
        return []

    def run_excel_analysis(self, excel_path):
        """分析 Excel"""
        script = self.skills_dir / "excel_reader.py"
        json_path = self.output_dir / f"{Path(excel_path).stem}_data.json"
        csv_path = self.output_dir / f"{Path(excel_path).stem}_data.csv"

        cmd = [sys.executable, str(script), str(excel_path), str(json_path), str(csv_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        return str(json_path) if json_path.exists() else None

    def generate_report(self, input_path, options=None):
        """
        生成完整報告

        Args:
            input_path: 輸入檔案（PPT/Excel/JSON）
            options: 生成選項
                - pdf: 生成 PDF
                - pptx: 生成 PPT
                - charts: 生成圖表
                - all: 生成全部
        """
        options = options or {'pdf': True, 'pptx': True, 'charts': True}
        data_type = self.detect_data_source(input_path)

        self.log(f"Input: {input_path}")
        self.log(f"Type: {data_type.upper()}")
        self.log(f"Options: {options}")

        outputs = {}

        # 步驟 1: 讀取/分析數據
        if data_type == 'pptx':
            self.log("Step 1: Analyzing PPT...")
            analysis_json = self.step("PPT Analysis", self.run_ppt_analysis, input_path)
            if analysis_json:
                self.step("Data Analysis", self.run_data_analysis, analysis_json)

        elif data_type == 'excel':
            self.log("Step 1: Reading Excel...")
            analysis_json = self.step("Excel Analysis", self.run_excel_analysis, input_path)

        elif data_type == 'json':
            analysis_json = input_path

        else:
            self.log(f"Unsupported file type: {data_type}", "ERROR")
            return None

        if not analysis_json or not Path(analysis_json).exists():
            self.log("Data analysis failed", "ERROR")
            return None

        # 步驟 2: 生成輸出
        if options.get('pdf') or options.get('all'):
            pdf_path = self.step("PDF Generation", self.run_pdf_generation, analysis_json)
            if pdf_path:
                outputs['pdf'] = pdf_path

        if options.get('pptx') or options.get('all'):
            pptx_path = self.step("PPT Generation", self.run_ppt_generation, analysis_json)
            if pptx_path:
                outputs['pptx'] = pptx_path

        if options.get('charts') or options.get('all'):
            charts = self.step("Chart Generation", self.run_chart_generation, analysis_json)
            if charts:
                outputs['charts'] = charts

        return outputs

    def generate_summary(self):
        """生成摘要報告"""
        summary = []
        summary.append("=" * 60)
        summary.append("       Automated Report Generation Summary")
        summary.append(f"       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("=" * 60)

        summary.append("\n[Steps Executed]")
        for step in self.steps[-10:]:
            summary.append(f"  {step}")

        summary.append("\n[Results]")
        for name, result in self.results.items():
            status = "OK" if result['status'] == 'success' else "FAIL"
            summary.append(f"  [{status}] {name}")

        summary.append("\n[Output Files]")
        for key, path in self.results.items():
            if result['status'] == 'success' and result['result']:
                val = result['result']
                if isinstance(val, list):
                    for v in val:
                        summary.append(f"  - {Path(v).name}")
                elif isinstance(val, str):
                    summary.append(f"  - {Path(val).name}")

        summary.append("\n" + "=" * 60)
        summary.append(f"Output Directory: {self.output_dir}")
        summary.append("=" * 60)

        return "\n".join(summary)


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("Automated Report Generator")
        print("=" * 60)
        print("")
        print("Usage: python auto_report.py <input_file> [options]")
        print("")
        print("Input types: .pptx, .xlsx, .xls, .csv, .json")
        print("")
        print("Options:")
        print("  --pdf      Generate PDF report")
        print("  --pptx     Generate PPT report")
        print("  --charts   Generate charts")
        print("  --all      Generate all (default)")
        print("")
        print("Examples:")
        print('  python auto_report.py "data.pptx" --all')
        print('  python auto_report.py "data.xlsx" --pdf --charts')
        print('  python auto_report.py "market.json" --pptx')
        sys.exit(1)

    input_path = sys.argv[1]

    # 解析選項
    options = {
        'pdf': '--pdf' in sys.argv or '--all' in sys.argv or '--charts' not in sys.argv,
        'pptx': '--pptx' in sys.argv or '--all' in sys.argv or '--charts' not in sys.argv,
        'charts': '--charts' in sys.argv or '--all' in sys.argv
    }

    if '--all' in sys.argv:
        options = {'pdf': True, 'pptx': True, 'charts': True}

    generator = AutoReportGenerator()
    results = generator.generate_report(input_path, options)

    print("\n" + generator.generate_summary())

    if results:
        print("\n[SUCCESS] Report generated!")
    else:
        print("\n[FAILURE] Report generation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
