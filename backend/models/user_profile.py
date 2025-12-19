from pydantic import BaseModel, Field
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
    days:Optional[int] = Field(None, description='游玩天数')
    people_count:Optional[int] = Field(None, description="人数")
    people_type:Optional[str] = Field(None, description="人群类型：独行/朋友/情侣/带小孩/带老人/家庭")
    budget:Optional[str] = Field(None, description="预算:/穷游/适中/豪华")
    pace:Optional[str] = Field(None, description="节奏：特种兵/悠闲/深度")
    # 记录已问过问题
    asked_fields:List[str] = Field(default_factory=list)
    # 必填项
    def is_complete(self)->bool:
        return self.days is not None and self.people_type is not None

class UserProfile(BaseModel):
    user_id:str
    background:UserBackground = Field(
        default_factory=UserBackground # type: ignore[arg-type]
    )
    state:Optional[str] = None      # 当前短期状态
    preferences:Dict[str, float] = Field(default_factory=dict)       # 长期偏好权重
    itinerary:Optional[Itinerary] = None
