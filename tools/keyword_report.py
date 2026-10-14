#!/usr/bin/env python3
"""네이버 검색광고 키워드도구에서 월간 검색량을 가져와 data/keywords 에 기록합니다."""
import base64, csv, datetime, hashlib, hmac, os, sys, time
from pathlib import Path
import requests

BASE = "https://api.searchad.naver.com"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "keywords"

def sign(secret, ts, method, path):
    msg = f"{ts}.{method}.{path}".encode()
    return base64.b64encode(hmac.new(secret.encode(), msg, hashlib.sha256).digest()).decode()

def fetch(seeds, cid, lic, secret):
    path = "/keywordstool"
    ts = str(round(time.time() * 1000))
    headers = {"X-Timestamp": ts, "X-API-KEY": lic, "X-Customer": cid,
               "X-Signature": sign(secret, ts, "GET", path)}
    r = requests.get(BASE + path, headers=headers, timeout=30,
                     params={"hintKeywords": ",".join(seeds), "showDetail": "1"})
    r.raise_for_status()
    return r.json().get("keywordList", [])

def num(v):
    # 검색량이 적으면 "< 10" 처럼 문자로 옴 → 5로 간주
    try:
        return int(v)
    except (TypeError, ValueError):
        return 5

def main():
    cid = os.environ["SA_CUSTOMER_ID"]; lic = os.environ["SA_ACCESS_LICENSE"]; secret = os.environ["SA_SECRET_KEY"]
    seeds = [l.strip() for l in (ROOT / "tools" / "keywords.txt").read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.startswith("#")]
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
    rows = {}
    for i in range(0, len(seeds), 5):
        for k in fetch(seeds[i:i + 5], cid, lic, secret):
            kw = k["relKeyword"]
            pc, mo = num(k.get("monthlyPcQryCnt")), num(k.get("monthlyMobileQryCnt"))
            rows[kw] = {"keyword": kw, "pc": pc, "mobile": mo, "total": pc + mo,
                        "competition": k.get("compIdx", ""), "avg_ad_depth": k.get("plAvgDepth", "")}
        time.sleep(0.5)
    ranked = sorted(rows.values(), key=lambda x: x["total"], reverse=True)[:400]
    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["keyword", "pc", "mobile", "total", "competition", "avg_ad_depth"]
    with open(OUT / f"{today}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(ranked)
    # 기준 키워드의 날짜별 기록 (추이 계산용)
    hist = OUT / "history.csv"
    new = not hist.exists()
    with open(hist, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new: w.writerow(["date", "keyword", "total", "pc", "mobile"])
        for s in seeds:
            if s in rows: w.writerow([today, s, rows[s]["total"], rows[s]["pc"], rows[s]["mobile"]])
    print(f"{today}: 기준 {len(seeds)}개, 연관 포함 {len(rows)}개 키워드 기록")

if __name__ == "__main__":
    sys.exit(main())
