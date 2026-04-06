# -*- coding: utf-8 -*-
from pptx import Presentation

src1 = r'd:/claude mini max 2.7/storage_market_output/Global_Storage_Market_2025_2030.pptx'
src2 = r'd:/claude mini max 2.7/storage_market_output/CCS_全球储能市场综合报告_2025-2030_FINAL.pptx'
src3 = r'd:/claude mini max 2.7/storage_market_output/merged_report_final.pptx'

for name, path in [('SRC1 全球储能', src1), ('MERGED FINAL', src2), ('merged_final', src3)]:
    try:
        prs = Presentation(path)
        print(f'{name}: {len(prs.slides)} slides OK')
    except Exception as e:
        print(f'{name} ERROR: {e}')
