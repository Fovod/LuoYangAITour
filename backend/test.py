# ————————测试数据模型（user_profile.py）————————
# from models.user_profile import UserProfile, UserBackground, Spot, DayPlan, Itinerary

# def test_user_profile():
#     user = UserProfile(
#         user_id="test1",
#         background=UserBackground(days=2, budget="中等", people="2人"),
#         state="需要休息",
#         preferences={"photo": 0.2}
#     )

#     # 创建简单行程
#     spots = [Spot(name="景点A", start="09:00", duration=2.0)]
#     day_plan = DayPlan(day=1, spots=spots)
#     itinerary = Itinerary(plan=[day_plan])
#     user.itinerary = itinerary

#     print(user.model_dump_json(indent=2))

# test_user_profile()

# ————————测试 itinerary_agent.py————————
# import asyncio
# from models.user_profile import UserProfile, UserBackground
# from agents.itinerary_agent import itinerary_agent

# async def test_itinerary_agent():
#     user = UserProfile(
#         user_id="test2",
#         background=UserBackground(days=2),
#         preferences={"photo":0.2, "food":0.1}
#     )

#     itinerary = await itinerary_agent(user)
#     print(itinerary.model_dump_json(indent=2))

# asyncio.run(test_itinerary_agent())



# ————————测试 ai_service.py————————
# import asyncio
# from models.user_profile import UserProfile, UserBackground, Spot, DayPlan, Itinerary
# from agents.adjuster_agent import adjuster_agent

# import asyncio
# from models.user_profile import UserProfile, UserBackground, Spot, DayPlan, Itinerary
# from agents.adjuster_agent import adjuster_agent

# async def test_adjuster():
#     # 构建初始行程
#     spots = [
#         Spot(name="景点A", start="09:00", duration=2.0),
#         Spot(name="景点B", start="11:00", duration=2.0)
#     ]
#     day_plan = DayPlan(day=1, spots=spots)
#     itinerary = Itinerary(plan=[day_plan])

#     #构建用户对象
#     user = UserProfile(
#         user_id="test3",
#         background=UserBackground(days=1),
#         state="需要休息",  # 触发休息调整逻辑
#         itinerary=itinerary
#     )

#     # 调用 adjuster_agent
#     new_itinerary = await adjuster_agent(user)

#     #打印结果（兼容 Pydantic v1/v2）
#     if new_itinerary is None:
#         print("行程为空，未做调整")
#         return

#     if hasattr(new_itinerary, "model_dump_json"):
#         # Pydantic v2
#         print(new_itinerary.model_dump_json(indent=2))
#     else:
#         # Pydantic v1
#         print(new_itinerary.json(indent=2))

# #运行异步测试
# if __name__ == "__main__":
#     asyncio.run(test_adjuster())


# ——————————测试 user_agent.py——————————
# import asyncio
# from models.user_profile import UserProfile, UserBackground
# from agents.user_agent import user_agent

# async def test_user_agent():
#     user = UserProfile(
#         user_id="test4",
#         background=UserBackground(days=1),
#         state=None,
#         preferences={}
#     )

#     user_input = "我今天想拍照"
#     result = await user_agent(user, user_input)
#     print(result)
#     print(user.model_dump_json(indent=2))

# asyncio.run(test_user_agent())




#——————————测试 ai_service.py——————————
# test_ai_service.py
import asyncio
import json
from models.user_profile import UserProfile, UserBackground, Spot, DayPlan, Itinerary
from models.session_model import Session
from services.ai_service import ai_service
from agents.itinerary_agent import itinerary_agent
from agents.adjuster_agent import adjuster_agent

async def test_ai_service():
    user = UserProfile(
        user_id="test_user",
        background=UserBackground(days=2),
        preferences={"photo":0.2, "food":0.1},
        state="需要休息"
    )

    session = Session(
        session_id="test_session",
        role="导游",
        history=[]
    )

    # 生成初始行程
    await itinerary_agent(user)
    print("初始行程:")
    print(json.dumps(user.model_dump(), indent=2, ensure_ascii=False))

    # 调整行程
    await adjuster_agent(user)
    print("\n调整后行程:")
    print(json.dumps(user.model_dump(), indent=2, ensure_ascii=False))

    # AI 回复
    user_input = "我饿了，想找好吃的"
    reply = await ai_service(session, user_input)
    print("\nAI 回复:", reply)
    print("\n会话历史:", session.history)

if __name__ == "__main__":
    asyncio.run(test_ai_service())
