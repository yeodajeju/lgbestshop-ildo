"""네이버 검색어 트렌드(NAVER API HUB)로 연령대별 검색 추이를 기록한다.

- 키워드 목록: tools/age_keywords.txt (한 줄에 한 묶음, 쉼표로 같은 뜻 표기를 묶을 수 있고, --- 줄로 조회 묶음을 나눔)
- 결과: data/age/age_trend.csv (최근 90일 일별 상댓값), data/age/age_summary.csv (오늘 요약),
        data/age/age_summary_history.csv (요약 누적)
- 키는 환경변수 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 로만 받는다(코드·로그에 남기지 않음).

주의: ratio는 '한 번 조회한 결과 안에서 가장 큰 값을 100으로 잡은 상댓값'이다.
조회(묶음)마다 기준이 달라서 키워드끼리 크기를 직접 비교하면 안 되고,
같은 키워드의 '변화율'만 믿고 쓴다.
"""
import csv
import datetime as dt
import os
import sys
import time

import requests

URL = "https://naverapihub.apigw.ntruss.com/search-trend/v1/search"
KST = dt.timezone(dt.timedelta(hours=9))

# 연령 코드(공식): 3=19~24, 4=25~29, 5=30~34, 6=35~39, 7=40~44, 8=45~49,
#                 9=50~54, 10=55~59, 11=60세 이상
AGE_BANDS = [
    ("20대", ["3", "4"]),      # 19~29세
    ("30대", ["5", "6"]),      # 30~39세
    ("40대", ["7", "8"]),      # 40~49세
    ("50대", ["9", "10"]),     # 50~59세
    ("60대이상", ["11"]),      # 60세 이상
]
DAYS = 90          # 조회 기간(일)
BATCH = 5          # 한 번에 보낼 수 있는 주제어 수(최대 5)
RECENT = 7         # '최근' 평균 일수
BASE = 28          # 비교 기준 평균 일수
MIN_LEVEL = 3.0    # 최근·직전 평균 중 하나라도 이보다 작으면 '데이터 적음'(0~100 상댓값 기준)

OUT_DIR = "data/age"


def load_batches(path="tools/age_keywords.txt"):
    """키워드 파일을 조회 묶음(batch) 목록으로 읽는다.

    한 번 조회 안에서는 가장 큰 값이 100이 되므로, 검색량이 크게 다른 키워드를
    같이 넣으면 작은 쪽이 거의 0으로 눌려 버린다. 그래서 '---' 줄로 묶음을
    나눌 수 있게 했다. 구분선이 없어도 한 묶음은 최대 BATCH(5)개까지만 담는다.
    """
    batches, cur = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "---":
                if cur:
                    batches.append(cur)
                    cur = []
                continue
            if not line or line.startswith("#"):
                continue
            words = [w.strip() for w in line.split(",") if w.strip()]
            cur.append({"groupName": words[0], "keywords": words})
            if len(cur) == BATCH:
                batches.append(cur)
                cur = []
    if cur:
        batches.append(cur)
    return batches


def post_with_retry(headers, body, tries=4):
    wait = 2
    for i in range(tries):
        try:
            r = requests.post(URL, headers=headers, json=body, timeout=30)
        except requests.RequestException as e:
            print("네트워크 오류:", type(e).__name__, file=sys.stderr)
            r = None
        if r is not None and r.status_code == 200:
            return r.json()
        code = r.status_code if r is not None else "-"
        # 인증·권한 문제는 재시도해도 소용없으니 바로 알린다
        if code in (400, 401, 403):
            print(f"요청 거부({code}):", (r.text or "")[:200], file=sys.stderr)
            return None
        print(f"응답 {code}, {wait}초 후 재시도 ({i + 1}/{tries})", file=sys.stderr)
        time.sleep(wait)
        wait *= 2
    return None


def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += dt.timedelta(days=1)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main():
    cid = os.environ.get("NAVER_CLIENT_ID")
    sec = os.environ.get("NAVER_CLIENT_SECRET")
    if not cid or not sec:
        print("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 이 설정되지 않았습니다.", file=sys.stderr)
        return 1
    headers = {
        "X-NCP-APIGW-API-KEY-ID": cid,
        "X-NCP-APIGW-API-KEY": sec,
        "Content-Type": "application/json",
    }

    today = dt.datetime.now(KST).date()
    end = today - dt.timedelta(days=1)          # 오늘 값은 아직 덜 쌓여서 어제까지
    start = end - dt.timedelta(days=DAYS - 1)
    days = list(daterange(start, end))
    batches = load_batches()

    series = {}   # (age, keyword) -> {date: ratio}
    failed = 0
    for age_name, codes in AGE_BANDS:
        for batch in batches:
            body = {
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "timeUnit": "date",
                "keywordGroups": batch,
                "ages": codes,
            }
            res = post_with_retry(headers, body)
            if not res:
                failed += 1
                continue
            for item in res.get("results", []):
                vals = {d["period"]: float(d["ratio"]) for d in item.get("data", [])}
                series[(age_name, item["title"])] = vals
            time.sleep(0.3)

    if not series:
        print("조회 결과가 하나도 없습니다.", file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) 일별 상댓값 (최근 90일, 매번 덮어씀) — 검색이 0인 날은 0으로 채움
    with open(f"{OUT_DIR}/age_trend.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["age", "keyword", "date", "ratio"])
        for (age, kw), vals in sorted(series.items()):
            for d in days:
                w.writerow([age, kw, d.isoformat(), round(vals.get(d.isoformat(), 0.0), 3)])

    # 2) 요약: 최근 7일 평균 vs 그 전 28일 평균
    rows = []
    for (age, kw), vals in sorted(series.items()):
        seq = [vals.get(d.isoformat(), 0.0) for d in days]
        recent = seq[-RECENT:]
        base = seq[-(RECENT + BASE):-RECENT]
        r_avg, b_avg = mean(recent), mean(base)
        if min(r_avg, b_avg) >= MIN_LEVEL:
            change = round((r_avg / b_avg - 1) * 100, 1)
            note = ""
        else:
            change = ""
            note = "데이터 적음"
        rows.append([end.isoformat(), age, kw, round(r_avg, 2), round(b_avg, 2), change, note])

    header = ["기준일", "연령대", "키워드", "최근7일평균", "직전28일평균", "변화율(%)", "비고"]
    with open(f"{OUT_DIR}/age_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    # 3) 요약 누적: 같은 기준일 행은 다시 쓰고, 나머지는 보존
    hist_path = f"{OUT_DIR}/age_summary_history.csv"
    kept = []
    if os.path.exists(hist_path):
        with open(hist_path, newline="", encoding="utf-8-sig") as f:
            r = csv.reader(f)
            next(r, None)
            kept = [row for row in r if row and row[0] != end.isoformat()]
    with open(hist_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(kept)
        w.writerows(rows)

    print(f"완료: 시리즈 {len(series)}개, 실패한 조회 {failed}회, 기준일 {end}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
