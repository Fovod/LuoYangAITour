# AI服务统一调度入口

from agents.planner_agent import planner_agent
from agents.itinerary_agent import itinerary_agent
from agents.role_agent import role_agent
from services.knowledge_service import search_knowledge_base # 导入检索功能

async def ai_service(session, user_profile, user_input: str):
    
    # 1. Planner 依然负责路由
    decision = await planner_agent(user_input)
    intent = decision.get("intent", "chat")
    
    system_msg = ""

    # 2. 如果要改行程，还是交给 Itinerary Agent (它内部有全量列表，这里不用管)
    if intent == "update_plan":
        await itinerary_agent(user_profile, user_input)
        system_msg = "（系统提示：行程JSON已更新，请告知用户）"

    # 3. 【关键步骤】检索知识库 (RAG)
    # 不管是聊天还是改行程，都去库里搜一下有没有相关的知识点
    # 比如用户说“我想去龙门石窟”，这里就能把龙门石窟的历史和票价搜出来
    knowledge_context = search_knowledge_base(user_input)

    # 4. 调用 Role Agent，把搜到的知识喂给它
    reply = await role_agent(
        role=session.role, 
        user_input=user_input,
        knowledge=knowledge_context, # <--- 注入知识
        system_msg=system_msg
    )

    # 更新历史
    session.history.append({"sender": "user", "text": user_input})
    session.history.append({"sender": "ai", "text": reply})

    return reply