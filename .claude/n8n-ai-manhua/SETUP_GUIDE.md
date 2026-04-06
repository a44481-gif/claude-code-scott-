# 漫剧出海变现 - n8n + Claude AI 完整指南

## 目录
1. [获取 Claude API 密钥](#1-获取-claude-api-密钥)
2. [搭建 n8n 环境](#2-搭建-n8n-环境)
3. [创建 n8n 工作流](#3-创建-n8n-工作流)
4. [Claude Code 自定义技能](#4-claude-code-自定义技能)
5. [使用示例](#5-使用示例)

---

## 1. 获取 Claude API 密钥

### 步骤 1: 注册 Anthropic 账号
1. 访问 [ Anthropic Console ](https://console.anthropic.com/)
2. 点击 "Sign Up" 使用邮箱注册
3. 验证邮箱完成注册

### 步骤 2: 创建 API 密钥
1. 登录 [console.anthropic.com](https://console.anthropic.com/)
2. 进入 **API Keys** 页面
3. 点击 **Create Key**
4. 复制生成的密钥（格式：`sk-ant-api03-xxxxxx`）

### 步骤 3: 充值 Credits
1. 进入 **Billing** 页面
2. 建议先购买 $20-50 体验
3. Claude Pro 订阅：$20/月，包含 API 使用额度

### 费用参考
| 模型 | 输入价格 | 输出价格 | 推荐场景 |
|------|---------|---------|---------|
| Claude 3.5 Sonnet | $3/1M tokens | $15/1M tokens | 日常生成 |
| Claude 3 Haiku | $0.25/1M tokens | $1.25/1M tokens | 批量生成 |

---

## 2. 搭建 n8n 环境

### 方案 A: n8n Cloud（推荐新手）
1. 访问 [n8n.io](https://n8n.io/)
2. 点击 **Start Free**
3. 使用 Google/GitHub 账号注册
4. 即可使用云端版本

### 方案 B: 本地部署 n8n（推荐长期运营）
```bash
# 使用 Docker 部署
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# 或使用 npm
npm install -g n8n
n8n start
```

### 方案 C: Zeabur 一键部署（免费额度）
1. 访问 [zeabur.com](https://zeabur.com)
2. 连接 GitHub
3. 一键部署 n8n
4. 获得免费域名和 HTTPS

---

## 3. 创建 n8n 工作流

### 工作流结构
```
[触发器] → [调用 Claude API] → [解析 JSON] → [格式化内容] → [发布到平台]
```

### 节点配置

#### 节点 1: Manual Trigger（手动触发）
- 类型: Trigger
- 用途: 测试时手动运行

#### 节点 2: Code（生成 Prompt）
```javascript
const contentType = $json.content_type || '龙王';
const prompt = `你是专业的漫剧出海AI变现运营师。生成一套完整的漫剧内容，严格输出JSON格式：

{
"theme": "高变现漫剧主题",
"6_panel_script": "6格分镜台词",
"title": "付费钩子标题",
"caption": "发布文案",
"tags": "#标签1 #标签2...",
"cta_text": "跳转付费链接话术",
"post_time": "最佳发布时间"
}

题材类型：${contentType}
要求：
- 仅生成龙王、逆袭、虐渣、重生、神医、系统类海外华人爆款付费题材
- 前5格造冲突爽点，最后1格强留悬念引导看全集付费
- 标题提升点击率与付费意愿
- 标签10个精准变现热门标签`;

return { prompt, contentType };
```

#### 节点 3: HTTP Request（调用 Claude API）
- **Method**: POST
- **URL**: `https://api.anthropic.com/v1/messages`
- **Authentication**: None (use Headers)
- **Headers**:
  ```
  x-api-key: YOUR_API_KEY
  anthropic-version: 2023-06-01
  content-type: application/json
  ```
- **Body**:
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 2048,
  "messages": [
    {
      "role": "user",
      "content": "{{ $json.prompt }}"
    }
  ]
}
```

#### 节点 4: JSON Parse（解析响应）
```javascript
const response = JSON.parse($input.first().json.content[0].text);
return response;
```

#### 节点 5: Slack/Discord 通知（可选）
- 发送生成结果到你的频道

---

## 4. Claude Code 自定义技能

创建以下 6 个技能文件，覆盖所有题材类型。

### 4.1 龙王题材技能
