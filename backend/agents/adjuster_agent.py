from models.user_profile import UserProfile, Spot
from datetime import datetime, timedelta

def add_time_str(start: str, hours: float) -> str:
    t = datetime.strptime(start, "%H:%M") + timedelta(hours=hours)
    return t.strftime("%H:%M")

async def adjuster_agent(user_profile: UserProfile):
    if not user_profile.itinerary:
        return None

    for day in user_profile.itinerary.plan:
        # 累计时间
        for i, spot in enumerate(day.spots):
            if user_profile.state == "需要休息" and i == len(day.spots) - 1:
                # 在最后一个景点后增加休息
                end_time = add_time_str(spot.start, spot.duration)
                rest_spot = Spot(
                    name="咖啡馆休息",
                    start=end_time,
                    duration=1.0,
                    tags=["rest"]
                )
                day.spots.append(rest_spot)
    return user_profile.itinerary
