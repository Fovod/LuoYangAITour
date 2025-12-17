from openai import OpenAI
import json
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_URL
from models.user_profile import UserProfile
from utils.profile_utils import update_state, update_preference

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_URL
)

async def user_agent(user_profile: UserProfile, user_input: str):
    """
    用 LLM 判断用户短期状态 & 长期偏好变化
    """
    prompt = f"""
你是一个【用户状态与偏好识别智能体】。
你的任务是：从用户的话中，判断是否透露了【短期状态】或【长期偏好】。

【可选短期状态 state】（只能选一个或 null）：
- 需要休息
- 想拍照
- 想吃东西
- 想要安静
- 想热闹
- null

【长期偏好 preference】
- 用“标签:权重增量”表示，如 photo:0.2 food:0.1
- 权重范围 0.1 ~ 0.3
- 如果没有明确偏好，不要编

【用户基本背景】
- 行程天数：{user_profile.background.days}
- 预算：{user_profile.background.budget}
- 人群：{user_profile.background.people}
- 当前状态：{user_profile.state}

【用户说的话】
{user_input}

【输出要求】
- 只输出 JSON
- 不要解释
- 不要输出多余文本

JSON格式：
{{
  "state": "... or null",
  "state_confidence": 0.0,
  "preference_updates": {{
    "tag": weight
  }}
}}
"""

    completion = client.chat.completions.create(
        model=DASHSCOPE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )

    if completion.choices[0].message.content is not None:
        text_output = completion.choices[0].message.content.strip()

    try:
        result = json.loads(text_output)
    except Exception:
        return {"used": False}

    # 状态更新
    state = result.get("state")
    confidence = result.get("state_confidence", 0)

    if state and confidence >= 0.7:
        update_state(user_profile, state)

    #偏好更新
    prefs = result.get("preference_updates", {})
    for tag, weight in prefs.items():
        if isinstance(weight, (int, float)) and 0 < weight <= 0.5:
            update_preference(user_profile, tag, weight)

    return {
        "used": True,
        "state": state,
        "confidence": confidence,
        "preferences": prefs
    }
