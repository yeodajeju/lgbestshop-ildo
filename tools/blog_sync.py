#!/usr/bin/env python3
"""네이버 블로그 RSS의 최신 글을 홈페이지 '가전 꿀팁' 칸(index.html)에 글자로 반영합니다.
제목·날짜·요약 몇 줄·원문 링크만 넣고, 글 전체는 복사하지 않습니다."""
import datetime, html, re, sys, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
RSS = "https://rss.blog.naver.com/lg_bestshop_ildo.xml"
START, END = "<!-- BLOG-POSTS:START", "<!-- BLOG-POSTS:END -->"
MAX_POSTS, MIN_POSTS = 8, 4

# (키워드, 이모지, 태그) — 위에서부터 먼저 맞는 것을 사용
RULES = [
    ("김치냉장고", "🧊", "냉장고"), ("냉장고", "🧊", "냉장고"), ("세탁", "🧺", "세탁·건조"), ("건조기", "🧺", "세탁·건조"),
    ("스타일러", "👔", "스타일러"), ("에어컨", "❄️", "에어컨"), ("제습", "💧", "공기청정기·제습"), ("공기청정", "💧", "공기청정기·제습"),
    ("TV", "📺", "TV·영상"), ("OLED", "📺", "TV·영상"), ("올레드", "📺", "TV·영상"), ("사운드바", "📺", "TV·영상"),
    ("청소기", "🧹", "청소기"), ("로봇", "🤖", "로봇청소기"), ("식기세척", "🍽️", "주방가전"), ("인덕션", "🍳", "주방가전"),
    ("구독", "🔁", "구독"), ("혼수", "💍", "혼수·신혼"), ("신혼", "💍", "혼수·신혼"), ("이벤트", "🎁", "이벤트"), ("혜택", "🎁", "혜택"),
]

def classify(text):
    for kw, emo, tag in RULES:
        if kw.lower() in text.lower():
            return emo, tag
    return "💡", "가전"

def clean(raw, n=70):
    t = re.sub(r"<[^>]+>", " ", html.unescape(raw or ""))
    t = re.sub(r"\s+", " ", html.unescape(t)).strip()
    return (t[:n].rstrip() + "…") if len(t) > n else t

def parse(xml_text):
    root = ET.fromstring(xml_text)
    out = []
    for it in root.iter("item"):
        title = clean(it.findtext("title"), 80)
        link = (it.findtext("link") or "").split("?")[0].strip()
        if not title or not link.startswith("https://blog.naver.com/"):
            continue
        try:
            d = parsedate_to_datetime(it.findtext("pubDate")).astimezone(datetime.timezone(datetime.timedelta(hours=9)))
            date = f"{d.year}.{d.month}.{d.day}"
        except Exception:
            date = ""
        emo, tag = classify(title + " " + (it.findtext("category") or ""))
        out.append({"title": title, "link": link, "date": date, "body": clean(it.findtext("description")), "emoji": emo, "tag": tag})
    return out[:MAX_POSTS]

def card(p):
    e = html.escape
    return f'''    <a class="tcard fi" href="{e(p["link"])}" target="_blank" rel="noopener" style="text-decoration:none;color:inherit">
      <div class="temoji">{p["emoji"]}</div>
      <div class="ttitle">{e(p["title"])}</div>
      <div class="tbody">{e(p["body"])}</div>
      <div style="margin-top:10px;display:flex;justify-content:space-between;align-items:center">
        <span class="ttag">{e(p["tag"])}</span>
        <span style="font-size:11px;color:#999">{e(p["date"])}</span>
      </div>
      <div style="margin-top:10px;font-size:12px;font-weight:600;color:var(--red)">블로그에서 보기 →</div>
    </a>
'''

def apply(index_text, posts):
    a = index_text.index(START); a = index_text.index("\n", a) + 1
    b = index_text.index(END)
    return index_text[:a] + "".join(card(p) for p in posts) + "    " + index_text[b:]

def main():
    r = requests.get(RSS, timeout=30, headers={"User-Agent": "Mozilla/5.0 (compatible; ildo-blog-sync)"})
    r.raise_for_status()
    posts = parse(r.content)
    if len(posts) < MIN_POSTS:
        print(f"글 {len(posts)}개만 읽혀서 홈페이지를 바꾸지 않습니다."); return 1
    idx = ROOT / "index.html"
    old = idx.read_text(encoding="utf-8"); new = apply(old, posts)
    if new == old:
        print("변경 없음"); return 0
    idx.write_text(new, encoding="utf-8")
    sm = ROOT / "sitemap.xml"
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
    sm.write_text(re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{today}</lastmod>", sm.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"블로그 최신 글 {len(posts)}개 반영")
    return 0

if __name__ == "__main__":
    sys.exit(main())
