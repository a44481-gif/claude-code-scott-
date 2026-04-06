# 健康食品 AI 扩客代理人 - 定时任务配置

## 自动执行计划

### 选项 1: 每日早上 9:00 自动执行
```
时间: 每天 09:00
功能: 生成报告 + 发送邮件
```

### 选项 2: 每周一早上 9:00 自动执行
```
时间: 每周一 09:00
功能: 生成报告 + 发送邮件
```

---

## Windows 任务计划程序设置

请以管理员身份运行 PowerShell 执行以下命令：

### 每日执行
```powershell
# 创建每日任务
$action = New-ScheduledTaskAction -Execute "python" -Argument "skill_health_food.py --mode full" -WorkingDirectory "D:\claude mini max 2.7\.claude\health_food_agent"
$trigger = New-ScheduledTaskTrigger -Daily -At "09:00"
Register-ScheduledTask -TaskName "HealthFoodAgent_Daily" -Action $action -Trigger $trigger -Description "健康食品 AI 扩客代理人 - 每日自动分析报告" -RunLevel Highest
```

### 每周执行（周一）
```powershell
# 创建每周任务
$action = New-ScheduledTaskAction -Execute "python" -Argument "skill_health_food.py --mode full" -WorkingDirectory "D:\claude mini max 2.7\.claude\health_food_agent"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "09:00"
Register-ScheduledTask -TaskName "HealthFoodAgent_Weekly" -Action $action -Trigger $trigger -Description "健康食品 AI 扩客代理人 - 每周自动分析报告" -RunLevel Highest
```

---

## 手动管理任务

```powershell
# 查看任务状态
Get-ScheduledTask -TaskName "HealthFoodAgent_Daily"

# 立即执行一次
Start-ScheduledTask -TaskName "HealthFoodAgent_Daily"

# 删除任务（如需）
Unregister-ScheduledTask -TaskName "HealthFoodAgent_Daily" -Confirm:$false
```

---

## 建议选择

| 选项 | 频率 | 适用场景 |
|------|------|----------|
| A | 每日 | 市场变化快，需密切监控 |
| B | 每周 | 常规运营，周报形式 |

请选择 **A** 或 **B**，我来帮您自动配置！
