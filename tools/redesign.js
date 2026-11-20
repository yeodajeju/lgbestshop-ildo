// ===== 새 디자인: 첫 화면 행사 + 달력 =====
var nOpenEv = {}, nHeroIdx = 0, nHeroList = [];
function nEsc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function nKey(y,m,d){return y+'-'+String(m+1).padStart(2,'0')+'-'+String(d).padStart(2,'0');}
function nPeriod(ev,k){
  var s=(ev.rangeStart||k).split('-'), e=(ev.rangeEnd||ev.rangeStart||k).split('-');
  var a=parseInt(s[1])+'.'+String(parseInt(s[2])).padStart(2,'0'), b=parseInt(e[1])+'.'+String(parseInt(e[2])).padStart(2,'0');
  return a===b ? a+' 하루' : a+' – '+b;
}
function nUniq(list){
  var seen={}, out=[];
  list.forEach(function(x){var id=(x.ev.rangeStart||x.k)+'|'+x.ev.title; if(!seen[id]){seen[id]=1; x.id=id; out.push(x);}});
  out.sort(function(a,b){return (b.ev.rangeStart||b.k).localeCompare(a.ev.rangeStart||a.k);});
  return out;
}
function selectCalDay(d){ selectedDay=d; renderCal(); }
function nToggleEv(i){
  var it=window._nEvItems&&window._nEvItems[i]; if(!it) return;
  // 같은 행사의 소식 글이 있으면 자세한 내용은 소식 창에서 보여준다
  if(nFindNews(it.ev)>=0){ nOpenEvNews(it.ev,null,'event_news_click'); return; }
  nOpenEv[it.id]=!nOpenEv[it.id];
  var el=document.getElementById('n-ei-'+i); if(!el) return;
  el.classList.toggle('open',!!nOpenEv[it.id]);
  el.querySelector('.n-ei-arr').textContent=nOpenEv[it.id]?'−':'+';
  el.querySelector('.n-ei-row').setAttribute('aria-expanded',nOpenEv[it.id]?'true':'false');
  if(nOpenEv[it.id]&&window.gtag) gtag('event','event_detail_open',{event_category:'engagement',event_label:it.ev.title});
}
function renderCal(){
  var lbl=document.getElementById('cal-label'), cells=document.getElementById('cal-cells');
  if(!lbl||!cells) return;
  lbl.textContent=curY+'년 '+(curM+1)+'월';
  var fd=new Date(curY,curM,1).getDay(), dim=new Date(curY,curM+1,0).getDate(), td=new Date(); td.setHours(0,0,0,0);
  var isCur=td.getFullYear()===curY&&td.getMonth()===curM, mk=curY+'-'+curM;
  if(window._nMonth!==mk){ window._nMonth=mk; selectedDay=isCur?td.getDate():null; }
  var html='', monthItems=[];
  for(var i=0;i<fd;i++) html+='<div class="ncc empty"></div>';
  for(var d=1;d<=dim;d++){
    var k=nKey(curY,curM,d), arr=calEvs[k]||[];
    arr.forEach(function(ev){monthItems.push({k:k,ev:ev});});
    var hasP=arr.some(function(e){return e.isPeriod;}), hasS=arr.some(function(e){return !e.isPeriod;});
    var c='ncc'; if(hasP)c+=' tint'; if((fd+d-1)%7===0)c+=' sun'; if(isCur&&td.getDate()===d)c+=' today'; if(selectedDay===d)c+=' sel';
    html+='<button type="button" class="'+c+'" onclick="selectCalDay('+d+')" aria-label="'+(curM+1)+'월 '+d+'일, 행사 '+arr.length+'건">'+d+(hasS?'<i></i>':'')+'</button>';
  }
  cells.innerHTML=html;
  var items, label, isToday=false;
  if(selectedDay){
    var k2=nKey(curY,curM,selectedDay);
    items=nUniq((calEvs[k2]||[]).map(function(ev){return {k:k2,ev:ev};}));
    label=(curM+1)+'월 '+selectedDay+'일 ('+'일월화수목금토'[new Date(curY,curM,selectedDay).getDay()]+')';
    isToday=isCur&&td.getDate()===selectedDay;
  } else { items=nUniq(monthItems); label=(curM+1)+'월 전체 행사'; }
  window._nEvItems=items;
  var dEl=document.getElementById('n-ev-date'), cEl=document.getElementById('n-ev-count'), lEl=document.getElementById('n-ev-list');
  if(dEl) dEl.innerHTML=label+(isToday?'<small>오늘</small>':'');
  if(cEl) cEl.textContent=items.length?('진행하는 행사 '+items.length+'건'):'';
  if(lEl) lEl.innerHTML=items.length?items.map(function(it,i){
    var ev=it.ev, linked=nFindNews(ev)>=0, op=!linked&&!!nOpenEv[it.id];
    return `<div class="n-ei${op?' open':''}" id="n-ei-${i}">
      <button type="button" class="n-ei-row" ${linked?'aria-label="'+nEsc(ev.title)+' 소식 보기"':'aria-expanded="'+op+'"'} onclick="nToggleEv(${i})">
        ${ev.img?`<img class="n-ei-th" src="${nEsc(ev.img)}" alt="">`:''}
        <span class="n-ei-txt"><span class="n-ei-p">${nPeriod(ev,it.k)}</span><span class="n-ei-t">${nEsc(ev.title)}</span>${ev.hl?`<span class="n-ei-s">${nEsc(ev.hl)}</span>`:''}</span>
        <span class="n-ei-arr${linked?' go':''}" aria-hidden="true">${linked?'자세히 →':(op?'−':'+')}</span>
      </button>
      <div class="n-ei-body">
        ${ev.img?`<img src="${nEsc(ev.img)}" alt="${nEsc(ev.title)}" loading="lazy">`:''}
        ${ev.desc?`<div class="n-ei-desc">${nEsc(ev.desc).replace(/\n/g,'<br>')}</div>`:''}
        <div class="n-ei-cta"><a href="#reservation" onclick="gtag('event','reservation_click',{event_category:'conversion',event_label:'event_banner'})">이 행사 상담 예약하기</a><a class="sec" href="tel:0647587722" onclick="gtag('event','phone_click',{event_category:'conversion',event_label:'event_banner'}); fbq('track','Contact');">전화 문의</a></div>
      </div>
    </div>`;
  }).join(''):'<p class="n-ev-empty">이 날은 등록된 행사가 없습니다.</p>';
  nRenderHero();
}
function nRenderHero(){
  var wrap=document.getElementById('n-evwrap'), store=document.getElementById('n-store'), box=document.getElementById('n-slides');
  if(!wrap||!box||!store) return;
  var n=new Date(), tk=nKey(n.getFullYear(),n.getMonth(),n.getDate());
  var list=nUniq((calEvs[tk]||[]).filter(function(e){return e.img;}).map(function(ev){return {k:tk,ev:ev};}));
  list.sort(function(a,b){return (b.ev.strip?1:0)-(a.ev.strip?1:0);});
  list=list.slice(0,5); nHeroList=list;
  if(!list.length){ wrap.style.display='none'; store.style.display=''; return; }
  store.style.display='none'; wrap.style.display='';
  if(nHeroIdx>=list.length) nHeroIdx=0;
  box.innerHTML=list.map(function(it,i){
    var ev=it.ev;
    return `<div class="n-slide"${i===nHeroIdx?'':' hidden'}>
      <div class="n-slide-txt">
        <div class="n-slide-meta"><span class="n-live">지금 진행 중</span><span>${nPeriod(ev,it.k)}</span></div>
        <h2 class="n-slide-title">${nEsc(ev.title).replace(/\n/g,"<br>")}</h2>
        ${ev.hl?`<p class="n-slide-sub">${nEsc(ev.hl)}</p>`:''}
        <div class="n-btns">
          <a href="tel:0647587722" class="n-btn-p" onclick="gtag('event','phone_click',{event_category:'conversion',event_label:'hero_btn'}); fbq('track','Contact');">전화상담 064-758-7722</a>
          <button type="button" class="n-btn-o" onclick="nHeroDetail(${i})">행사 자세히 보기</button>
        </div>
      </div>
      <div class="n-slide-img"><img src="${nEsc(ev.img)}" alt="${nEsc(ev.title)}"></div>
    </div>`;
  }).join('');
  var pg=document.getElementById('n-pager'), ps=document.getElementById('n-pager-pos');
  if(pg) pg.style.display=list.length>1?'':'none';
  if(ps) ps.textContent='진행 중인 행사 '+(nHeroIdx+1)+' / '+list.length;
}
function nHeroShow(){
  var sl=document.querySelectorAll('#n-slides .n-slide');
  for(var i=0;i<sl.length;i++){ if(i===nHeroIdx) sl[i].removeAttribute('hidden'); else sl[i].setAttribute('hidden',''); }
  var ps=document.getElementById('n-pager-pos');
  if(ps) ps.textContent='진행 중인 행사 '+(nHeroIdx+1)+' / '+nHeroList.length;
}
// 화살표를 누르면 넘어가고, 타이머도 처음부터 다시 센다
function nHeroGo(d,auto){
  if(nHeroList.length<2) return;
  nHeroIdx=(nHeroIdx+d+nHeroList.length)%nHeroList.length; nHeroShow();
  if(!auto) nHeroTimer();
}
// 자동 넘김: 4.5초마다. 손가락을 대고 있는 동안, 팝업·소식 창이 열려 있는 동안은 멈춘다
var nHeroT=null, nHeroHold=false, nHeroLast=Date.now(), N_HERO_MS=4500;
function nHeroTimer(){
  nHeroLast=Date.now();
  if(nHeroT) return;
  // 0.3초마다 확인해서, 마지막으로 넘어간 뒤 4.5초가 지났으면 넘긴다 (잠깐 멈췄다가도 바로 이어서 넘어가도록)
  nHeroT=setInterval(function(){
    if(nHeroHold||document.hidden) return;
    var pop=document.getElementById('popup-overlay'), news=document.getElementById('news-panel');
    if((pop&&pop.style.display!=='none'&&pop.style.display!=='')||(news&&news.classList.contains('open'))){ nHeroLast=Date.now(); return; }
    if(Date.now()-nHeroLast>=N_HERO_MS){ nHeroLast=Date.now(); nHeroGo(1,true); }
  },300);
}
(function(){
  var w=document.getElementById('n-evwrap'); if(!w) return;
  w.addEventListener('touchstart',function(){nHeroHold=true;},{passive:true});
  w.addEventListener('touchend',function(){nHeroHold=false;},{passive:true});
  w.addEventListener('touchcancel',function(){nHeroHold=false;},{passive:true});
  nHeroTimer();
})();
function nFindNews(ev){
  if(typeof newsData==='undefined'||!newsData.length) return -1;
  for(var i=0;i<newsData.length;i++){ if(ev.img&&(newsData[i].photo||'').indexOf(ev.img)>=0) return i; }
  var t=(ev.title||'').replace(/\s/g,'');
  for(var j=0;j<newsData.length;j++){ var nt=(newsData[j].title||'').replace(/\s/g,''); if(t&&(nt.indexOf(t)>=0||t.indexOf(nt)>=0)) return j; }
  // 이미지·제목으로 못 찾으면 시작일이 같은 소식 글이 하나뿐일 때 그 글로 연결
  if(ev.rangeStart){
    var c=[]; for(var m=0;m<newsData.length;m++){ if(newsData[m].startDate===ev.rangeStart) c.push(m); }
    if(c.length===1) return c[0];
    var c2=c.filter(function(x){return (newsData[x].endDate||newsData[x].startDate)===(ev.rangeEnd||ev.rangeStart);});
    if(c2.length===1) return c2[0];
  }
  return -1;
}
function nShowInCal(it){
  var t=new Date(); curY=t.getFullYear(); curM=t.getMonth(); window._nMonth=curY+'-'+curM; selectedDay=t.getDate();
  nOpenEv[it.id]=true; renderCal();
  var sec=document.getElementById('events'); if(sec) sec.scrollIntoView({behavior:'smooth'});
}
// 첫 화면 "행사 자세히 보기": 같은 행사의 소식 글이 있으면 소식 창으로, 없으면 달력으로
async function nOpenEvNews(ev, it, label){
  if(typeof newsData!=='undefined'&&!newsData.length){ try{ await loadNewsSheet(); }catch(e){} }
  var idx=nFindNews(ev);
  if(window.gtag) gtag('event',label,{event_category:'engagement',event_label:ev.title});
  if(idx>=0){ openNews(idx); if(window.fbq) fbq('track','ViewContent'); }
  else if(it) nShowInCal(it);
}
function nHeroDetail(i){ var it=nHeroList[i]; if(it) nOpenEvNews(it.ev,it,'hero_event_click'); }
function nEvNews(i){ var it=window._nEvItems&&window._nEvItems[i]; if(it) nOpenEvNews(it.ev,null,'event_news_click'); }
try{ renderCal(); }catch(e){}
// 팝업: 이전으로 돌아가기
function closePopupPrev(){ if(popupIdx>0) showQueuePopup(popupIdx-1); }
(function(){
  var orig=showQueuePopup;
  showQueuePopup=function(i){
    orig(i);
    var pb=document.getElementById('popup-prev-btn');
    if(pb) pb.style.display=(popupQueue.length>1&&popupIdx>0)?'':'none';
  };
})();
// 소식이 불러와지면 달력 목록의 "소식에서 자세히 보기" 버튼이 나타나도록 다시 그린다
(function(){
  var orig=renderInlineNews;
  renderInlineNews=function(){ orig(); try{ renderCal(); }catch(e){} };
})();
