import json
from openai import OpenAI
from models.user_profile import UserProfile
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_URL
client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_URL)

async def inquiry_agent(user_profile: UserProfile, user_input:str):
    """从用户输入中提取信息填入UserBackgournd,若信息不全，生成追问的问题"""
    bg = user_profile.background

    extract_prompt = f"""
你是一个信息提取助手。请根据用户最新的话，更新用户背景信息。

【当前背景】
{bg.model_dump_json()}

【用户输入】
"{user_input}"

【任务】
1. 分析用户输入，提取：days(天数), people_count(人数), people_type(情侣/亲子/独行等), budget(预算), pace(节奏)。
2. 只更新用户提到的字段，没提到的保持原样。
3. 如果用户说"随便"、"不限"，也请填入"默认/适中"。

【输出格式】
只输出 JSON，包含需要更新的字段即可。例如: {{ "days": 2, "people_type": "情侣" }}
"""
    try:
        completion = client.chat.completions.create(
            model=DASHSCOPE_MODEL,
            messages=[{"role": "user", "content": extract_prompt}],
            temperature=0.1
        )

        if completion.choices[0].message.content is None:
            raise ValueError("inquiry_agent内容为空")
        content = completion.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        updates = json.loads(content)

        bg_dict = bg.model_dump()
        bg_dict.update(updates)
        for k, v in updates.items():
            if hasattr(bg, k):
                setattr(bg, k, v)
    except Exception as e:
        print(f"用户信息打听失败：{e}")

    # —————— 判断是否需要追问 ————————
    if not bg.is_complete():
        ask_prompt = f"""
你是一个专业的旅行顾问。用户想去洛阳玩，但缺少关键信息。
当前已知：{bg.model_dump_json(exclude={'asked_fields'})}
核心缺口：天数(days)、人群类型(people_type)。

请用亲切、自然的口吻，追问用户缺失的信息。一次只问 1-2 个最重要的问题，不要像查户口。
"""
        completion = client.chat.completions.create(
                model=DASHSCOPE_MODEL,
                messages=[{"role": "user", "content": extract_prompt}],
                temperature=0.7
            )
        return {"action":"ask", "reply": completion.choices[0].message.content}

    return {"action":"ready", "reply":None}
