#!/usr/bin/env python3
"""Windsor.ai 에서 인스타그램 최신 게시물을 읽어, 첫 이미지를 우리 저장소에 저장하고
홈페이지 '일도점 미디어' 아래 '인스타그램 최신 게시물' 줄을 갱신합니다.
(인스타그램 이미지 주소는 곧 만료되므로 사본을 직접 보관합니다. 실패하면 기존 내용을 그대로 둡니다.)"""
import datetime, html, io, os, re, sys
from pathlib import Path
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "images" / "instagram"
API = "https://connectors.windsor.ai/instagram_public"
PROFILE = "https://www.instagram.com/lgbestshop_ildo/"
START, END = "<!-- IG-POSTS:START", "<!-- IG-POSTS:END -->"
COUNT, WIDTH = 6, 720
FIELDS = "media_timestamp,media_type,media_product_type,media_permalink,media_caption,media_url,media_thumbnail_url"

def fetch_rows(key):
    since = (datetime.date.today() - datetime.timedelta(days=730)).isoformat()
    try:
        r = requests.get(API, timeout=60, params={"api_key": key, "fields": FIELDS, "date_from": since,
                                                  "date_to": datetime.date.today().isoformat()})
    except requests.RequestException as e:
        raise SystemExit(f"Windsor 연결 실패: {type(e).__name__}")
    if r.status_code != 200:
        raise SystemExit(f"Windsor 응답 오류 HTTP {r.status_code}")
    j = r.json()
    return j.get("data", j) if isinstance(j, dict) else j

def shortcode(link):
    m = re.search(r"/(?:p|reel|tv)/([^/?]+)", link or "")
    return m.group(1) if m else None

def pick(rows):
    seen, out = set(), []
    for r in sorted(rows, key=lambda x: x.get("media_timestamp") or "", reverse=True):
        sc = shortcode(r.get("media_permalink"))
        img = r.get("media_url") if r.get("media_type") in ("IMAGE", "CAROUSEL_ALBUM") else r.get("media_thumbnail_url")
        if not sc or sc in seen or not img:
            continue
        seen.add(sc); out.append({"code": sc, "link": r["media_permalink"], "img": img,
                                  "caption": r.get("media_caption") or "", "ts": r.get("media_timestamp", "")})
    return out

def save_image(url, code):
    try:
        b = requests.get(url, timeout=60).content
        im = Image.open(io.BytesIO(b)).convert("RGB")
    except Exception:
        return False
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)))
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    im.save(IMG_DIR / f"{code}.jpg", "JPEG", quality=82, optimize=True)
    return True

def alt_text(caption):
    first = next((l.strip() for l in caption.splitlines() if l.strip()), "")
    first = re.sub(r"#\S+", "", first).strip()
    return ("일도점 인스타그램 - " + first[:50]) if first else "LG전자 베스트샵 일도점 인스타그램 게시물"

def block(items):
    e = html.escape
    cells = "".join(
        f'      <a class="ig-item" href="{e(i["link"])}" target="_blank" rel="noopener">'
        f'<img src="images/instagram/{i["code"]}.jpg" alt="{e(alt_text(i["caption"]))}" loading="lazy" width="{WIDTH}" height="{WIDTH}"></a>\n'
        for i in items)
    return (f'  <div class="ig-wrap">\n    <div class="ig-head">인스타그램 최신 게시물'
            f'<a href="{PROFILE}" target="_blank" rel="noopener">@lgbestshop_ildo 더 보기 →</a></div>\n'
            f'    <div class="ig-grid">\n{cells}    </div>\n  </div>\n')

def apply(text, items):
    a = text.index(START); a = text.index("\n", a) + 1
    b = text.index(END)
    return text[:a] + block(items) + "  " + text[b:]

def main():
    key = os.environ.get("WINDSOR_API_KEY", "")
    if not key:
        raise SystemExit("WINDSOR_API_KEY 가 설정되지 않았습니다.")
    rows = fetch_rows(key)
    cand = pick(rows)
    print(f"Windsor에서 게시물 {len(rows)}건 수신, 이미지 후보 {len(cand)}건")
    items = []
    for c in cand:
        if len(items) >= COUNT: break
        if save_image(c["img"], c["code"]): items.append(c)
    if not items:
        print("저장된 이미지가 없어 홈페이지를 바꾸지 않습니다."); return 1
    keep = {f'{i["code"]}.jpg' for i in items}
    for f in IMG_DIR.glob("*.jpg"):
        if f.name not in keep: f.unlink()
    idx = ROOT / "index.html"
    old = idx.read_text(encoding="utf-8"); new = apply(old, items)
    if new != old: idx.write_text(new, encoding="utf-8")
    print(f"인스타그램 이미지 {len(items)}개 반영 (최신: {items[0]['ts'][:10]})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
