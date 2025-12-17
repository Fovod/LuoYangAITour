# 会话状态Pydantic模型
# 作用：存储用户会话状态，包括角色、时间、地点、聊天历史、提供Agent调用上下文

from pydantic import BaseModel
from typing import List, Dict

class Session(BaseModel):
    session_id:str
    role:str = '李白'
    time:str = "上午9点"
    location: str = '洛阳古城'
    history:List[Dict] = []

# 内存存储所有会话
sessions = {}

class ChatRequest(BaseModel):
    session_id:str
    user_input:str

