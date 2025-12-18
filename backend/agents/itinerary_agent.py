import json
from openai import OpenAI
from models.user_profile import UserProfile, Itinerary
from services.knowledge_service import SPOTS, RESTAURANTS
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_URL
client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_URL)

async def itinerary_agent(user_profile: UserProfile, user_input: str):
    """根据用户的话，直接修改 JSON"""

    # 1. 获取当前状态
    current_plan = json.dumps(user_profile.itinerary.model_dump(), ensure_ascii=False) if user_profile.itinerary else "无"
    
    # 2. 简化数据喂给 LLM (避免 Token 溢出)
    spots_str = json.dumps([{"name": s["name"], "tags": s["tags"], "duration": s["duration_hours"]} for s in SPOTS], ensure_ascii=False)
    food_str = json.dumps([{"name": r["name"], "type": "餐厅"} for r in RESTAURANTS], ensure_ascii=False)

    prompt = f"""
你是一个行程数据维护员。请根据【用户指令】更新【当前行程JSON】。

【可用资源】
景点库：{spots_str}
餐厅库：{food_str}

【当前行程JSON】
{current_plan}

【用户指令】
"{user_input}"

【操作要求】
1. 如果是新规划，生成合理行程。
2. 如果用户说"饿了"，在合适时间插入餐厅。
3. 如果用户说"累了"，插入休息节点。
4. 如果用户指定地点，去库里找并替换/插入。
5. **重要**：修改后必须重新计算后续所有节点的 start 时间（顺延）。

【输出格式】
只输出标准 JSON，格式符合 Pydantic 模型。
"""

    completion = client.chat.completions.create(
        model=DASHSCOPE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    try:
        if completion.choices[0].message.content is None:
            raise ValueError("模型返回的 content 为 None")
        content = completion.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        # 直接覆盖原来的行程对象
        user_profile.itinerary = Itinerary(**data)
    except Exception as e:
        print(f"JSON生成出错: {e}")