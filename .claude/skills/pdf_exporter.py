# -*- coding: utf-8 -*-
"""
PDF 導出腳本
使用 PowerPoint COM 對象導出 PDF
僅適用於 Windows + 已安裝 PowerPoint
"""

import subprocess
import os
import sys


def export_ppt_to_pdf(pptx_path, output_dir=None):
    """
    將 PPT 導出為 PDF

    Args:
        pptx_path: PPT 檔案路徑
        output_dir: 輸出目錄（預設為 PPT 同目錄）

    Returns:
        str: PDF 檔案路徑
    """
    if not os.path.exists(pptx_path):
        print(f"[ERROR] File not found: {pptx_path}")
        return None

    if output_dir is None:
        output_dir = os.path.dirname(pptx_path)

    pdf_name = os.path.splitext(os.path.basename(pptx_path))[0] + ".pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    # 使用 PowerShell + COM 對象
    ppt_path_escaped = pptx_path.replace("\\", "\\\\")
    pdf_path_escaped = pdf_path.replace("\\", "\\\\")

    ps_script = '''
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName Microsoft.Office.Interop.PowerPoint

$pptPath = "''' + ppt_path_escaped + '''"
$pdfPath = "''' + pdf_path_escaped + '''"

$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue

$presentation = $ppt.Presentations.Open($pptPath, $false, $false, $false)
$presentation.SaveAs($pdfPath, 32)

$presentation.Close()
$ppt.Quit()

[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
Write-Output "PDF saved: $pdfPath"
'''

    # 保存 PowerShell 腳本
    ps_file = os.path.join(output_dir, "_export_pdf.ps1")
    with open(ps_file, 'w', encoding='utf-8') as f:
        f.write(ps_script)

    print(f"Exporting PDF...")
    print(f"  Source: {pptx_path}")
    print(f"  Output: {pdf_path}")

    try:
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print(f"[OK] PDF exported successfully!")
            return pdf_path
        else:
            print(f"[ERROR] Export failed: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print("[ERROR] Export timeout")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None
    finally:
        # 清理臨時腳本
        if os.path.exists(ps_file):
            os.remove(ps_file)


def export_multiple(pptx_files, output_dir):
    """批量導出 PDF"""
    results = []
    for pptx in pptx_files:
        print(f"\nProcessing: {os.path.basename(pptx)}")
        result = export_ppt_to_pdf(pptx, output_dir)
        results.append((pptx, result))

    print("\n" + "=" * 60)
    print("Batch Export Complete")
    print("=" * 60)
    for pptx, result in results:
        status = os.path.basename(result) if result else "FAILED"
        print(f"  {os.path.basename(pptx)} -> {status}")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_exporter.py <pptx_file> [output_dir]")
        print("       python pdf_exporter.py file1.pptx file2.pptx [output_dir]")
        sys.exit(1)

    files = sys.argv[1:]
    output_dir = None

    # 檢查最後一個參數是否為目錄
    if len(files) > 1 and os.path.isdir(files[-1]):
        output_dir = files.pop()

    # 檢查是否為目錄
    if len(files) == 1 and os.path.isdir(files[0]):
        # 導出目錄中所有 PPT
        output_dir = files[0]
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)
                 if f.endswith('.pptx')]

    print(f"Files to export: {len(files)}")

    if len(files) == 1:
        export_ppt_to_pdf(files[0], output_dir)
    else:
        export_multiple(files, output_dir)
