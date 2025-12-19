from fastapi import APIRouter
from models.user_profile import UserProfile, UserBackground
from models.session_model import Session

# 导入所有组件
from agents.planner_agent import planner_agent
from agents.itinerary_agent import itinerary_agent
from agents.role_agent import role_agent
from services.knowledge_service import search_knowledge_base
from agents.inquiry_agent import inquiry_agent

router = APIRouter()

GLOBAL_USER = UserProfile(
    user_id="test",
)

# 会话状态 (历史记录)
GLOBAL_SESSION = Session(
    session_id="test_session_001",
    role="李白",
    location="洛阳",
    history=[] 
)

@router.post("/test_itinerary")
async def test_itinerary(data: dict):
    user_input = data.get("text", "")

    # planner agent判断意图
    decision = await planner_agent(GLOBAL_SESSION, user_input)
    print(f"🧠 Planner 决策: {decision}")

    # 定义系统提示词 (用于告诉 Role Agent 发生了什么)
    system_msg = ""

    processed_inquiry = False   # 标记是否触发了追问
    check_inquiry = False       # 标记是否需要检查信息完整性
    if decision["intent"] == "update_plan":
        check_inquiry = True
    elif decision["intent"] == "chat":
        if GLOBAL_USER.background.days is None:
            check_inquiry = True
    
    if check_inquiry:
        inquiry_result = await inquiry_agent(GLOBAL_USER, user_input)
        if inquiry_result["action"] == "ask":
            missing_info_question = inquiry_result["reply"]
            print(f"信息缺失，触发追问: {missing_info_question}")

            if decision["intent"] == "chat":
                system_msg = f"（系统指令：用户正在闲聊，但你可以顺便地问一句：{missing_info_question}）"
            else:
                system_msg = f"（系统指令：关键信息缺失。请务必用{GLOBAL_SESSION.role}的口吻向用户提问：{missing_info_question}）"

            processed_inquiry = True
        elif inquiry_result["action"] == 'ready':
            if decision["intent"] == "update_plan":
                await itinerary_agent(GLOBAL_USER, user_input)
                print("（系统提示：行程已生成，请向用户介绍。）")
    if not processed_inquiry and decision["intent"] == "chat":
        print("💬 纯闲聊模式...")
        system_msg = ""

    # --- 知识库检索 (RAG) ---
    knowledge_context = await search_knowledge_base(user_input, GLOBAL_SESSION.history)

    # --- 获取行程 ---
    current_plan_data = None
    if GLOBAL_USER.itinerary is not None:
        current_plan_data = GLOBAL_USER.itinerary.model_dump()

    # --- Role Agent 生成回复 ---
    reply = await role_agent(
        role="李白", 
        user_input=user_input,
        knowledge=knowledge_context,
        system_msg=system_msg,
        itinerary_data=current_plan_data
    )

    GLOBAL_SESSION.history.append({"sender": "user", "text": user_input})
    GLOBAL_SESSION.history.append({"sender": "ai", "text": reply})

    return {
        "reply": reply,
        "itinerary": GLOBAL_USER.model_dump().get("itinerary"),
        "debug_intent": decision
    }