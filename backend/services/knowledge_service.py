import json
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent / "data"

def load_json(filename:str):
    with open(BASE_PATH / filename, "r", encoding='utf-8') as f:
        return json.load(f)

# 加载数据
SPOTS = load_json("spots.json")
RESTAURANTS = load_json("restaurants.json")
HISTORY = load_json("history.json")

def search_knowledge_base(query: str) -> str:
    """
    【核心功能】根据用户说的话，去所有知识库里检索相关信息。
    """
    results = []
    
    # 1. 搜历史 (匹配景点ID或名字)
    for h in HISTORY:
        # 如果用户提到了某个景点的历史人物或名字
        if h["spot_id"] in query or h["character"] in query: 
             results.append(f"【历史典故】关于{h['character']}：{h['story']}")

    # 2. 搜景点 (匹配名字)
    for s in SPOTS:
        if s["name"] in query:
            results.append(f"【景点数据】{s['name']}：建议游玩{s['duration_hours']}小时，票价{s['ticket_price']}元。Tips:{','.join(s['tips'])}")

    # 3. 搜餐厅 (匹配名字或类型)
    for r in RESTAURANTS:
        if r["name"] in query or (r["features"] and any(f in query for f in r["features"])):
             results.append(f"【推荐餐厅】{r['name']}：人均{r['price_per_person']}元，特色是{','.join(r['features'])}")

    # 如果搜到了东西，就拼接成字符串返回；没搜到就返回空
    if results:
        return "\n".join(results)
    return ""