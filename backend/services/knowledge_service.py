import json
import random
from pathlib import Path
from agents.search_agent import search_agent

BASE_PATH = Path(__file__).parent.parent / "data"

def load_json(filename:str):
    with open(BASE_PATH / filename, "r", encoding='utf-8') as f:
        return json.load(f)

# 加载数据
SPOTS = load_json("spots.json")
RESTAURANTS = load_json("restaurants.json")
HISTORY = load_json("history.json")

async def search_knowledge_base(user_input: str, history: list = []) -> str:
    recent_history = history[-6:] if history else []
    history_str = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in recent_history])
    
    search_intent = await search_agent(user_input, history_str)
    
    types = search_intent.get("types", [])
    keywords = search_intent.get("keywords", [])
    
    results = []

    def match_score(item, text_fields):
        if not keywords: 
            return True 
        for kw in keywords:
            for field in text_fields:
                if isinstance(field, list):
                    if any(kw in str(tag) for tag in field): return True
                elif kw in str(field):
                    return True
        return False

    if "spot" in types:
        found_spots = [s for s in SPOTS if match_score(s, [s["name"], s["tags"]])]
        display_spots = found_spots if keywords else random.sample(found_spots, min(2, len(found_spots)))
        for s in display_spots:
            results.append(f"【景点推荐】{s['name']} (建议{s['duration_hours']}h)：{';'.join(s['tips'])}")

    if "food" in types:
        found_food = [r for r in RESTAURANTS if match_score(r, [r["name"], r["features"], r["area"]])]
        display_food = found_food if keywords else random.sample(found_food, min(3, len(found_food)))
        for r in display_food:
            results.append(f"【美食推荐】{r['name']}：特色{','.join(r['features'])}，人均{r['price_per_person']}元。")

    if "history" in types or keywords:
        found_history = [h for h in HISTORY if match_score(h, [h["character"], h["story"], h["spot_id"]])]
        if found_history:
            h = found_history[0] 
            results.append(f"【历史典故】{h['character']}：{h['story']}")

    if not results and keywords:
        for kw in keywords:
            for s in SPOTS:
                if kw in s["name"]: results.append(f"【相关景点】{s['name']}")
            for r in RESTAURANTS:
                if kw in r["name"]: results.append(f"【相关餐厅】{r['name']}")

    return "\n\n".join(results)