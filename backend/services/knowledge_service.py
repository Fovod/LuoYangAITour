import json
from pathlib import Path
from random import choice

BASE_PATH = Path(__file__).parent.parent / "data"

def load_json(filename:str):
    with open(BASE_PATH / filename, "r", encoding='utf-8') as f:
        return json.load(f)

# 启动时加载
SPOTS = load_json("spots.json")
RESTAURANTS = load_json("restaurants.json")
HISTORY = load_json("history.json")

# 工具函数
def recommend_restaurant():
    """
    返回一个随机可用餐厅
    action: recommend_restaurant
    """
    available = [r for r in RESTAURANTS if not r.get("avoid")]
    return choice(available) if available else None

def recommend_spot(keyword: str = ""):
    """
    根据名称或关键字返回景点
    action: recommend_spot
    """
    if keyword:
        for spot in SPOTS:
            if keyword in spot["name"] or spot["name"] in keyword:
                return spot
    # 如果没有指定关键字，则随机返回一个景点
    return choice(SPOTS) if SPOTS else None

def tell_history(spot_name: str):
    """
    返回某个景点的历史事件列表
    action: tell_history
    """
    for spot in SPOTS:
        if spot_name in spot["name"] or spot["name"] in spot_name:
            return [h for h in HISTORY if h["spot_id"] == spot["id"]]
    return []
