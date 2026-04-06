@echo off
chcp 65001 >nul
color 0A

:start
cls
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                                                          ║
echo  ║        🎬 漫剧出海 - 自动运营系统 v2.0                ║
echo  ║        抖音号：@yaoweiba3300                           ║
echo  ║                                                          ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

echo  ┌─────────────────────────────────────────────────────────┐
echo  │                                                         │
echo  │  📊 系统状态：运行中                                  │
echo  │  📅 日期：%date%                                     │
echo  │  📦 内容库：40条                                      │
echo  │  ⏰ 定时任务：每日08:00自动提醒                       │
echo  │                                                         │
echo  └─────────────────────────────────────────────────────────┘
echo.

echo  请选择操作：
echo.
echo  [1] 📋 查看今日发布内容
echo  [2] 🚀 立即发布提醒
echo  [3] 📊 查看统计
echo  [4] 📝 导出发布清单
echo  [5] 🔄 更新内容库
echo  [6] 💰 收钱指南
echo  [0] ❌ 退出
echo.
echo.

set /p choice=请输入选项 (0-6):

if "%choice%"=="1" goto view
if "%choice%"=="2" goto remind
if "%choice%"=="3" goto stats
if "%choice%"=="4" goto export
if "%choice%"=="5" goto update
if "%choice%"=="6" goto money
if "%choice%"=="0" goto end

echo.
echo  ⚠️  无效选项，请重新选择
timeout /t 2 >nul
goto start

:view
cls
echo.
echo  📋 今日发布内容
echo  ====================
echo.
type output\today_content.txt
echo.
echo.
echo  按任意键返回菜单...
pause >nul
goto start

:remind
cls
echo.
echo  🚀 启动发布提醒
echo  ====================
echo.
start output\reminder.bat
echo.
echo  ✅ 提醒已启动！请查看弹出的窗口！
echo.
timeout /t 3 >nul
goto start

:stats
cls
echo.
echo  📊 统计数据
echo  ====================
echo.
node scripts\manager.js stats
echo.
echo  按任意键返回菜单...
pause >nul
goto start

:export
cls
echo.
echo  📝 导出发布清单
echo  ====================
echo.
node scripts\exporter.js list
echo.
echo  ✅ 已导出到 output\daily_publish_list.md
echo.
echo  按任意键返回菜单...
pause >nul
goto start

:update
cls
echo.
echo  🔄 更新内容库
echo  ====================
echo.
node scripts\generator.js
echo.
node auto\auto-poster.js
echo.
echo  ✅ 内容库已更新！
echo.
echo  按任意键返回菜单...
pause >nul
goto start

:money
cls
echo.
echo  💰 收钱指南
echo  ====================
echo.
echo  ┌─────────────────────────────────────────────────────────┐
echo  │                                                         │
echo  │  📌 立即行动：                                          │
echo  │                                                         │
echo  │  1. 打开 linktr.ee 注册账号                            │
echo  │  2. 设置付费产品（全集VIP $1.99）                     │
echo  │  3. 在抖音简介放Linktree链接                          │
echo  │  4. 每条视频引导付费                                   │
echo  │                                                         │
echo  │  💵 收入预估：                                          │
echo  │  · 1000粉丝 = $50/月                                   │
echo  │  · 10000粉丝 = $500/月                                 │
echo  │  · 100000粉丝 = $5000+/月                             │
echo  │                                                         │
echo  └─────────────────────────────────────────────────────────┘
echo.
echo  按任意键返回菜单...
pause >nul
goto start

:end
echo.
echo  ═══════════════════════════════════════════════════════════
echo.
echo  🎉 感谢使用漫剧出海自动运营系统！
echo.
echo  💡 提示：明天 08:00 自动提醒发布
echo.
echo  ═══════════════════════════════════════════════════════════
echo.
timeout /t 3 >nul
exit
