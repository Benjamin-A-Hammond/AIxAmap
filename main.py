# main.py (FastAPI应用程序)
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
import httpx
import re
import json

# 加载环境变量
load_dotenv()

# 获取API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AMAP_API_KEY = os.getenv("AMAP_API_KEY")
AMAP_JS_API_KEY = os.getenv("AMAP_JS_API_KEY")
AMAP_JS_API_PWD = os.getenv("AMAP_JS_API_PWD")

app = FastAPI()

# 创建templates和static目录
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "amap_key": AMAP_JS_API_KEY,  # 使用前端JS API的Key
        "amap_pwd": AMAP_JS_API_PWD   # 传递安全密钥
    })

@app.post("/process")
async def process_input(user_input: str = Form(...)):
    # 调用OpenAI API提取地点
    places = await extract_places(user_input)
    
    # 获取地点的地理坐标
    locations = []
    for place in places:
        location = await get_location(place)
        if location:
            locations.append({
                "name": place,
                "location": location
            })
    
    return {"locations": locations}

async def extract_places(text):
    """使用OpenAI API从用户输入中提取地点名称"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "你是一个地点提取助手。从用户输入中提取出所有地点名称，并以JSON数组形式返回。仅返回JSON数组，不要有其他文字。"},
                    {"role": "user", "content": f"从以下文本中提取地点名称: '{text}'"}
                ]
            },
            timeout=30.0
        )
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # 提取JSON数组
        try:
            # 尝试直接解析整个内容
            places = json.loads(content)
        except json.JSONDecodeError:
            # 如果失败，尝试从文本中提取JSON部分
            matches = re.search(r'\[(.*?)\]', content, re.DOTALL)
            if matches:
                try:
                    places = json.loads(f"[{matches.group(1)}]")
                except json.JSONDecodeError:
                    # 简单分割方法
                    text_places = [p.strip() for p in content.replace('[', '').replace(']', '').replace('"', '').replace("'", "").split(',')]
                    places = [p for p in text_places if p]
            else:
                # 如果没有找到JSON，直接按逗号分割
                places = [p.strip() for p in content.split(',')]
        
        return places

async def get_location(place_name):
    """使用高德地图API获取地点的地理坐标"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://restapi.amap.com/v3/geocode/geo",
            params={
                "key": AMAP_API_KEY,  # 使用Web服务API的Key
                "address": place_name
            }
        )
        
        result = response.json()
        if result.get("status") == "1" and result.get("geocodes") and len(result["geocodes"]) > 0:
            location = result["geocodes"][0]["location"]
            return location.split(",")  # 返回[经度, 纬度]
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)