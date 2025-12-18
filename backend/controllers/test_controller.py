from fastapi import APIRouter
from models.user_profile import UserProfile, UserBackground
from models.session_model import Session

# 导入三个核心 Agent
from agents.planner_agent import planner_agent      # 1. 大脑（路由）
from agents.itinerary_agent import itinerary_agent  # 2. 苦力（改JSON）
from agents.role_agent import role_agent            # 3. 嘴巴（说话）

router = APIRouter()

# 全局内存存储（模拟数据库，防止刷新页面后状态丢失）
GLOBAL_USER = UserProfile(
    user_id="test_user",
    background=UserBackground(days=1), # 默认1天
    preferences={},
    state=""
)

@router.post("/test_itinerary")
async def test_itinerary(data: dict):
    user_input = data.get("text", "")
    
    # --- 0. 初始化检查 ---
    # 如果用户没行程，且输入为空（或者是刚加载页面），强制初始化
    if not GLOBAL_USER.itinerary and not user_input:
        user_input = "帮我规划一个洛阳一日游"
        # 强制标记为 update_plan，让 Itinerary Agent 去初始化
        decision = {"intent": "update_plan"} 
    else:
        # --- 1. Planner 判断意图 ---
        decision = await planner_agent(user_input)
        print(f"🧠 Planner 决策: {decision}")

    reply = ""

    # --- 2. 根据意图分流 ---
    if decision["intent"] == "update_plan":
        # === 分支 A：修改行程 ===
        print("🔧 进入行程修改模式...")
        
        # 让 Itinerary Agent 根据用户的话修改 JSON
        await itinerary_agent(GLOBAL_USER, user_input)
        
        # 让 Role Agent 汇报结果 (带上用户原话作为上下文)
        reply = await role_agent(
            role="李白", 
            user_input=f"用户要求：'{user_input}'。系统已完成行程更新。请向用户汇报调整结果。"
        )

    else:
        # === 分支 B：纯闲聊 ===
        print("💬 进入闲聊模式...")
        
        # 直接让 Role Agent 陪聊，不动 JSON
        reply = await role_agent(
            role="李白", 
            user_input=user_input
        )

    # --- 3. 返回结果给前端 ---
    return {
        "reply": reply,
        # 返回最新的行程 JSON 给前端渲染
        "itinerary": GLOBAL_USER.model_dump().get("itinerary"),
        "debug_intent": decision # 方便前端调试看状态
    }