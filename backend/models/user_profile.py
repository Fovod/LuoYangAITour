from pydantic import BaseModel
from typing import Dict, List, Optional

class Spot(BaseModel):
    name:str
    start:str
    duration:float
    tags:Optional[List[str]] = []

class DayPlan(BaseModel):
    day:int
    spots:List[Spot]

class Itinerary(BaseModel):
    plan:List[DayPlan]

class UserBackground(BaseModel):
    days: int
    budget: Optional[str] = None
    people: Optional[str] = None
    notes: Optional[str] = None

class UserProfile(BaseModel):
    user_id:str     # 唯一用户标识
    background:UserBackground
    state:Optional[str] = None      # 当前短期状态
    preferences:Dict[str, float] = {}       # 长期偏好权重
    itinerary:Optional[Itinerary] = None
