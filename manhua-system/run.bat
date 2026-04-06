@echo off
chcp 65001 >nul
color 0A

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║                                                  ║
echo  ║        漫剧出海 - 内容管理系统 v1.0             ║
echo  ║        Manhua Content Management System          ║
echo  ║                                                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:menu
echo  请选择操作：
echo.
echo  [1] 生成内容    - 生成60套漫剧内容
echo  [2] 查看统计    - 查看内容统计数据
echo  [3] 发布计划    - 生成7天发布计划
echo  [4] 提醒脚本    - 生成Windows提醒
echo  [5] 任务计划    - 生成任务计划命令
echo  [6] 列出内容    - 列出所有内容
echo  [7] 导出CSV     - 导出为CSV格式
echo  [8] 发布内容    - 标记内容为已发布
echo  [0] 退出
echo.
echo.

set /p choice=请输入选项 (0-8):

if "%choice%"=="1" goto generate
if "%choice%"=="2" goto stats
if "%choice%"=="3" goto schedule
if "%choice%"=="4" goto reminder
if "%choice%"=="5" goto tasks
if "%choice%"=="6" goto list
if "%choice%"=="7" goto export
if "%choice%"=="8" goto publish
if "%choice%"=="0" goto end

echo 无效选项，请重新选择
echo.
goto menu

:generate
echo.
echo 正在生成内容...
node scripts\generator.js
echo.
pause
goto menu

:stats
echo.
echo 正在生成统计...
node scripts\manager.js stats
echo.
pause
goto menu

:schedule
echo.
echo 正在生成发布计划...
node scripts\manager.js schedule
echo.
pause
goto menu

:reminder
echo.
echo 正在生成提醒脚本...
node scripts\manager.js reminder
echo.
echo 双击 output\reminder.bat 可查看发布计划
echo.
pause
goto menu

:tasks
echo.
echo 正在生成任务计划命令...
node scripts\manager.js tasks
echo.
pause
goto menu

:list
echo.
echo 正在列出内容...
node scripts\manager.js list
echo.
pause
goto menu

:export
echo.
echo 正在导出内容...
node scripts\exporter.js
echo.
pause
goto menu

:publish
echo.
echo 请输入要发布的内容ID:
set /p contentId=
node scripts\manager.js publish %contentId%
echo.
pause
goto menu

:end
echo.
echo 感谢使用！
echo.
exit
