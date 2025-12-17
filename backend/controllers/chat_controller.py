from fastapi import APIRouter
from services.ai_service import ai_service
from models.session_model import sessions, Session, ChatRequest

router = APIRouter()

@router.post("/chat")
async def chat(req:ChatRequest):
    session = sessions.get(req.session_id)
    if not session:
        session = Session(session_id=req.session_id)
        sessions[req.session_id] = session

    reply = await ai_service(session, req.user_input)
    return {"reply": reply}