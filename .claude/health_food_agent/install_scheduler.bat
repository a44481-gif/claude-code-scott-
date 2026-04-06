@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   健康食品 AI 扩客代理人 - 定时任务安装
echo ========================================
echo.
echo 请选择执行频率:
echo   1) 每日执行 (每天 09:00)
echo   2) 每周执行 (每周一 09:00)
echo.
set /p choice=请选择 (1/2):

if "%choice%"=="1" goto daily
if "%choice%"=="2" goto weekly
echo 无效选择！
pause
exit

:daily
echo.
echo 正在创建每日定时任务...
powershell -ExecutionPolicy Bypass -Command "
$action = New-ScheduledTaskAction -Execute 'python' -Argument '--mode full' -WorkingDirectory 'D:\claude mini max 2.7\.claude\health_food_agent'
$trigger = New-ScheduledTaskTrigger -Daily -At '09:00'
Register-ScheduledTask -TaskName 'HealthFoodAgent_Daily' -Action $action -Trigger $trigger -Description '健康食品 AI 扩客代理人 - 每日自动分析报告' -RunLevel Highest -Force
"
echo.
echo 完成！任务已创建: HealthFoodAgent_Daily
echo.
echo 可选操作:
echo   - 立即测试: 启动任务计划程序，找到 HealthFoodAgent_Daily，点击运行
echo   - 查看报告: D:\claude mini max 2.7\.claude\health_food_agent\reports\
echo.
pause
exit

:weekly
echo.
echo 正在创建每周定时任务...
powershell -ExecutionPolicy Bypass -Command "
$action = New-ScheduledTaskAction -Execute 'python' -Argument '--mode full' -WorkingDirectory 'D:\claude mini max 2.7\.claude\health_food_agent'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At '09:00'
Register-ScheduledTask -TaskName 'HealthFoodAgent_Weekly' -Action $action -Trigger $trigger -Description '健康食品 AI 扩客代理人 - 每周自动分析报告' -RunLevel Highest -Force
"
echo.
echo 完成！任务已创建: HealthFoodAgent_Weekly
echo.
echo 可选操作:
echo   - 立即测试: 启动任务计划程序，找到 HealthFoodAgent_Weekly，点击运行
echo   - 查看报告: D:\claude mini max 2.7\.claude\health_food_agent\reports\
echo.
pause
