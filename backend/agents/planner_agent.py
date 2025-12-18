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
你是一个路由助手。请根据用户最新的话，判断是否需要【修改或生成行程表】。

【参考历史】
{history_text}

【用户最新输入】
"{user_input}"

【分类标准】
1. **update_plan** (需要修改):
   - 用户表达了需求变化（饿了、累了、想去哪、不喜欢哪、时间不够）。
   - 用户要求规划、重置、调整顺序。
   - 只要涉及行程表(JSON)的变动，都选这个。
   
2. **chat** (不需要修改):
   - 纯闲聊、问候、问历史知识、问天气。
   - 用户只是在询问当前行程细节，但没有要求改动。

【输出格式】
只输出 JSON: {{ "intent": "update_plan" 或 "chat" }}
"""
    
    completion = client.chat.completions.create(
        model=DASHSCOPE_MODEL,
        messages=[{"role":"user", "content":prompt}],
        stream=False
    )
    
    content = completion.choices[0].message.content
    
    # 清洗逻辑
    if content is None:
        raise ValueError("模型返回的 content 为 None")
    cleaned_content = content.replace("```json", "").replace("```", "").strip()
    
    try:
        result = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Planner JSON 解析失败")

    # 检查字段完整性
    if "intent" not in result:
        raise KeyError(f"[ERROR] Planner 返回了 JSON 但缺少 'intent' 字段: {result}")
        
    return result