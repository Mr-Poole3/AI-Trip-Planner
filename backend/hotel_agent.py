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
INTENT_SYSTEM_PROMPT = """你是一个智能的旅行酒店推荐助手。你的任务是分析用户输入，判断是否需要进行"预订酒店"的搜索与推荐。

🆕 特别功能：如果用户提供了旅行计划，你需要：
- 当用户提到"第X天"、"第X晚"、"Day X"时，从旅行计划中提取对应日期和景点信息
- 推断合适的酒店位置：通常选择该天最后一个景点，或第二天第一个景点附近
- 自动提取入住和退房日期（第X天的日期为入住日期，第X+1天的日期为退房日期）
- 提取景点名称作为目的地关键词

严格要求：只有当用户明确表达"要预订/订酒店/订房/帮我订/我需要预定酒店"等明确的订房意图时，才将 `hotel-book` 设置为 true。
如果用户只是表达去旅行/去某地，但未明确说要"预订"，想找住宿/看看酒店/了解酒店信息，则将 `hotel-book` 设置为 false。

当 `hotel-book` 为 false 时，建议进行一次复问以确认是否需要预订，例如："是否需要我直接为您预订酒店（并搜索合适选项）？"但在本步骤的输出中只返回 JSON，不要包含复问文本。

请从用户输入和旅行计划中尽可能提取下列信息，并以 JSON 格式输出：

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

示例1（无旅行计划）：
用户："我想在成都春熙路附近找个酒店，11月13号入住，住一晚，两个人，帮我订"
输出：{"intent": "book_hotel", "hotel-book": true, "params": {"destination": "成都春熙路", "checkin_date": "2025-11-13", "checkout_date": "2025-11-14", "adults": 2}}

示例2（有旅行计划）：
旅行计划：
{
  "itinerary": [
    {"day": 1, "date": "2025-11-17", "activities": [{"name": "外滩"}, {"name": "城隍庙"}]},
    {"day": 2, "date": "2025-11-18", "activities": [{"name": "豫园"}, {"name": "南京路"}]}
  ]
}
用户："我需要预定第一日旅行的酒店"
分析：Day 1最后景点是"城隍庙"，Day 2第一个景点是"豫园"，两者相邻，适合住城隍庙或豫园附近
输出：{"intent": "book_hotel", "hotel-book": true, "params": {"destination": "城隍庙", "checkin_date": "2025-11-17", "checkout_date": "2025-11-18"}}

示例3（有旅行计划，指定天数）：
旅行计划：
{
  "itinerary": [
    {"day": 2, "date": "2025-11-18", "activities": [{"name": "迪士尼"}]},
    {"day": 3, "date": "2025-11-19", "activities": [{"name": "田子坊"}]}
  ]
}
用户："第二晚住哪里合适？"
分析：第二晚是Day 2的晚上，Day 2有迪士尼，第三天要去田子坊，迪士尼较远，建议住迪士尼附近
输出：{"intent": "book_hotel", "hotel-book": false, "params": {"destination": "迪士尼", "checkin_date": "2025-11-18", "checkout_date": "2025-11-19"}}

用户："我想去春熙路玩儿，看看附近有没有酒店"
输出：{"intent": "book_hotel", "hotel-book": false, "params": {"destination": "春熙路"}}

用户："今天天气怎么样？"
输出：{"intent": "chat", "message": "今天天气怎么样？", "hotel-book": false}"""

# 酒店推荐的系统提示词
RECOMMENDATION_SYSTEM_PROMPT = """你是一个专业的旅行酒店推荐顾问。你会收到用户的原始需求和搜索到的酒店列表。

🆕 特别功能：如果用户提供了旅行计划（包含每日行程、景点等信息），你需要：
- 深度分析行程中的景点分布和活动安排
- 推荐最符合行程路线的酒店位置
- 考虑每日活动的强度，推荐适合休息的酒店
- 如果跨越多个区域，建议在不同地点预订酒店以节省通勤时间
- 结合景点特点推荐主题相符的酒店（如商务区、文化景区、休闲度假等）

你的任务是：
1. 理解用户的需求和偏好（包括旅行计划）
2. 从提供的酒店列表中选择最合适的酒店（最多5个）
3. 为每个推荐的酒店提供详细的推荐理由
4. 按照推荐优先级排序

输出格式要求：
以友好、专业的语气输出推荐内容，包括：
- 简短的开场白，呼应用户需求（如果有旅行计划，要提及行程安排）
- 每个酒店的推荐（包括名称、价格、评分、位置、推荐理由）
- 如果有旅行计划，要说明酒店如何匹配行程路线
- 简短的总结建议

注意：
- 推荐理由要具体，结合酒店特点和用户需求
- 🆕 如果提供了旅行计划，推荐理由必须说明该酒店如何方便用户游览计划中的景点
- 语气要亲切、专业
- 如果酒店信息不完整，不要编造，可以说明信息待确认"""


class HotelAgent:
    """智能酒店推荐代理"""
    
    def __init__(self):
        self.client = client
    
    def analyze_intent(self, user_message: str, travel_plan: Optional[Dict] = None) -> Dict:
        """
        分析用户意图并提取参数
        
        Args:
            user_message: 用户消息
            travel_plan: 用户的旅行计划（可选）
        
        Returns:
            {"intent": "book_hotel", "params": {...}} 或
            {"intent": "chat", "message": "..."}
        """
        try:
            # 🆕 如果有旅行计划，添加到用户消息中
            user_content = user_message
            if travel_plan:
                travel_plan_json = json.dumps(travel_plan, ensure_ascii=False, indent=2)
                user_content = f"""用户消息：{user_message}

【用户的旅行计划】
```json
{travel_plan_json}
```

请结合旅行计划分析用户的酒店需求，从计划中提取目的地、日期等信息。"""
            
            response = self.client.chat.completions.create(
                model="doubao-1-5-thinking-vision-pro-250428",
                messages=[
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
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
    
    async def search_hotels(self, params: Dict) -> Dict:
        """
        搜索酒店（异步）
        
        Args:
            params: 搜索参数
        
        Returns:
            搜索结果
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔍 开始搜索酒店，参数: {params}")
            
            result = await search_hotel(
                destination=params.get("destination"),
                checkin_date=params.get("checkin_date"),
                checkout_date=params.get("checkout_date"),
                adults=params.get("adults", 2),
                children=params.get("children", 0),
                rooms=params.get("rooms", 1),
                children_ages=params.get("children_ages"),
                pets=params.get("pets", False)
            )
            
            logger.info(f"✅ 搜索完成，成功: {result.get('success')}, 酒店数: {len(result.get('hotels', []))}")
            if not result.get('success'):
                logger.error(f"❌ 搜索失败: {result.get('error')}")
            
            return result
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"❌ 搜索酒店时出现异常: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": f"搜索酒店时出错: {str(e)}",
                "hotels": []
            }
    
    def generate_recommendations(self, user_message: str, search_result: Dict, travel_plan: Optional[Dict] = None):
        """
        基于搜索结果生成酒店推荐（流式）
        
        Args:
            user_message: 用户原始消息
            search_result: 酒店搜索结果
            travel_plan: 用户的旅行计划（可选）
        
        Yields:
            推荐文本片段
        """
        try:
            # 构建提示
            hotels_info = json.dumps(search_result.get("hotels", []), ensure_ascii=False, indent=2)
            search_params = json.dumps(search_result.get("search_params", {}), ensure_ascii=False, indent=2)
            
            # 🆕 如果有旅行计划，添加到提示中
            travel_plan_context = ""
            if travel_plan:
                travel_plan_json = json.dumps(travel_plan, ensure_ascii=False, indent=2)
                travel_plan_context = f"""

【用户的旅行计划】
以下是用户已经规划好的旅行行程，请根据这个行程推荐最合适的酒店：
```json
{travel_plan_json}
```

注意事项：
- 根据行程中的景点位置，推荐交通便利的酒店
- 考虑每日的活动安排，推荐合适的酒店类型
- 如果行程跨越多天，建议是否需要在不同区域预订多家酒店
- 结合行程节奏，推荐适合休息的酒店
"""
            
            prompt = f"""用户需求：{user_message}

搜索参数：
{search_params}
{travel_plan_context}

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
