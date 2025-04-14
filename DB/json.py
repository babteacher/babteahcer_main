# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 21:42:51 2025

@author: sineu
"""

import json
from pymongo import MongoClient

# 1. MongoDB 연결
client = MongoClient("mongodb+srv://babteacher33:rlarlatls@babteacher.sriiv.mongodb.net/")  # 필요시 주소 수정
db = client["babteacherDB"]                        # DB 이름 입력
collection = db["youtube_recipes"]                 # 컬렉션 이름

# 2. 데이터 수집 및 정리
recipes = []
for doc in collection.find():
    recipe = {
        "title": doc.get("title", "제목 없음"),
        "ingredients": doc.get("ingredients", "재료 없음"),
        "steps": doc.get("text", "설명 없음").split('\n'),  # 요약 텍스트를 줄마다 나눔
        "video": doc.get("url", "#"),
        "thumbnail": doc.get("img", ""),
        "category": doc.get("category", ""),
        "views": doc.get("views", ""),
        "upload_date": doc.get("upload_date", "")
    }
    recipes.append(recipe)

# 3. JSON 파일로 저장
with open("recipes.json", "w", encoding="utf-8") as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2)

print("✅ recipes.json 생성 완료!")
