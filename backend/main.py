from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from controllers.chat_controller import router
from controllers.test_controller import router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)