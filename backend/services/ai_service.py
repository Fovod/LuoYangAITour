# AI服务统一调度入口

from agents.planner_agent import planner_agent
from agents.itinerary_agent import itinerary_agent
from agents.role_agent import role_agent
from services.knowledge_service import search_knowledge_base

async def ai_service(session, user_profile, user_input: str):
    
    decision = await planner_agent(session, user_input)
    intent = decision.get("intent", "chat")
    
    system_msg = ""

    if intent == "update_plan":
        await itinerary_agent(user_profile, user_input)
        system_msg = "（系统提示：行程JSON已更新，请告知用户）"


    knowledge_context = await search_knowledge_base(user_input)

    current_plan_data = None
    if user_profile.itinerary is not None:
        current_plan_data = user_profile.itinerary.model_dump()

    # 调用 Role Agent，把搜到的知识喂给它
    reply = await role_agent(
        role=session.role, 
        user_input=user_input,
        knowledge=knowledge_context, # <--- 注入知识
        system_msg=system_msg,
        itinerary_data=current_plan_data
    )

    # 更新历史
    session.history.append({"sender": "user", "text": user_input})
    session.history.append({"sender": "ai", "text": reply})

    return reply