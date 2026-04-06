@echo off
chcp 65001 >nul
set PY=D:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe
set PROJ=D:\claude~1\.claude
echo [1/4] IT_News_Agent...
schtasks /create /tn IT_News_Agent /tr "cmd /c chcp 65001 >nul && cd /d %PROJ% && %PY% it_news_agent\src\run.py --mode full" /sc daily /st 07:00 /f
echo [2/4] PC_Parts_Agent...
schtasks /create /tn PC_Parts_Agent /tr "cmd /c chcp 65001 >nul && cd /d %PROJ% && %PY% pc_parts_agent\src\run.py --mode full" /sc daily /st 08:00 /f
echo [3/4] MSI_Monitor_Agent...
schtasks /create /tn MSI_Monitor_Agent /tr "cmd /c chcp 65001 >nul && cd /d %PROJ% && %PY% msi_monitor_agent\src\run.py --mode full" /sc daily /st 09:00 /f
echo [4/4] Report_Agent...
schtasks /create /tn Report_Agent /tr "cmd /c chcp 65001 >nul && cd /d %PROJ% && %PY% report_agent\src\run.py --mode full" /sc weekly /d MON /st 10:00 /f
echo.
schtasks /query /tn IT_News_Agent /fo CSV 2>nul
schtasks /query /tn PC_Parts_Agent /fo CSV 2>nul
schtasks /query /tn MSI_Monitor_Agent /fo CSV 2>nul
schtasks /query /tn Report_Agent /fo CSV 2>nul
