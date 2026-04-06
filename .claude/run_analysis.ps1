# Run CoBM_BQT_Analysis.py
Set-Location "D:\claude mini max 2.7\.claude"
$env:PYTHONIOENCODING = "utf-8"
python.exe CoBM_BQT_Analysis.py 2>&1 | Tee-Object -FilePath "analysis_log.txt"
