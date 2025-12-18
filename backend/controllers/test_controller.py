from fastapi import APIRouter
from models.user_profile import UserProfile, UserBackground
from models.session_model import Session

# 导入所有组件
from agents.planner_agent import planner_agent
from agents.itinerary_agent import itinerary_agent
from agents.role_agent import role_agent
from services.knowledge_service import search_knowledge_base

router = APIRouter()

# --- 全局存储 (模拟数据库) ---
# 1. 存储用户行程
GLOBAL_USER = UserProfile(
    user_id="test_user",
    background=UserBackground(days=1),
    preferences={},
    state=""
)

# 2. 【新增】存储会话状态 (历史记录)
GLOBAL_SESSION = Session(
    session_id="test_session_001",
    role="李白",
    location="洛阳",
    history=[] 
)

@router.post("/test_itinerary")
async def test_itinerary(data: dict):
    user_input = data.get("text", "")
    
    # --- 0. 初始化兜底 ---
    if not GLOBAL_USER.itinerary and not user_input:
        user_input = "帮我规划一个洛阳一日游"
        decision = {"intent": "update_plan"} 
    else:
        # --- 1. Planner 判断意图 ---
        decision = await planner_agent(GLOBAL_SESSION, user_input)
        print(f"🧠 Planner 决策: {decision}")

    # 定义系统提示词 (用于告诉 Role Agent 发生了什么)
    system_msg = ""

    # --- 2. 分支处理 ---
    if decision["intent"] == "update_plan":
        print("🔧 进入行程修改模式...")
        # 调用 Itinerary Agent 修改 JSON
        await itinerary_agent(GLOBAL_USER, user_input)
        system_msg = "（系统提示：行程数据已根据用户要求更新完毕。）"
    else:
        print("💬 进入闲聊模式...")
        system_msg = ""

    # --- 3. 知识库检索 (RAG) ---
    knowledge_context = search_knowledge_base(user_input)

    # --- 4. Role Agent 生成回复 ---
    reply = await role_agent(
        role="李白", 
        user_input=user_input,
        knowledge=knowledge_context,
        system_msg=system_msg
    )

    # --- 5. 返回结果 ---
    return {
        "reply": reply,
        "itinerary": GLOBAL_USER.model_dump().get("itinerary"),
        "debug_intent": decision
    }