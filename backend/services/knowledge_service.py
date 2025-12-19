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

async def search_knowledge_base(user_input: str) -> str:
    search_intent = await search_agent(user_input)
    
    types = search_intent.get("types", [])
    keywords = search_intent.get("keywords", [])
    
    results = []

    # --- 辅助函数：关键词匹配 ---
    def match_score(item, text_fields):
        """如果关键词列表为空，返回 True (代表泛搜)；否则检查是否包含任一关键词"""
        if not keywords: 
            return True 
        # 只要 item 的任意字段包含任意一个 keyword，就命中
        for kw in keywords:
            for field in text_fields:
                if isinstance(field, list):
                    if any(kw in str(tag) for tag in field): return True
                elif kw in str(field):
                    return True
        return False

    # 2. 根据意图搜索知识库
    
    # === 搜景点 ===
    if "spot" in types:
        found_spots = [s for s in SPOTS if match_score(s, [s["name"], s["tags"]])]
        # 如果是泛搜（没关键词），随机推2个；如果是精搜，全展示
        display_spots = found_spots if keywords else random.sample(found_spots, min(2, len(found_spots)))
        
        for s in display_spots:
            results.append(f"【景点推荐】{s['name']} (建议{s['duration_hours']}h)：{';'.join(s['tips'])}")

    # === 搜美食 ===
    if "food" in types:
        found_food = [r for r in RESTAURANTS if match_score(r, [r["name"], r["features"], r["area"]])]
        display_food = found_food if keywords else random.sample(found_food, min(3, len(found_food)))
        
        for r in display_food:
            results.append(f"【美食推荐】{r['name']}：特色{','.join(r['features'])}，人均{r['price_per_person']}元。")

    # === 搜历史 ===
    # 历史不仅看 types，如果用户提到了特定关键词（如“武则天”），即使 types 没识别出 history 也可以尝试搜一下
    if "history" in types or keywords:
        found_history = [h for h in HISTORY if match_score(h, [h["character"], h["story"], h["spot_id"]])]
        if found_history:
            # 历史故事这就取相关性最高的一个即可，避免刷屏
            h = found_history[0] 
            results.append(f"【历史典故】{h['character']}：{h['story']}")

    # 3. 如果 AI 什么都没分类出来 (兜底)，但用户确实说了具体名词，尝试全库暴力匹配
    if not results and keywords:
        for kw in keywords:
            for s in SPOTS:
                if kw in s["name"]: results.append(f"【相关景点】{s['name']}")
            for r in RESTAURANTS:
                if kw in r["name"]: results.append(f"【相关餐厅】{r['name']}")

    return "\n\n".join(results)