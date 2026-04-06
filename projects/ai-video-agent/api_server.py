# 短视频内容生成 API
# 使用 FastAPI 创建一个简单的 API

from fastapi import FastAPI
from pydantic import BaseModel
import sys
sys.path.insert(0, 'src')

app = FastAPI(title="AI 短视频内容生成 API")

class ContentResponse(BaseModel):
    date: str
    category: str
    content_type: str
    title: str
    caption: str
    hashtags: list
    publish_time: str

@app.get("/")
def home():
    return {"message": "AI 短视频内容生成 API", "status": "running"}

@app.get("/daily-content", response_model=ContentResponse)
def get_daily_content():
    """获取每日内容"""
    from content.daily_content_generator import generate_daily_content, format_content_for_douyin

    content = generate_daily_content()
    caption = format_content_for_douyin(content)

    # 确定发布时间
    from datetime import datetime
    hour = datetime.now().hour
    if 6 <= hour < 12:
        publish_time = "12:00"
    elif 12 <= hour < 18:
        publish_time = "18:00"
    else:
        publish_time = "21:00"

    return ContentResponse(
        date=content['date'],
        category=content['category'],
        content_type=content['content_type'],
        title=content['title'],
        caption=caption,
        hashtags=content['hashtags'],
        publish_time=publish_time
    )

@app.post("/send-email")
def send_content_email():
    """发送内容到邮箱"""
    from content.daily_content_generator import send_daily_content_email
    result = send_daily_content_email()
    return {"status": "success", "message": "邮件已发送"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
