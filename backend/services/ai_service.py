# AI服务统一调度入口

from agents.planner_agent import planner_agent
from agents.itinerary_agent import itinerary_agent
from agents.adjuster_agent import adjuster_agent
from agents.role_agent import role_agent
from models.user_profile import UserProfile
from services.knowledge_service import(recommend_restaurant, recommend_spot, tell_history)


async def ai_service(session, user_input:str):
    #1. 调用planner决策
    plan = await planner_agent(session, user_input)

    #2. 根据planner决策查询知识库
    target = plan.get("detail")
    if plan["action"] == "recommend_restaurant":
        knowledge = recommend_restaurant()
    elif plan["action"] == "recommend_spot":
        knowledge = recommend_spot(keyword=target or '')
    elif plan["action"] == "tell_history":
        knowledge = tell_history(spot_name=target or '')
    else:
        knowledge = None

    #3. 调用role agent生成回复
    reply = await role_agent(role=session.role, plan=plan, knowledge=knowledge, session=session)

    #4. 更新会话历史
    session.history.append({"sender":"user", "text": user_input})
    session.history.append({"sender":"ai", "text":reply})

    return reply