# 决策智能体
# 输入：session、用户最新信息
# 输出：结构化决策

from openai import OpenAI
import json
from models.session_model import Session
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_URL
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_URL
)

async def planner_agent(session, user_input:str):
    """
    判断用户意图和行动
    输出：
    action:推荐餐厅 / 推荐景点 / 讲历史 / 随便聊天
    detail:景点或餐厅名称
    """
    history_text = ''
    if session.history:
        history_text = "\n".join(f"{m['sender']}: {m['text']}" for m in session.history[-5:]) if session.history else "无"

    prompt = f"""
你是洛阳旅游规划智能体（Planner）。
为了提供更好的导游服务，你还需要判断用户现在是否需要“知识支持”。
可选action：
- recommend_restaurant
- recommend_spot
- tell_history
- casual_chat

【当前情况】
-角色：{session.role}
-时间：{session.time}
-地点：{session.location}
-历史记录：{history_text}

【用户说】
{user_input}

【输出】
请只输出JSON：
{{
    "action":action名,
    "detail": "具体景点或餐厅名称，如无可留空"
}}
不要输出其他文字。
"""
    
    completion = client.chat.completions.create(
        model=DASHSCOPE_MODEL,
        messages=[{"role":"user", "content":prompt}],
        stream=False
    )
    choice = completion.choices[0]
    text_output = ""
    if hasattr(choice, "message") and choice.message and choice.message.content:
        text_output = choice.message.content
    else:
        text_output = getattr(choice, "content", "{}")
    try:
        action_json = json.loads(text_output)
    except:
        action_json = {"action": "casual_chat", "detail": ""}
    return action_json