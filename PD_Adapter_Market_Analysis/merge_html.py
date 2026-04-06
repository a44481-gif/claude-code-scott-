#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge HTML files for PD Adapter Market Analysis Report"""

import os

base = r'd:\claude mini max 2.7\PD_Adapter_Market_Analysis'
main = os.path.join(base, 'PD_Adapter_Market_Analysis_Report.html')
append = os.path.join(base, 'html_append_content.html')
out = os.path.join(base, 'PD_Adapter_Market_Analysis_Report_FULL.html')

# Read first 265 lines of main file
with open(main, 'r', encoding='utf-8') as f:
    main_lines = f.readlines()
main_content = ''.join(main_lines[:265])

# Read full append file
with open(append, 'r', encoding='utf-8') as f:
    append_content = f.read()

# Combine
combined = main_content + append_content

# Write output
with open(out, 'w', encoding='utf-8') as f:
    f.write(combined)

size = os.path.getsize(out)
line_count = combined.count('\n') + 1
print(f'SUCCESS: Merged file written')
print(f'Output: {out}')
print(f'Lines: {line_count}')
print(f'Size: {size} bytes ({size/1024:.1f} KB)')
