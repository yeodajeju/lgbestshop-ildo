#!/usr/bin/env python3
"""index.html(현재 사이트)에 새 디자인을 입혀 preview.html 을 만든다.
사용: python3 tools/build_redesign.py [출력파일=preview.html]
기존 기능(시트 연동·추적 코드·상담 폼·관리자 패널·블로그/인스타 자동 갱신 구간)은 그대로 두고
구조·스타일·달력/첫 화면 렌더링만 바꾼다."""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = sys.argv[1] if len(sys.argv) > 1 else 'preview.html'
PREVIEW = OUT != 'index.html'
s = (ROOT / 'index.html').read_text(encoding='utf-8')
if 'n-hero' in s:
    sys.exit('index.html 에 이미 새 디자인이 적용되어 있습니다.')

def rep(a, b, n=1):
    global s
    assert s.count(a) >= 1, 'not found: ' + a[:60]
    s = s.replace(a, b) if n == 0 else s.replace(a, b, n)

def block(start_pat, end='</section>'):
    i = s.index(start_pat)
    j = s.index(end, i) + len(end)
    return i, j

# ── 섹션 위치
h_i, h_j = block('<section class="hero">')
g_i, g_j = block('<section class="gallery-sec">')
a_i, a_j = block('<section class="about" id="about">')
e_i, e_j = block('<section class="events" id="events"')
m_i, m_j = block('<section class="managers" id="managers">')
r_i, r_j = block('<section class="reviews" id="reviews">')
b_i, b_j = block('<section class="benefits" id="benefits">')
v_i, v_j = block('<section class="resv-sec" id="reservation">')
t_i, t_j = block('<section class="tips" id="tips">')
d_i, d_j = block('<section class="media-sec" id="media"')
c_i, c_j = block('<section class="cta-sec">')

hero, gallery = s[h_i:h_j], s[g_i:g_j]
store_img = re.search(r"class=\"hlbg\" style=\"background-image:url\('([^']+)'\)", hero).group(1)
gal = {m.group(2): m.group(1) for m in re.finditer(r'<img src="([^"]+)" alt="([^"]+)">', gallery)}
GAL_ORDER = [('냉장고존', '냉장고'), ('세탁기존', '세탁기·건조기'), ('에어컨존', '에어컨'), ('공기청정기존', '공기청정기'),
             ('청소기존', '청소기'), ('스타일러존', '스타일러'), ('식기세척기존', '식기세척기'), ('노트북존', 'gram 노트북'),
             ('1층 상담 공간', '상담 공간'), ('컨설팅룸', '컨설팅룸')]
gal_html = ''.join(f'<figure><img src="{gal[k]}" alt="일도점 {l}" loading="lazy"><figcaption>{l}</figcaption></figure>' for k, l in GAL_ORDER if k in gal)

TEL = "gtag('event','phone_click',{event_category:'conversion',event_label:'%s'}); fbq('track','Contact');"

NEW_HERO = f'''<section class="n-hero" id="top">
  <div class="n-head">
    <div class="n-badge" id="hero-badge">SINCE 1994 · 제주 LG전자 베스트샵 일도점</div>
    <h1 class="n-title" id="hero-title">비교하다 지치기 전에, <span class="acc">일도점에서</span> 한 번에 끝내세요</h1>
    <p class="n-desc" id="hero-desc">후기가 증명합니다. 내 친구가 가전 산 바로 그 매장</p>
    <a href="#events" class="n-link" id="hero-cta-secondary">이달의 이벤트 보기</a>
  </div>
  <div id="n-evwrap" style="display:none">
    <div id="n-slides"></div>
    <div class="n-pager" id="n-pager">
      <div class="n-pager-pos" id="n-pager-pos"></div>
      <div class="n-pager-btns">
        <button type="button" onclick="nHeroGo(-1)" aria-label="이전 행사">←</button>
        <button type="button" class="dk" onclick="nHeroGo(1)" aria-label="다음 행사">→</button>
      </div>
    </div>
  </div>
  <div id="n-store">
    <div class="n-slide">
      <div class="n-slide-txt">
        <div class="n-slide-meta"><span class="n-kicker">제주시내 LG가전 전문매장</span></div>
        <h2 class="n-slide-title n-store-title">구매 혜택은 물론,<br>친절한 상담과 설치 후 관리까지<br>책임지고 끝까지 함께합니다</h2>
        <p class="n-store-sub">예약 없이도 편하게 방문·상담하실 수 있어요.</p>
        <div class="n-btns">
          <a href="tel:0647587722" class="n-btn-p" onclick="{TEL % 'hero_btn'}">전화상담 064-758-7722</a>
          <a href="#reservation" class="n-btn-o" onclick="gtag('event','reservation_form_click',{{event_category:'conversion',event_label:'hero_form'}}); fbq('track','Lead');">상담 예약하기</a>
        </div>
      </div>
      <div class="n-store-photo" role="img" aria-label="LG전자 베스트샵 일도점 매장 전경" style="background-image:url('{store_img}')"></div>
    </div>
  </div>
  <div class="n-info">
    <div>제주시 동광로 157</div>
    <div>월~금 10:30–20:30 · 토 10:30–20:00 · 일 11:00–20:00</div>
    <div class="mut">명절 전날·당일 휴무</div>
  </div>
</section>
'''

NEW_EVENTS = '''<section class="n-ev" id="events">
  <div class="n-ev-head">
    <div><div class="n-label">This Month</div><h2 class="n-h2">이달의 행사·이벤트</h2></div>
    <div class="n-ev-hint">오늘 진행 중인 행사가 먼저 보이고, 날짜를 누르면 그날 행사로 바뀌어요</div>
  </div>
  <div class="n-ev-grid">
    <div class="n-ev-info">
      <div class="n-ev-date" id="n-ev-date"></div>
      <div class="n-ev-count" id="n-ev-count"></div>
      <div id="n-ev-list"></div>
      <div class="n-ev-note">행사제품 및 혜택은 모델, 기간, 수량에 따라 상이할 수 있으며 LG전자 공식 행사 기준입니다.</div>
    </div>
    <div class="n-ev-cal">
      <div class="n-cal-top">
        <button type="button" onclick="chM(-1)" aria-label="이전 달">←</button>
        <div id="cal-label"></div>
        <button type="button" onclick="chM(1)" aria-label="다음 달">→</button>
      </div>
      <div class="n-cal-dow"><div>일</div><div>월</div><div>화</div><div>수</div><div>목</div><div>금</div><div>토</div></div>
      <div class="n-cal-cells" id="cal-cells"></div>
      <div class="n-cal-legend">
        <span><b class="lg-tint"></b>기간 행사 진행 중</span>
        <span><b class="lg-dot"></b>하루 행사</span>
        <span><b class="lg-today"></b>오늘</span>
        <span><b class="lg-sel"></b>선택한 날</span>
      </div>
      <div style="margin-top:10px"><div id="sheet-status" class="sheet-status" style="display:inline-block"></div></div>
    </div>
  </div>
</section>
'''

NEW_ABOUT = f'''<section class="n-sec n-about" id="about">
  <div class="n-sec-head">
    <div class="n-label">About</div>
    <h2 class="n-h2">Since 1994.<br>제주시내 LG가전<br>전문매장</h2>
  </div>
  <div class="n-sec-body">
    <p class="n-lead about-intro">LG전자 베스트샵 일도점은 구매 혜택은 물론, 친절한 상담과 설치 후 관리까지 한결같이 책임지는 제주시 LG전자 가전 전문 매장입니다.</p>
    <div class="n-slogan">가전은 역시, <span>LG</span><br>LG가전은 역시, <span>베스트샵 일도점</span></div>
    <div>
      <div class="n-gal-cap">냉장고부터 노트북까지, LG 가전 전 제품군을 한 곳에서</div>
      <div class="n-gal">{gal_html}</div>
    </div>
    <div class="n-prom">
      <div class="n-prom-t">뭘 모르는지도 모르는 채로 <span>오셔도 됩니다.</span></div>
      <div class="afeats">
        <div class="af"><div class="af-i"></div><div class="af-t">나에게 딱 맞는 제품</div><div class="af-d">예산과 생활에 맞는 제품만 골라드립니다</div></div>
        <div class="af"><div class="af-i"></div><div class="af-t">계속 바뀌는 견적</div><div class="af-d">더 좋은 조건이 생기면 계약 후에도 먼저 업데이트합니다</div></div>
        <div class="af"><div class="af-i"></div><div class="af-t">구매 후 혜택 케어</div><div class="af-d">놓치기 쉬운 혜택까지 먼저 챙겨드립니다</div></div>
        <div class="af"><div class="af-i"></div><div class="af-t">비교해도 결국 일도점</div><div class="af-d">다시 찾아오시는 데는 이유가 있습니다</div></div>
      </div>
    </div>
  </div>
</section>
'''

cta = s[c_i:c_j]
cta = cta.replace('📞 064-758-7722 전화하기', '064-758-7722 전화하기').replace('📅 공식홈페이지 예약', '공식홈페이지 예약').replace('🗺️ 네이버플레이스 예약', '네이버플레이스 예약')
cta = cta.replace('</section>', '''  <div class="n-visit" id="visit">
    <div class="n-visit-t">오시는 길</div>
    <div>제주시 동광로 157 · 064-758-7722</div>
    <div>월~금 10:30–20:30 · 토 10:30–20:00 · 일 11:00–20:00 · 명절 전날·당일 휴무</div>
    <div class="n-visit-maps">
      <a href="https://m.place.naver.com/place/1607379211/home" target="_blank" rel="noopener">네이버지도</a>
      <a href="https://map.kakao.com/link/search/LG전자베스트샵일도점" target="_blank" rel="noopener">카카오맵</a>
    </div>
  </div>
</section>''')

managers = s[m_i:m_j].replace('📅 지금 예약하기', '상담 예약하기')
benefits = s[b_i:b_j].replace('🎁 일도점 단독 혜택 받기', '일도점 단독 혜택 받기')
media = s[d_i:d_j]

s = (s[:h_i] + NEW_HERO + s[h_j:g_i] + NEW_EVENTS + s[r_i:r_j] + '\n' + managers + '\n' + NEW_ABOUT + benefits + '\n'
     + s[t_i:t_j] + '\n' + media + s[d_j:c_i] + s[v_i:v_j] + '\n' + cta + s[c_j:])

# ── 내비게이션
i = s.index('<ul class="nav-links">'); j = s.index('</ul>', i) + 5
s = s[:i] + f'''<ul class="nav-links">
    <li><a href="#events">이달의 행사</a></li>
    <li><a href="javascript:openNews()">소식</a></li>
    <li><a href="#reviews">고객 후기</a></li>
    <li><a href="#managers">매니저</a></li>
    <li><a href="#about">매장 소개</a></li>
    <li><a href="#visit">오시는 길</a></li>
    <li><a href="tel:0647587722" class="nav-cta nav-cta-o" onclick="{TEL % 'nav_bar'}">전화상담</a></li>
    <li><a href="#reservation" class="nav-cta" onclick="gtag('event','reservation_form_click',{{event_category:'conversion',event_label:'nav_form'}}); fbq('track','Lead');">상담 예약</a></li>
  </ul>''' + s[j:]
i = s.index('<div class="mob-menu" id="mob-menu">'); j = s.index('</div>', i) + 6
s = s[:i] + f'''<div class="mob-menu" id="mob-menu">
  <a href="#events" onclick="closeMob()">이달의 행사</a>
  <a href="javascript:void(0)" onclick="closeMob();setTimeout(openNews,300)">소식</a>
  <a href="#reviews" onclick="closeMob()">고객 후기</a>
  <a href="#managers" onclick="closeMob()">매니저</a>
  <a href="#about" onclick="closeMob()">매장 소개</a>
  <a href="#benefits" onclick="closeMob()">구매 혜택</a>
  <a href="#tips" onclick="closeMob()">일도점 이야기</a>
  <a href="#media" onclick="closeMob()">미디어</a>
  <a href="#visit" onclick="closeMob()">오시는 길</a>
  <a href="tel:0647587722" class="mob-cta" onclick="{TEL % 'mob_menu'}">064-758-7722 전화상담</a>
  <a href="#reservation" class="mob-cta" onclick="closeMob(); gtag('event','reservation_form_click',{{event_category:'conversion',event_label:'mob_form'}}); fbq('track','Lead');">상담 신청하기</a>
</div>''' + s[j:]

# ── 자잘한 문구(이모지 제거)
for a, b in [('<h2>📰 일도점 소식</h2>', '<h2>일도점 소식</h2>'), ('🔄 새로고침</button>\n        <button class="news-close"', '새로고침</button>\n        <button class="news-close"'),
             ('🎁 혜택 받으러 가기', '혜택 받으러 가기'), ('<br>📞 064-758-7722<br>', '<br>064-758-7722<br>')]:
    if a in s: s = s.replace(a, b)

# ── 가전 꿀팁 → 일도점 이야기
rep('<div class="slabel fi">Know-how</div>', '<div class="slabel fi">Story</div>')
rep('<h2 class="stitle fi">가전 <span>꿀팁</span></h2>', '<h2 class="stitle fi">일도점 <span>이야기</span></h2>')
rep('<li><a href="#tips">가전 꿀팁</a></li>', '<li><a href="#tips">일도점 이야기</a></li>')
# ── 팝업: 이전 버튼
rep('<button class="popup-close-btn" id="popup-close-btn"', '<button class="popup-close-btn popup-prev-btn" id="popup-prev-btn" onclick="closePopupPrev()" style="display:none">◂ 이전</button>\n      <button class="popup-close-btn" id="popup-close-btn"')

# ── 이벤트 시트: H열(첫 화면 한 줄) 읽기 + 렌더 연결
rep("strip:(cols[6]||'').trim(),", "strip:(cols[6]||'').trim(), hl:(cols[7]||'').trim(),")
rep("    renderCal();\n    setStatus(st,'ok'", "    if(window.nAddExtra) nAddExtra();\n    renderCal();\n    setStatus(st,'ok'")

# ── 폰트·스타일·스크립트
s = re.sub(r'<link href="https://fonts.googleapis.com/css2\?family=Noto\+Serif\+KR[^>]*>',
           '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">', s, count=1)
s = s.replace('<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>', 1)
css = (ROOT / 'tools' / 'redesign.css').read_text(encoding='utf-8')
js = (ROOT / 'tools' / 'redesign.js').read_text(encoding='utf-8')
if PREVIEW:
    js += '\n' + (ROOT / 'tools' / 'redesign_preview_extra.js').read_text(encoding='utf-8')
    s = s.replace('<meta name="description"', '<meta name="robots" content="noindex,nofollow">\n<meta name="description"', 1)
i = s.index('</style>')
s = s[:i] + '\n/* ===== REDESIGN ===== */\n' + css + '\n' + s[i:]
bar = f'''<div class="n-bar"><a href="tel:0647587722" onclick="{TEL % 'bottom_bar'}">전화상담</a><a class="p" href="#reservation" onclick="gtag('event','reservation_form_click',{{event_category:'conversion',event_label:'bottom_bar'}}); fbq('track','Lead');">상담 예약</a></div>
<script>
{js}
</script>
'''
i = s.rindex('</body>')
s = s[:i] + bar + s[i:]
(ROOT / OUT).write_text(s, encoding='utf-8')
print('wrote', OUT, len(s))
