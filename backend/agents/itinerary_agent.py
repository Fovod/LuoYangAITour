# itinerary_agent.py
from datetime import datetime, timedelta
from typing import List
from models.user_profile import UserProfile, Itinerary, DayPlan, Spot
from services.knowledge_service import SPOTS  # 假设你的景点数据在这里

def add_time(start_str: str, duration_hours: float) -> str:
    """给时间字符串累加小时，返回新时间字符串"""
    start_time = datetime.strptime(start_str, "%H:%M")
    end_time = start_time + timedelta(hours=duration_hours)
    return end_time.strftime("%H:%M")

async def itinerary_agent(user_profile: UserProfile) -> Itinerary:
    days = user_profile.background.days
    preferences = user_profile.preferences

    # 给景点打分
    scored_spots = []
    for s in SPOTS:
        score = sum(preferences.get(tag, 0.0) for tag in s.get("tags", []))
        scored_spots.append((score, s))
    scored_spots.sort(key=lambda x: x[0], reverse=True)

    plan: List[DayPlan] = []
    day_index = 0
    current_time = "09:00"
    current_day_spots: List[Spot] = []

    for _, s in scored_spots:
        duration = s.get("duration_hours", 1.0)

        # 如果超过当日21:00，则换下一天
        end_time_dt = datetime.strptime(current_time, "%H:%M") + timedelta(hours=duration)
        if end_time_dt.hour >= 21:
            # 保存当前天
            plan.append(DayPlan(day=day_index + 1, spots=current_day_spots))
            day_index += 1
            if day_index >= days:
                break  # 超出用户总天数
            current_day_spots = []
            current_time = "09:00"

        # 添加景点
        spot = Spot(
            name=s["name"],
            start=current_time,
            duration=duration,
            tags=s.get("tags", [])
        )
        current_day_spots.append(spot)
        # 更新当前时间
        current_time = add_time(current_time, duration)

    # 保存最后一天
    if current_day_spots and day_index < days:
        plan.append(DayPlan(day=day_index + 1, spots=current_day_spots))

    itinerary = Itinerary(plan=plan)
    user_profile.itinerary = itinerary
    return itinerary
