from openai import OpenAI
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_URL
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_URL
)

async def role_agent(role: str, plan: dict, knowledge, session):
    """根据Planner决策，用角色口吻生成文本"""
    history_text = ''
    if session.history:
        history_text = "\n".join(f"{m['sender']}: {m['text']}" for m in session.history[-5:]) if session.history else "无"
    prompt=f"""
你是洛阳历史角色 {role}，用角色口吻给用户建议。
【当前行动】{plan['action']}
【具体细节】{plan['detail']}
【知识库】{knowledge if knowledge else "无"}
【当前情况】
-角色：{session.role}
-时间：{session.time}
-地点：{session.location}
-历史记录：{history_text}
请输出不超过120字的中文回复，口吻符合角色，不对用户进行说教。
"""
    completion = client.chat.completions.create(
        model=DASHSCOPE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=False
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
