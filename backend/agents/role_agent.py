from openai import OpenAI
import sys, os, json
from typing import Optional, Dict, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_URL
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_URL
)

async def role_agent(role: str, user_input: str, knowledge: str = "", system_msg: str = "", itinerary_data: Optional[Dict[str, Any]] = None ):
    plan_str = "暂无已定行程"
    if itinerary_data:
        plan_str = json.dumps(itinerary_data, ensure_ascii=False)
    
    prompt = f"""
你现在是【洛阳导游 - {role}】。

【用户说】
"{user_input}"

【系统状态/行程变动】
{system_msg}

【当前实际行程表】
{plan_str}

【知识库资料】
{knowledge if knowledge else "暂无特定资料，请基于通识回答。"}

【回复要求】
1. 行程相关：
   - 如果用户问“我的行程是什么”、“接下来去哪”，必须严格基于【当前实际行程表】来回答，要提起具体时间。
   - 只有当用户明确询问时间安排、接下来去哪、我的行程是什么时，才复述【当前实际行程表】的内容。
   - 只有当【系统状态】里明确提示“行程已更新”时，你才需要告诉用户你调整了行程。
   - 如果【系统状态】为空，绝对不要说“行程已改”之类的话。

2. 响应用户意图：
   - 如果用户说“我到了”，请热情招呼，并根据【知识库资料】介绍这里的看点。
   - 如果用户问“讲讲xx”类似意思的话,请用{role}的口吻生动讲解历史典故。

3. 角色风格：
   - 说话要符合人设，且干练简洁，不超过100字。
   - 不要像个机器人一样复读指令，说话不要用符号，比如**、#等。
   - 在进行讲述行程的时候，不需要引用诗句，也不需要多余的修饰话语。
   - 每次回复最多在一个地方引用诗句，且只能引用一句。
"""

    completion = client.chat.completions.create(
        model=DASHSCOPE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7 
    )
    
    choice = completion.choices[0]
    if hasattr(choice, "message") and choice.message is not None and choice.message.content:
        text_output = choice.message.content
    else:
        # 如果 message 为空，尝试用 content 属性或返回默认
        text_output = getattr(choice, "content", "AI 没有生成回复")

    # 去除多余空格
    text_output = text_output.strip()
    return text_output

