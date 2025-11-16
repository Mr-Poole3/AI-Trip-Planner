import os
import base64
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn
import logging
import asyncio
from hotel_agent import HotelAgent
from pydantic import BaseModel
import urllib.parse
import urllib.request

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Chat API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vue开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

# 初始化酒店代理
hotel_agent = HotelAgent()

AMAP_KEY = os.environ.get("AMAP_KEY")

class TravelPlanRequest(BaseModel):
    message: str

class MessageContent(BaseModel):
    type: str  # "text" or "image_url"
    text: Optional[str] = None
    image_url: Optional[dict] = None

class ChatMessage(BaseModel):
    role: str
    content: List[MessageContent]

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "doubao-1-5-thinking-vision-pro-250428"
    system_prompt: Optional[str] = None  # 系统提示词

class ChatResponse(BaseModel):
    message: str
    role: str = "assistant"

class HotelChatRequest(BaseModel):
    message: str

class RouteTestRequest(BaseModel):
    origin_name: str
    destination_name: str
    city: Optional[str] = None
    mode: Optional[str] = "driving"


@app.get("/")
async def root():
    return {"message": "AI Chat API is running"}


@app.post("/api/hotel-chat")
async def hotel_chat(request: HotelChatRequest):
    """
    智能酒店推荐聊天接口
    流式返回处理步骤和结果
    """
    try:
        async def generate_hotel_stream():
            try:
                # 步骤1: 意图识别
                step1_running = json.dumps({'step': 1, 'status': 'running', 'message': '正在分析您的需求...'}, ensure_ascii=False)
                logger.info(f"发送步骤1 running: {step1_running}")
                yield f"data: {step1_running}\n\n"
                yield ": ping\n\n"  # SSE 注释行，强制刷新
                await asyncio.sleep(0.1)
                
                # 在线程池中运行同步代码
                loop = asyncio.get_event_loop()
                intent_result = await loop.run_in_executor(None, hotel_agent.analyze_intent, request.message)
                
                step1_completed = json.dumps({'step': 1, 'status': 'completed', 'message': '需求分析完成', 'data': intent_result}, ensure_ascii=False)
                logger.info(f"发送步骤1 completed: {step1_completed}")
                yield f"data: {step1_completed}\n\n"
                yield ": ping\n\n"  # SSE 注释行，强制刷新
                await asyncio.sleep(0.1)

                # 基于 hotel-book 门控：仅当明确需要预订时进入酒店搜索与推荐
                hotel_book = bool(intent_result.get("hotel-book", False))
                if not hotel_book:
                    # 未明确预订，进行二次确认而不进入搜索
                    yield f"data: {json.dumps({'step': 2, 'status': 'completed', 'message': '未明确需要预订，建议确认后再继续'}, ensure_ascii=False)}\n\n"
                    confirm_text = (
                        "我可以为您搜索并推荐可预订的酒店。请确认是否需要预订酒店，并可补充入住时间、人数与目的地等信息。"
                    )
                    yield f"data: {json.dumps({'type': 'final_response', 'content': confirm_text}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                    return

                # 普通聊天意图直接走聊天（冗余保护）
                if intent_result.get("intent") == "chat":
                    yield f"data: {json.dumps({'step': 2, 'status': 'running', 'message': '正在生成回复...'}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.1)
                    response = await loop.run_in_executor(None, hotel_agent.chat, request.message)
                    yield f"data: {json.dumps({'step': 2, 'status': 'completed', 'message': '回复生成完成'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'final_response', 'content': response}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                    return
                
                # 酒店预订流程
                params = intent_result.get("params", {})
                
                # 步骤2: 参数验证
                yield f"data: {json.dumps({'step': 2, 'status': 'running', 'message': '正在准备搜索参数...'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
                
                if not params.get("destination"):
                    yield f"data: {json.dumps({'step': 2, 'status': 'error', 'message': '未能识别目的地，请提供更多信息'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'final_response', 'content': '抱歉，我没有理解您想去哪里。请告诉我您的目的地，比如"成都春熙路"或"上海外滩"。'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                    return
                
                yield f"data: {json.dumps({'step': 2, 'status': 'completed', 'message': '搜索参数准备完成', 'data': params}, ensure_ascii=False)}\n\n"
                yield ": ping\n\n"  # SSE 注释行，强制刷新
                await asyncio.sleep(0.1)
                
                # 步骤3: 搜索酒店
                destination = params.get("destination", "")
                step3_running = json.dumps({'step': 3, 'status': 'running', 'message': f'正在搜索 {destination} 的酒店...'}, ensure_ascii=False)
                logger.info(f"发送步骤3 running: {step3_running}")
                yield f"data: {step3_running}\n\n"
                yield ": ping\n\n"  # SSE 注释行，强制刷新
                await asyncio.sleep(0.1)
                
                # 在后台线程中执行搜索
                logger.info("开始在后台线程执行酒店搜索...")
                search_result = await loop.run_in_executor(None, hotel_agent.search_hotels, params)
                logger.info(f"酒店搜索完成，结果: {search_result.get('success')}")
                
                if not search_result.get("success"):
                    error_msg = search_result.get("error", "未知错误")
                    yield f"data: {json.dumps({'step': 3, 'status': 'error', 'message': f'搜索失败: {error_msg}'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'final_response', 'content': f'抱歉，搜索酒店时遇到问题：{error_msg}'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                    return
                
                hotels_count = len(search_result.get("hotels", []))
                yield f"data: {json.dumps({'step': 3, 'status': 'completed', 'message': f'找到 {hotels_count} 家酒店'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
                
                if hotels_count == 0:
                    yield f"data: {json.dumps({'type': 'final_response', 'content': '抱歉，没有找到符合条件的酒店。请尝试调整搜索条件。'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                    return
                
                # 步骤4: 生成推荐
                yield f"data: {json.dumps({'step': 4, 'status': 'running', 'message': '正在为您生成个性化推荐...'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)

                # 开始流式输出推荐内容（在完成所有片段之前，保持第4步为running）
                logger.info("开始流式输出推荐内容")
                yield f"data: {json.dumps({'type': 'recommendation_start'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)

                # 真正的流式生成推荐
                try:
                    for chunk in hotel_agent.generate_recommendations(request.message, search_result):
                        if chunk:
                            yield f"data: {json.dumps({'type': 'recommendation_chunk', 'content': chunk}, ensure_ascii=False)}\n\n"
                            await asyncio.sleep(0.05)  # 小延迟以实现打字机效果
                except Exception as e:
                    logger.error(f"生成推荐时出错: {str(e)}")
                    # 标记第4步为error
                    yield f"data: {json.dumps({'step': 4, 'status': 'error', 'message': f'生成推荐时出错: {str(e)}'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'error', 'content': f'生成推荐时出错: {str(e)}'}, ensure_ascii=False)}\n\n"
                    return

                # 推荐完成后，先结束推荐流，再标记第4步完成
                logger.info("推荐内容发送完成")
                yield f"data: {json.dumps({'type': 'recommendation_end'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
                yield f"data: {json.dumps({'step': 4, 'status': 'completed', 'message': '推荐生成完成'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"酒店聊天流式生成错误: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'content': f'处理请求时出错: {str(e)}'}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(generate_hotel_stream(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"酒店聊天接口错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/travel-plan")
async def travel_plan(request: TravelPlanRequest):
    try:
        async def generate_travel_stream():
            try:
                step1_running = json.dumps({'step': 1, 'status': 'running', 'message': '正在分析您的旅行需求...'}, ensure_ascii=False)
                yield f"data: {step1_running}\n\n"
                await asyncio.sleep(0.1)

                loop = asyncio.get_event_loop()

                def analyze():
                    system_prompt = (
                        "你是一个智能旅行规划助手。你需要判断用户是否需要旅行计划规划推荐。"
                        "输出严格的JSON。当不需要旅行规划时，返回 {\"plan_needed\": false, \"message\": \"normal_chat\"}。"
                        "当需要旅行规划时，返回 {\"plan_needed\": true, \"plan\": {\"destination\": ..., \"origin\": ..., \"start_date\": ..., \"end_date\": ..., \"people\": 可选, \"attractions\": 可选数组}, \"corrections\": 可选列表 }。"
                        "不得添加虚构数据。若用户输入存在明显错误如地名拼写，将在 corrections 中给出 from/to 的纠正，并要求确认。"
                        "优先使用 YYYY-MM-DD 日期格式。"
                    )
                    resp = client.chat.completions.create(
                        model="doubao-1-5-thinking-vision-pro-250428",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": request.message},
                        ],
                        temperature=0.3,
                        max_tokens=1200,
                    )
                    content = resp.choices[0].message.content.strip()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        import re
                        m = re.search(r"\{[\s\S]*\}", content)
                        if m:
                            return json.loads(m.group())
                        return {"plan_needed": False, "message": "normal_chat"}

                intent = await loop.run_in_executor(None, analyze)
                step1_completed = json.dumps({'step': 1, 'status': 'completed', 'message': '需求分析完成', 'data': intent}, ensure_ascii=False)
                yield f"data: {step1_completed}\n\n"
                await asyncio.sleep(0.1)

                if not intent.get('plan_needed'):
                    yield f"data: {json.dumps({'type': 'final_response', 'content': '普通聊天'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                    return

                plan = intent.get('plan', {})
                required = ['destination', 'origin', 'start_date', 'end_date']
                missing = [k for k in required if not plan.get(k)]

                yield f"data: {json.dumps({'step': 2, 'status': 'running', 'message': '正在验证必填项...'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)

                if missing:
                    msg = '缺少必填项: ' + ', '.join(missing)
                    yield f"data: {json.dumps({'step': 2, 'status': 'error', 'message': msg}, ensure_ascii=False)}\n\n"
                    ask_text = '请补充以下信息：' + '、'.join(missing) + '。例如：目的地、出发地、开始时间(YYYY-MM-DD)、结束时间(YYYY-MM-DD)。'
                    yield f"data: {json.dumps({'type': 'ask', 'content': ask_text}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                    return

                yield f"data: {json.dumps({'step': 2, 'status': 'completed', 'message': '必填项已完整', 'data': plan}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)

                yield f"data: {json.dumps({'type': 'travel_json_start'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)
                json_text = json.dumps({
                    'destination': plan.get('destination'),
                    'origin': plan.get('origin'),
                    'start_date': plan.get('start_date'),
                    'end_date': plan.get('end_date'),
                    'people': plan.get('people'),
                    'attractions': plan.get('attractions')
                }, ensure_ascii=False)
                for i in range(0, len(json_text), 50):
                    yield f"data: {json.dumps({'type': 'travel_json_chunk', 'content': json_text[i:i+50]}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.02)
                yield f"data: {json.dumps({'type': 'travel_json_end'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

            except Exception as e:
                logger.error(f"旅行规划流式生成错误: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'content': f'处理请求时出错: {str(e)}'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(generate_travel_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"旅行规划接口错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        if not os.environ.get("ARK_API_KEY"):
            raise HTTPException(status_code=500, detail="ARK_API_KEY环境变量未设置")

        last_user_text = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                for item in msg.content:
                    if item.type == "text" and item.text:
                        last_user_text = item.text
                        break
                if last_user_text:
                    break

        INTENT_PROMPT = (
            "你是一位亲切、专业的旅行规划助手。只输出严格 JSON。\n"
            "输出类型：\n"
            "- 不需要规划：{\"type\": \"chat\", \"content\": \"...\"}\n"
            "- 需要规划：根据信息完整度二选一：\n"
            "  1) 必填（destination, origin, start_date, end_date）齐全：\n"
            "     输出 {\"type\": \"daily_plan_json\", \"plan\": {\"destination\":..., \"origin\":..., \"start_date\":..., \"end_date\":..., \"people\": 可选, \"attractions\": 可选数组}, \"itinerary\": [ {\"day\":1, \"date\":\"YYYY-MM-DD\", \"title\":\"Day 1\", \"activities\":[{\"name\":\"...\", \"notes\":\"...\"}], \"summary\":\"...\" } ... ], \"notes\": 可选字符串, \"corrections\": 可选数组[{from,to,reason}] }。\n"
            "  2) 缺少必填：仅在缺少必填时输出 {\"type\": \"ask\", \"question\": \"...\"}。\n"
            "可选项（people, attractions）未提供时不要提问；若提供 attractions，必须纳入行程但不局限于它们。\n"
            "不得编造具体票价/地址；日期用 YYYY-MM-DD。\n"
            "所有 activities 仅包含景点名称与可选 notes，不输出 time 字段。活动的 name 必须是单一、标准化的中文景点官方名称，不得包含斜杠、顿号或并列名称；不要输出组合名称或模糊标签。示例：使用‘天守阁’或‘大阪城公园’之一，不要‘西之丸庭园/大阪城周边闲游’。如需要说明从属关系或补充信息，写入 notes。"
        )

        intent_messages = [{"role": "system", "content": INTENT_PROMPT}]
        if request.system_prompt:
            intent_messages.append({"role": "system", "content": request.system_prompt})
        intent_messages.append({"role": "user", "content": last_user_text or ""})

        intent_resp = client.chat.completions.create(
            model=request.model,
            messages=intent_messages,
            temperature=0.3,
            max_tokens=4000,
        )
        intent_raw = intent_resp.choices[0].message.content.strip()
        try:
            intent_data = json.loads(intent_raw)
        except Exception:
            import re
            m = re.search(r"\{[\s\S]*\}", intent_raw)
            intent_data = json.loads(m.group()) if m else {"type": "chat", "content": intent_raw}

        itype = intent_data.get("type")
        if itype == "ask":
            return {"type": "ask", "content": intent_data.get("question", "请补充必填信息")}
        if itype == "daily_plan_json":
            return {
                "type": "daily_plan_json",
                "plan": intent_data.get("plan", {}),
                "itinerary": intent_data.get("itinerary", []),
                "notes": intent_data.get("notes"),
                "corrections": intent_data.get("corrections"),
            }
        if itype == "plan_json":
            return {"type": "plan_json", "plan": intent_data.get("plan", {})}
        if itype == "chat":
            content_txt = intent_data.get("content")
            if content_txt:
                return {"type": "chat", "content": content_txt}
            chat_resp = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI助手。"},
                    {"role": "user", "content": last_user_text or ""},
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            return {"type": "chat", "content": chat_resp.choices[0].message.content}

        return {"type": "chat", "content": intent_raw}

    except Exception as e:
        logger.error(f"聊天接口错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _amap_geocode_sync(name: str, city: Optional[str] = None):
    if not AMAP_KEY:
        raise RuntimeError("AMAP_KEY未设置")
    params = {"address": name, "key": AMAP_KEY}
    if city:
        params["city"] = city
    url = "https://restapi.amap.com/v3/geocode/geo?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("status") != "1" or not data.get("geocodes"):
        # 回退：使用POI关键字搜索
        sparams = {"keywords": name, "key": AMAP_KEY}
        if city:
            sparams["city"] = city
            sparams["citylimit"] = "true"
        surl = "https://restapi.amap.com/v3/place/text?" + urllib.parse.urlencode(sparams)
        with urllib.request.urlopen(surl, timeout=8) as sresp:
            sdata = json.loads(sresp.read().decode("utf-8"))
        if sdata.get("status") != "1" or not sdata.get("pois"):
            return None
        poi = sdata["pois"][0]
        loc = poi.get("location")
        if not loc:
            return None
        return {"name": name, "location": loc, "poi": poi.get("name")}
    gc = data["geocodes"][0]
    loc = gc.get("location")
    if not loc:
        return None
    return {"name": name, "location": loc}


def _amap_direction_sync(origin_loc: str, dest_loc: str, mode: str = "driving"):
    if not AMAP_KEY:
        raise RuntimeError("AMAP_KEY未设置")
    if mode == "walking":
        path = "/v3/direction/walking"
        params = {"origin": origin_loc, "destination": dest_loc, "key": AMAP_KEY}
    else:
        path = "/v3/direction/driving"
        params = {"origin": origin_loc, "destination": dest_loc, "key": AMAP_KEY}
    url = "https://restapi.amap.com" + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("status") != "1":
        return None
    route = data.get("route") or {}
    paths = route.get("paths") or []
    if not paths:
        return None
    p0 = paths[0]
    try:
        dist_m = int(p0.get("distance", 0))
        dur_s = int(p0.get("duration", 0))
    except Exception:
        return None
    km = round(dist_m / 1000, 1)
    minutes = max(1, round(dur_s / 60))
    return {"distance_km": km, "duration_min": minutes}


@app.post("/api/amap-route-test")
async def amap_route_test(req: RouteTestRequest):
    try:
        loop = asyncio.get_event_loop()
        def compute():
            o = _amap_geocode_sync(req.origin_name, req.city)
            d = _amap_geocode_sync(req.destination_name, req.city)
            if not o or not d:
                return {"success": False, "error": "geocode_failed", "origin": o, "destination": d}
            drv = _amap_direction_sync(o["location"], d["location"], req.mode or "driving")
            if not drv:
                return {"success": False, "error": "direction_failed", "origin": o, "destination": d}
            disp = f"🚗 {drv['distance_km']}km-{drv['duration_min']}分钟 >"
            return {"success": True, "origin": o, "destination": d, "route": drv, "display": disp}
        result = await loop.run_in_executor(None, compute)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        # 读取图片文件
        contents = await file.read()
        
        # 转换为base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        # 构造data URL
        image_url = f"data:{file.content_type};base64,{base64_image}"
        
        return {"image_url": image_url}
    
    except Exception as e:
        logger.error(f"图片上传错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
