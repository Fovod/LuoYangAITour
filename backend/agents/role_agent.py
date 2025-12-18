from openai import OpenAI
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_URL
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_URL
)

async def role_agent(role: str, user_input: str, knowledge: str = "", system_msg: str = ""):
    prompt = f"""
你现在是【洛阳导游 - {role}】，用角色口吻给用户建议。
【回复要求】
1. 必须包含实质性信息：直接告诉用户你已经把行程改了，改了哪里。
2. 不要废话：不要吟诗作对超过一句，不要讲莫名其妙的大道理。
3. 语气风格：说话要干练、热情。可以在最后加上一句符合 {role} 风格的感叹（比如李白可以说一句“妙哉”或引用半句诗），但只能作为点缀。

【知识库资料】(必须严格基于此回答，严禁编造数据)
{knowledge if knowledge else "暂无特定资料，请基于通识回答。"}

【系统状态】
{system_msg}

【用户说】
"{user_input}"

【回复要求】
1. 如果【知识库资料】里有相关数据（如票价、历史典故、餐厅特色），请务必引用。
2. 保持{role}的口吻，但不要因为扮演角色而忽略了 factual (事实) 信息。
3. 如果用户问行程，记得结合系统状态回复。
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

