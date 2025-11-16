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
                
                # 判断意图
                if intent_result.get("intent") == "chat":
                    # 普通聊天
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

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # 检查API密钥
        if not os.environ.get("ARK_API_KEY"):
            raise HTTPException(status_code=500, detail="ARK_API_KEY环境变量未设置")

        # 转换消息格式
        openai_messages = []
        for msg in request.messages:
            content = []
            for content_item in msg.content:
                if content_item.type == "text" and content_item.text:
                    content.append({"type": "text", "text": content_item.text})
                elif content_item.type == "image_url" and content_item.image_url:
                    content.append({"type": "image_url", "image_url": content_item.image_url})

            openai_messages.append({
                "role": msg.role,
                "content": content
            })

        # 添加系统提示词（如果提供）
        if request.system_prompt:
            # 在消息列表开头插入系统消息
            system_message = {
                "role": "system",
                "content": [{"type": "text", "text": request.system_prompt}]
            }
            openai_messages.insert(0, system_message)
        else:
            # 使用默认系统提示词
            default_system_prompt = "你是一个专业的AI助手，请按照以下要求回答用户问题。"
            
            system_message = {
                "role": "system", 
                "content": [{"type": "text", "text": default_system_prompt}]
            }
            openai_messages.insert(0, system_message)

        # 流式生成器函数
        async def generate_stream():
            try:
                # 准备API调用参数
                api_params = {
                    "model": request.model,
                    "messages": openai_messages,
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "stream": True
                }
                
                # 调用豆包API，流式响应
                stream = client.chat.completions.create(**api_params)
                
                for chunk in stream:
                    if chunk.choices:
                        choice = chunk.choices[0]
                        
                        # 处理思考过程（reasoning）
                        if hasattr(choice, 'delta') and hasattr(choice.delta, 'reasoning_content') and choice.delta.reasoning_content:
                            yield f"data: {json.dumps({'type': 'reasoning', 'content': choice.delta.reasoning_content}, ensure_ascii=False)}\n\n"
                        
                        # 处理正常内容
                        if hasattr(choice, 'delta') and hasattr(choice.delta, 'content') and choice.delta.content:
                            yield f"data: {json.dumps({'type': 'content', 'content': choice.delta.content}, ensure_ascii=False)}\n\n"
                        
                        # 检查是否完成
                        if choice.finish_reason:
                            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                            break
                
            except Exception as e:
                logger.error(f"流式生成错误: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'content': f'生成响应时出错: {str(e)}'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"聊天接口错误: {str(e)}")
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
