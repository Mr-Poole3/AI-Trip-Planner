"""
智能酒店推荐代理
处理用户输入，识别意图，提取参数，搜索酒店，生成推荐
"""
import json
import os
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
from booking_hotel_search import search_hotel

load_dotenv()

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

# 意图识别和参数提取的系统提示词
INTENT_SYSTEM_PROMPT = """你是一个智能的旅行酒店推荐助手。你的任务是分析用户输入，判断是否需要进行“预订酒店”的搜索与推荐。

严格要求：只有当用户明确表达“要预订/订酒店/订房/帮我订/我需要预定酒店”等明确的订房意图时，才将 `hotel-book` 设置为 true。
如果用户只是表达去旅行/去某地，但未明确说要“预订”，想找住宿/看看酒店/了解酒店信息，则将 `hotel-book` 设置为 false。

当 `hotel-book` 为 false 时，建议进行一次复问以确认是否需要预订，例如：“是否需要我直接为您预订酒店（并搜索合适选项）？”但在本步骤的输出中只返回 JSON，不要包含复问文本。

请从用户输入中尽可能提取下列信息，并以 JSON 格式输出：

必填字段（在能识别时给出，否则省略）：
- destination (string): 目的地（城市、地区、酒店名称或地标）

可选字段：
- checkin_date (string): 入住日期，格式 YYYY-MM-DD
- checkout_date (string): 退房日期，格式 YYYY-MM-DD
- adults (number): 成人数量，默认 2
- children (number): 儿童数量，默认 0
- rooms (number): 房间数量，默认 1
- children_ages (array): 儿童年龄列表
- pets (boolean): 是否携带宠物，默认 false

输出格式要求（仅输出 JSON，不要输出任何其他文字）：
- 若涉及酒店或旅行相关需求，输出：
  {"intent": "book_hotel", "hotel-book": <true|false>, "params": { ... }}
- 若是与酒店无关的普通聊天，输出：
  {"intent": "chat", "message": "用户的原始消息", "hotel-book": false}

示例：
用户："我想在成都春熙路附近找个酒店，11月13号入住，住一晚，两个人，帮我订"
输出：{"intent": "book_hotel", "hotel-book": true, "params": {"destination": "成都春熙路", "checkin_date": "2025-11-13", "checkout_date": "2025-11-14", "adults": 2}}

用户："我想去春熙路玩儿，看看附近有没有酒店"
输出：{"intent": "book_hotel", "hotel-book": false, "params": {"destination": "春熙路"}}

用户："帮我找上海的酒店"
输出：{"intent": "book_hotel", "hotel-book": false, "params": {"destination": "上海"}}

用户："今天天气怎么样？"
输出：{"intent": "chat", "message": "今天天气怎么样？", "hotel-book": false}

用户："你好"
输出：{"intent": "chat", "message": "你好", "hotel-book": false}"""

# 酒店推荐的系统提示词
RECOMMENDATION_SYSTEM_PROMPT = """你是一个专业的旅行酒店推荐顾问。你会收到用户的原始需求和搜索到的酒店列表。

你的任务是：
1. 理解用户的需求和偏好
2. 从提供的酒店列表中选择最合适的酒店（最多5个）
3. 为每个推荐的酒店提供详细的推荐理由
4. 按照推荐优先级排序

输出格式要求：
以友好、专业的语气输出推荐内容，包括：
- 简短的开场白，呼应用户需求
- 每个酒店的推荐（包括名称、价格、评分、位置、推荐理由）
- 简短的总结建议

注意：
- 推荐理由要具体，结合酒店特点和用户需求
- 语气要亲切、专业
- 如果酒店信息不完整，不要编造，可以说明信息待确认"""


class HotelAgent:
    """智能酒店推荐代理"""
    
    def __init__(self):
        self.client = client
    
    def analyze_intent(self, user_message: str) -> Dict:
        """
        分析用户意图并提取参数
        
        Returns:
            {"intent": "book_hotel", "params": {...}} 或
            {"intent": "chat", "message": "..."}
        """
        try:
            response = self.client.chat.completions.create(
                model="doubao-1-5-thinking-vision-pro-250428",
                messages=[
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # 如果不是有效的JSON，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
                else:
                    # 无法解析，当作普通聊天
                    return {"intent": "chat", "message": user_message}
        
        except Exception as e:
            print(f"意图分析错误: {e}")
            return {"intent": "chat", "message": user_message}
    
    def search_hotels(self, params: Dict) -> Dict:
        """
        搜索酒店
        
        Args:
            params: 搜索参数
        
        Returns:
            搜索结果
        """
        try:
            result = search_hotel(
                destination=params.get("destination"),
                checkin_date=params.get("checkin_date"),
                checkout_date=params.get("checkout_date"),
                adults=params.get("adults", 2),
                children=params.get("children", 0),
                rooms=params.get("rooms", 1),
                children_ages=params.get("children_ages"),
                pets=params.get("pets", False)
            )
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"搜索酒店时出错: {str(e)}",
                "hotels": []
            }
    
    def generate_recommendations(self, user_message: str, search_result: Dict):
        """
        基于搜索结果生成酒店推荐（流式）
        
        Args:
            user_message: 用户原始消息
            search_result: 酒店搜索结果
        
        Yields:
            推荐文本片段
        """
        try:
            # 构建提示
            hotels_info = json.dumps(search_result.get("hotels", []), ensure_ascii=False, indent=2)
            search_params = json.dumps(search_result.get("search_params", {}), ensure_ascii=False, indent=2)
            
            prompt = f"""用户需求：{user_message}

搜索参数：
{search_params}

找到的酒店列表：
{hotels_info}

请从以上酒店中选择最合适的（最多5个），并生成专业的推荐。"""
            
            stream = self.client.chat.completions.create(
                model="doubao-1-5-thinking-vision-pro-250428",
                messages=[
                    {"role": "system", "content": RECOMMENDATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            yield f"生成推荐时出错: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """
        普通聊天
        
        Args:
            user_message: 用户消息
        
        Returns:
            回复内容
        """
        try:
            response = self.client.chat.completions.create(
                model="doubao-1-5-thinking-vision-pro-250428",
                messages=[
                    {"role": "system", "content": "你是一个友好的AI助手，可以回答各种问题。"},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"抱歉，我遇到了一些问题: {str(e)}"


if __name__ == "__main__":
    # 测试
    agent = HotelAgent()
    
    # 测试1: 酒店预订意图
    print("=== 测试1: 酒店预订 ===")
    test_message = "我想在成都春熙路附近找个酒店，11月13号入住，住一晚，两个人"
    intent_result = agent.analyze_intent(test_message)
    print(f"意图分析结果: {json.dumps(intent_result, ensure_ascii=False, indent=2)}")
    
    # 测试2: 普通聊天
    print("\n=== 测试2: 普通聊天 ===")
    test_message2 = "今天天气怎么样？"
    intent_result2 = agent.analyze_intent(test_message2)
    print(f"意图分析结果: {json.dumps(intent_result2, ensure_ascii=False, indent=2)}")
