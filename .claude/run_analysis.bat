@echo off
cd /d "D:\claude mini max 2.7\.claude"
python.exe CoBM_BQT_Analysis.py > analysis_log.txt 2>&1
type analysis_log.txt
