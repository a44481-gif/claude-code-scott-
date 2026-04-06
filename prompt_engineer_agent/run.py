#!/usr/bin/env python3
"""Prompt Engineer Agent 執行入口"""

import sys
import os

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prompt_engineer import main

if __name__ == "__main__":
    main()
