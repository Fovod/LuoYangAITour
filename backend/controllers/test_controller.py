from fastapi import APIRouter
from models.user_profile import UserProfile, UserBackground
from agents.planner_agent import planner_agent
from agents.itinerary_agent import itinerary_agent
from agents.adjuster_agent import adjuster_agent
from agents.role_agent import role_agent
from models.session_model import Session

router = APIRouter()

# 测试用户
test_user = UserProfile(
    user_id="test_user",
    background=UserBackground(days=1),
    preferences={"photo":0.2, "food":0.1},
    state=""
)
@router.post("/test_itinerary")
async def test_itinerary(data: dict):
    user_input = data.get("text", "")
    user = test_user

    # 1️⃣ 生成初始行程
    await itinerary_agent(user)
    initial_itinerary = user.model_dump().get("itinerary")

    # 2️⃣ 调整行程
    await adjuster_agent(user)
    adjusted_itinerary = user.model_dump().get("itinerary")

    # 3️⃣ 创建 Session 对象给 role_agent 使用
    session_obj = Session(
        session_id="test_session",
        role="李白",
        history=[]  # 必须初始化
    )

    # 4️⃣ 调用 role_agent
    reply = await role_agent(
        role=session_obj.role,
        plan={"action": "none", "detail": None},
        knowledge=None,
        session=session_obj
    )

    # 5️⃣ 返回偏好
    preferences = user.preferences

    return {
        "reply": reply,
        "initial_itinerary": initial_itinerary,
        "itinerary": adjusted_itinerary,
        "preferences": preferences
    }