import json
from openai import OpenAI
import sys, os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_URL
client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_URL)

BASE_PATH = Path(__file__).parent.parent / "data"
def load_json(filename:str):
    with open(BASE_PATH / filename, "r", encoding='utf-8') as f:
        return json.load(f)
SPOTS = load_json("spots.json")
RESTAURANTS = load_json("restaurants.json")
HISTORY = load_json("history.json")

async def search_agent(user_input:str):
    '''分析用户意图，决定检索哪个知识库，以及提取什么关键词'''

    prompt = f"""
你是一个搜索引擎的意图分析器。请分析用户输入，提取检索条件。

【用户输入】
"{user_input}"

【知识库分类】
- spot: 景点、游玩、门票、看风景、去哪里玩。
- food: 餐厅、美食、特产、吃饭、饿了、喝汤。
- history: 历史典故、人物故事、传说、由来、文化背景。

【输出要求】
返回纯 JSON，格式如下：
{{
    "types": ["food", "spot"],  // 涉及的分类，可多选。没涉及则为空列表。
    "keywords": ["牛肉汤", "老城"] // 提取的实体关键词（地名/菜名/人名）。如果是泛指（如“推荐好吃的”），关键词留空。
}}
"""
    try:
        completion = client.chat.completions.create(
            model=DASHSCOPE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1 # 越低越准
        )
        content = completion.choices[0].message.content
        # 清洗可能存在的 markdown 符号
        if content is None:
            raise ValueError("content内容为None")
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Search Agent Error: {e}")
        return {"types": [], "keywords": []}