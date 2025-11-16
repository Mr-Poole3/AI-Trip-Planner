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

def extract_first_json(text: str) -> dict:
    """提取第一个有效的JSON对象（支持嵌套数组和对象）"""
    # 1. 直接尝试解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 2. 查找JSON对象（使用栈匹配括号，支持数组）
    import re
    start_idx = text.find('{')
    if start_idx == -1:
        return {"type": "chat", "content": text}
    
    # 使用栈来跟踪所有类型的括号
    bracket_stack = []
    in_string = False
    escape = False
    
    for i in range(start_idx, len(text)):
        char = text[i]
        
        if escape:
            escape = False
            continue
            
        if char == '\\':
            escape = True
            continue
            
        if char == '"':
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                bracket_stack.append('{')
            elif char == '[':
                bracket_stack.append('[')
            elif char == '}':
                if bracket_stack and bracket_stack[-1] == '{':
                    bracket_stack.pop()
                    if len(bracket_stack) == 0:
                        # 找到完整的JSON对象
                        json_str = text[start_idx:i+1]
                        try:
                            return json.loads(json_str)
                        except Exception as e:
                            logger.error(f"JSON解析失败: {e}, 内容: {json_str[:200]}...")
                            pass
                        break
            elif char == ']':
                if bracket_stack and bracket_stack[-1] == '[':
                    bracket_stack.pop()
    
    # 3. 如果栈匹配失败，尝试直接解析整个文本
    try:
        return json.loads(text)
    except:
        pass
    
    # 4. 返回原始内容作为聊天
    logger.warning(f"无法解析JSON，返回聊天模式")
    return {"type": "chat", "content": text}

class TravelPlanRequest(BaseModel):
    message: str

class MessageContent(BaseModel):
    type: str  # "text" or "image_url"
    text: Optional[str] = None
    image_url: Optional[dict] = None

class ChatMessage(BaseModel):
    role: str
    content: List[MessageContent]

class TravelPlanDraft(BaseModel):
    destination: Optional[str] = None
    origin: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    people: Optional[int] = None
    attractions: Optional[List[str]] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "doubao-1-5-thinking-vision-pro-250428"
    system_prompt: Optional[str] = None  # 系统提示词
    travel_draft: Optional[TravelPlanDraft] = None  # 旅行计划草稿

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

class BatchGeocodeRequest(BaseModel):
    places: List[str]  # 景点名称列表
    city: Optional[str] = None

class RouteDirectRequest(BaseModel):
    origin_coords: List[float]  # [lng, lat]
    destination_coords: List[float]  # [lng, lat]
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    mode: Optional[str] = "driving"


class MultiModeRouteRequest(BaseModel):
    """一次性获取三种出行方式的路线"""
    origin_coords: List[float]  # [lng, lat]
    destination_coords: List[float]  # [lng, lat]
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    city: str  # 公交路线需要城市参数（必填，不能有默认值）


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

        # 检查是否是生成计划的特殊请求
        if last_user_text == "__GENERATE_PLAN__" and request.travel_draft:
            draft = request.travel_draft.dict()
            logger.info(f"📍 收到生成计划请求，草稿内容: {json.dumps(draft, ensure_ascii=False)}")
            if draft.get("destination") and draft.get("origin") and draft.get("start_date") and draft.get("end_date"):
                logger.info("✅ 必填字段验证通过，开始生成计划...")
                
                # 构建计划生成提示词
                PLAN_GENERATION_PROMPT = (
                    "你是专业的旅行规划师，根据用户需求生成详细的每日行程。\n"
                    "\n【输出格式】严格JSON，无任何额外文字！\n"
                    f"\n【用户需求】\n{json.dumps(draft, ensure_ascii=False, indent=2)}\n"
                    "\n【任务】\n"
                    "基于以上信息，生成完整的每日旅行计划。\n"
                    "输出格式：{\"type\":\"daily_plan_json\",\"plan\":{...},\"itinerary\":[...]}\n"
                    "\n【行程规划规则】\n"
                    "1. 如果用户指定了景点（attractions），必须包含在行程中，但不局限于它们\n"
                    "2. 如果用户没指定景点，你要根据目的地推荐热门景点\n"
                    "3. 排期规则：\n"
                    "   - 全天景点（游乐园/爬山等）：单独安排一天\n"
                    "   - 城市打卡类（寺庙/博物馆等）：每天安排3-4个，保持相邻景点可步行或短途通勤\n"
                    "4. 每天行程包含：\n"
                    "   - day: 天数\n"
                    "   - date: 日期（YYYY-MM-DD）\n"
                    "   - title: 标题（如\"Day 1\"）\n"
                    "   - activities: [{\"name\":\"景点名\", \"notes\":\"可选说明\"}]\n"
                    "   - summary: 当天总结（交通方式、注意事项等）\n"
                    "5. 活动名称必须是单一、标准化的中文景点官方名称\n"
                    "6. plan字段包含：destination, origin, start_date, end_date, people（默认2），**city（必填）**\n"
                    "\n【重要：城市识别】\n"
                    "- 必须在plan中添加\"city\"字段\n"
                    "- 分析目的地(destination)，提取所属的**城市名称**\n"
                    "- 例如：destination=\"上海迪士尼\" → city=\"上海\"\n"
                    "- 例如：destination=\"西湖\" → city=\"杭州\"\n"
                    "- 例如：destination=\"北京\" → city=\"北京\"\n"
                    "- city字段用于公交路线查询，必须是标准的城市名称（不带\"市\"字）\n"
                    "\n再次强调：只输出JSON！"
                )
                
                plan_messages = [
                    {"role": "system", "content": PLAN_GENERATION_PROMPT},
                    {"role": "user", "content": f"请为我规划{draft.get('destination')}的旅行，从{draft.get('start_date')}到{draft.get('end_date')}。"}
                ]
                
                if request.system_prompt:
                    plan_messages.insert(1, {"role": "system", "content": request.system_prompt})
                
                # 调用LLM生成计划
                plan_resp = client.chat.completions.create(
                    model=request.model,
                    messages=plan_messages,
                    temperature=0.7,
                    max_tokens=4000,
                )
                
                plan_raw = plan_resp.choices[0].message.content.strip()
                logger.info(f"🤖 LLM返回原始内容长度: {len(plan_raw)} 字符")
                logger.info(f"🤖 LLM返回原始内容（前500字符）: {plan_raw[:500]}...")
                
                plan_data = extract_first_json(plan_raw)
                if plan_data:
                    logger.info(f"📊 解析后的JSON类型: {plan_data.get('type')}")
                else:
                    logger.error(f"❌ JSON解析返回None！原始内容: {plan_raw}")
                
                # 返回生成的计划
                if plan_data.get("type") == "daily_plan_json":
                    logger.info("✅ 成功生成每日计划！")
                    return {
                        "type": "daily_plan_json",
                        "plan": plan_data.get("plan", draft),
                        "itinerary": plan_data.get("itinerary", []),
                        "notes": plan_data.get("notes"),
                        "corrections": plan_data.get("corrections"),
                    }
                else:
                    logger.error(f"❌ 计划生成失败，返回类型错误: {plan_data.get('type')}")
                    return {"type": "chat", "content": "计划生成失败，请重试"}

        # 构建提示词 - 支持草稿模式
        draft_info = ""
        has_draft = request.travel_draft and any([
            request.travel_draft.destination,
            request.travel_draft.origin,
            request.travel_draft.start_date,
            request.travel_draft.end_date
        ])
        
        if has_draft:
            draft_dict = request.travel_draft.dict(exclude_none=True)
            draft_info = f"\n\n【当前收集到的信息】（用户正在逐步提供）：\n{json.dumps(draft_dict, ensure_ascii=False, indent=2)}"
        
        INTENT_PROMPT = (
            "你是旅行规划助手，职责：收集旅行必填信息。\n"
            f"{draft_info}\n"
            "\n【输出格式】严格JSON，无任何额外文字！\n"
            "正确：{\"type\":\"chat\",\"content\":\"...\"}\n"
            "错误：好的，{...}（不要任何前后文字）\n"
            "\n【输出类型】\n"
            "1. 普通聊天：{\"type\":\"chat\",\"content\":\"...\"}\n"
            "2. 收集信息：{\"type\":\"draft_update\",\"updates\":{...},\"draft\":{...},\"missing_required\":[...],\"is_complete\":true/false,\"next_question\":\"...\"}\n"
            "\n【核心规则 - 重要】\n"
            "你只负责收集4个必填字段：\n"
            "1. destination - 目的地城市\n"
            "2. origin - 出发地城市\n"
            "3. start_date - 开始日期（YYYY-MM-DD）\n"
            "4. end_date - 结束日期（YYYY-MM-DD）\n"
            "\n【可选字段 - 不要追问】\n"
            "- people：人数（用户提到就记录，没提到就null）\n"
            "- attractions：景点列表（用户提到就记录，没提到就null或[]）\n"
            "❌ 绝对不要主动询问：\"还想去哪些景点\"、\"想去什么地方\"\n"
            "✅ 用户没提景点很正常，我们会自动推荐\n"
            "\n【判断完成】\n"
            "当4个必填字段都有值时：\n"
            "- 设置 is_complete = true\n"
            "- next_question 可以是确认信息，如：\"好的，已收集完成！正在为您规划行程...\"\n"
            "\n【合并逻辑】\n"
            "- 提取用户新输入中的字段\n"
            "- 与草稿合并（不覆盖已有非空字段）\n"
            "- 缺少必填字段时，自然追问（只问缺的）\n"
            "\n再次强调：只输出JSON！"
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
        logger.info(f"🤖 需求分析LLM返回长度: {len(intent_raw)} 字符")
        logger.info(f"🤖 需求分析LLM返回（前500字符）: {intent_raw[:500]}...")
        
        # 健壮的JSON解析逻辑
        intent_data = extract_first_json(intent_raw)
        if intent_data:
            logger.info(f"📊 解析后的意图类型: {intent_data.get('type')}")
        else:
            logger.error(f"❌ 需求分析JSON解析返回None！原始内容: {intent_raw}")

        itype = intent_data.get("type")
        
        # 草稿更新模式
        if itype == "draft_update":
            is_complete = intent_data.get("is_complete", False)
            draft = intent_data.get("draft", {})
            logger.info(f"📝 草稿更新 - 完成状态: {is_complete}, 草稿: {json.dumps(draft, ensure_ascii=False)}")
            
            # 返回草稿更新（即使完成也先返回，让前端展示进度）
            return {
                "type": "draft_update",
                "updates": intent_data.get("updates", {}),
                "draft": draft,
                "missing_required": intent_data.get("missing_required", []),
                "is_complete": is_complete,
                "next_question": intent_data.get("next_question", ""),
            }
        
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


def _amap_direction_sync(origin_loc: str, dest_loc: str, mode: str = "driving", city: str = None):
    """获取路径规划（支持驾车、步行、公交）"""
    if not AMAP_KEY:
        raise RuntimeError("AMAP_KEY未设置")
    
    if mode == "walking":
        path = "/v3/direction/walking"
        params = {"origin": origin_loc, "destination": dest_loc, "key": AMAP_KEY}
    elif mode == "transit":
        # 公交路线规划（使用动态城市参数）
        if not city:
            logger.warning("⚠️ 公交路线查询缺少城市参数")
            return None
        path = "/v3/direction/transit/integrated"
        params = {
            "origin": origin_loc, 
            "destination": dest_loc, 
            "key": AMAP_KEY,
            "city": city,  # 🆕 使用动态传递的城市参数
            "cityd": city
        }
    else:
        path = "/v3/direction/driving"
        params = {"origin": origin_loc, "destination": dest_loc, "key": AMAP_KEY}
    
    url = "https://restapi.amap.com" + path + "?" + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"高德API请求失败: {e}")
        return None
    
    if data.get("status") != "1":
        logger.error(f"高德API返回错误: {data.get('info')}")
        return None
    
    # 解析不同模式的返回数据
    if mode == "transit":
        # 公交路线解析
        route = data.get("route") or {}
        transits = route.get("transits") or []
        if not transits:
            return None
        t0 = transits[0]
        try:
            dist_m = int(t0.get("distance", 0))
            dur_s = int(t0.get("duration", 0))
            # 提取换乘信息
            segments = t0.get("segments", [])
            steps = []
            for seg in segments:
                bus_lines = seg.get("bus", {}).get("buslines", [])
                if bus_lines:
                    bus = bus_lines[0]
                    steps.append({
                        "type": "bus",
                        "name": bus.get("name", "公交"),
                        "via_stops": bus.get("via_num", 0)
                    })
                walking = seg.get("walking", {})
                if walking and walking.get("distance"):
                    walk_dist = int(walking.get("distance", 0))
                    if walk_dist > 0:
                        steps.append({
                            "type": "walk",
                            "distance": round(walk_dist / 1000, 2)
                        })
        except Exception as e:
            logger.error(f"解析公交路线失败: {e}")
            return None
        
        km = round(dist_m / 1000, 1)
        minutes = max(1, round(dur_s / 60))
        return {
            "distance_km": km, 
            "duration_min": minutes,
            "steps": steps if mode == "transit" else None
        }
    else:
        # 驾车/步行路线解析
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
        
        # 提取详细步骤（用于展开显示）- 显示完整步骤
        steps = []
        if mode in ["driving", "walking"]:
            for step in p0.get("steps", []):  # 显示所有步骤
                instruction = step.get("instruction", "")
                road = step.get("road", "")
                distance = step.get("distance", "")
                if instruction or road:  # 只要有指引或道路名就显示
                    steps.append({
                        "instruction": instruction or f"沿{road}行驶",
                        "road": road,
                        "distance": distance
                    })
        
        return {
            "distance_km": km, 
            "duration_min": minutes,
            "steps": steps if steps else None
        }


@app.post("/api/batch-geocode")
async def batch_geocode(req: BatchGeocodeRequest):
    """批量获取景点地理编码"""
    try:
        loop = asyncio.get_event_loop()
        def compute():
            results = []
            for place_name in req.places:
                try:
                    geo = _amap_geocode_sync(place_name, req.city)
                    if geo and geo.get("location"):
                        coords = [float(x) for x in geo["location"].split(",")]
                        results.append({
                            "name": place_name,
                            "success": True,
                            "coords": coords,  # [lng, lat]
                            "address": geo.get("poi", place_name)
                        })
                    else:
                        results.append({
                            "name": place_name,
                            "success": False,
                            "error": "geocode_failed"
                        })
                except Exception as e:
                    results.append({
                        "name": place_name,
                        "success": False,
                        "error": str(e)
                    })
            return {"success": True, "results": results}
        result = await loop.run_in_executor(None, compute)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/amap-route-direct")
async def amap_route_direct(req: RouteDirectRequest):
    """直接使用坐标计算路线（避免重复地理编码）"""
    try:
        loop = asyncio.get_event_loop()
        def compute():
            # 坐标格式转换：[lng, lat] -> "lng,lat"
            origin_loc = f"{req.origin_coords[0]},{req.origin_coords[1]}"
            dest_loc = f"{req.destination_coords[0]},{req.destination_coords[1]}"
            
            # 直接调用路线规划
            drv = _amap_direction_sync(origin_loc, dest_loc, req.mode or "driving")
            if not drv:
                return {"success": False, "error": "direction_failed"}
            
            disp = f"🚗 {drv['distance_km']}km-{drv['duration_min']}分钟 >"
            return {
                "success": True,
                "route": drv,
                "display": disp,
                "origin_name": req.origin_name,
                "destination_name": req.destination_name
            }
        result = await loop.run_in_executor(None, compute)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/multi-mode-route")
async def multi_mode_route(req: MultiModeRouteRequest):
    """一次性获取三种出行方式（驾车、步行、公交）的路线"""
    try:
        loop = asyncio.get_event_loop()
        def compute():
            # 坐标格式转换
            origin_loc = f"{req.origin_coords[0]},{req.origin_coords[1]}"
            dest_loc = f"{req.destination_coords[0]},{req.destination_coords[1]}"
            
            results = {}
            
            # 1. 驾车路线
            driving = _amap_direction_sync(origin_loc, dest_loc, "driving")
            if driving:
                results["driving"] = {
                    "distance_km": driving["distance_km"],
                    "duration_min": driving["duration_min"],
                    "display": f"🚗 {driving['distance_km']}km · {driving['duration_min']}分钟",
                    "steps": driving.get("steps")
                }
            
            # 2. 步行路线
            walking = _amap_direction_sync(origin_loc, dest_loc, "walking")
            if walking:
                results["walking"] = {
                    "distance_km": walking["distance_km"],
                    "duration_min": walking["duration_min"],
                    "display": f"🚶 {walking['distance_km']}km · {walking['duration_min']}分钟",
                    "steps": walking.get("steps")
                }
            
            # 3. 公交路线（使用前端传递的城市参数）
            transit = _amap_direction_sync(origin_loc, dest_loc, "transit", req.city)
            if transit:
                results["transit"] = {
                    "distance_km": transit["distance_km"],
                    "duration_min": transit["duration_min"],
                    "display": f"🚌 {transit['distance_km']}km · {transit['duration_min']}分钟",
                    "steps": transit.get("steps")
                }
            
            return {
                "success": True,
                "origin_name": req.origin_name,
                "destination_name": req.destination_name,
                "routes": results
            }
        
        result = await loop.run_in_executor(None, compute)
        return result
    except Exception as e:
        logger.error(f"多模式路线规划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
            # 解析经纬度坐标
            origin_coords = [float(x) for x in o["location"].split(",")]
            destination_coords = [float(x) for x in d["location"].split(",")]
            return {
                "success": True, 
                "origin": o, 
                "destination": d, 
                "route": drv, 
                "display": disp,
                "origin_coords": origin_coords,  # [lng, lat]
                "destination_coords": destination_coords  # [lng, lat]
            }
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
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
