# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 17:35:09 2025

@author: sineu
"""

# yt_video_scraper.py
# 썸네일 사진 링크도 추가

import re
import requests
from pymongo import MongoClient
import yt_dlp

# MongoDB 설정
MONGO_URI = "mongodb+srv://babteacher33:rlarlatls@babteacher.sriiv.mongodb.net/"
DB_NAME = "babteacherDB"
COLLECTION_NAME = "youtube_recipes"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# 검색할 키워드
search_query = "자취생 레시피"
max_results = 20

# yt-dlp 옵션
ydl_opts = {
    'quiet': True,
    'extract_flat': False,
    'force_generic_extractor': False,
    'noplaylist': True,
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitlesformat': 'vtt',
    'subtitleslangs': ['ko'],
}

search_url = f"ytsearch{max_results}:{search_query}"

def vtt_to_clean_txt(vtt_content):
    lines = vtt_content.splitlines()
    text_segments = []
    
    for line in lines:
        line = line.strip()
        if re.match(r"^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}$", line):
            continue
        clean_line = re.sub(r"[^가-힣\s]", "", line)
        if clean_line.strip():
            text_segments.append(clean_line.strip())

    return "\n".join(text_segments)

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    result = ydl.extract_info(search_url, download=False)
    videos = result.get('entries', [])

    for video in videos:
        video_url = video.get('webpage_url', 'URL 없음')
        video_title = video.get('title', '제목 없음')
        video_views = video.get('view_count', '조회수 없음')
        upload_date = video.get('upload_date', '날짜 없음')
        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}" if upload_date != '날짜 없음' else upload_date
        video_thumbnail = video.get('thumbnail', '썸네일 없음')
        
        
        # 자막 처리 - 오직 한국어만
        subtitles = video.get('subtitles', {})
        auto_captions = video.get('automatic_captions', {})
        caption_url = None

        if 'ko' in subtitles:
            caption_url = subtitles['ko'][0].get('url')
        elif 'ko' in auto_captions:
            caption_url = auto_captions['ko'][0].get('url')
        else:
            print(f"❌ 한국어 자막 없음: {video_title}")
            continue  # 한국어 자막 없으면 스킵

        if caption_url:
            try:
                response = requests.get(caption_url)
                response.raise_for_status()
                clean_text = vtt_to_clean_txt(response.text)
                
                # MongoDB 저장 (중복 방지)
                data = {
                    "title": video_title,
                    "url": video_url,
                    "views": video_views,
                    "upload_date": upload_date,
                    "subtitle_lang": 'ko',
                    "subtitle_text": clean_text,
                    "img": video_thumbnail
                }
                
                collection.update_one(
                    {"$or": [{"title": video_title}, {"url": video_url}]},
                    {"$set": data},
                    upsert=True
                )
                print(f"✅ 저장 완료: {video_title}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ 자막 다운로드 실패: {video_title} - {e}")
