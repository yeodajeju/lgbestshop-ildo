// 미리보기 전용: 소식 시트에만 있고 이벤트 시트에는 아직 없는 11월 행사 (반영 시 이벤트 시트로 옮기고 이 파일은 빼요)
function nAddExtra(){
  var extra=[
    {s:'2026-11-01',e:'2026-11-30',title:'코리아 그랜드 페스티벌 쿠폰팩',desc:'베스트샵에서만 받는 최대 104만 혜택. 자세한 혜택은 매니저 상담으로 확인하세요.',img:'images/events/coupon-pack-nov.jpg',hl:'베스트샵에서만 받는 최대 104만 혜택'},
    {s:'2026-11-01',e:'2026-11-30',title:'김치냉장고 Fit&Max 구독 혜택전',desc:'김치냉장고 구매의 골든타임! 최대 100만 혜택. 자세한 혜택은 매니저 상담으로 확인하세요.',img:'images/events/kimchi-fridge-nov.jpg',hl:'최대 100만 혜택'},
    {s:'2026-11-05',e:'2026-11-30',title:'전시제품 대방출',desc:'TV·냉장고·김치냉장고·에어컨 전시제품 특가.',img:'images/events/display-sale-nov.jpg',hl:'TV·냉장고·김치냉장고·에어컨 전시제품 특가'},
    {s:'2026-11-19',e:'2026-11-30',title:'수험생 한정 LG gram 노트북 할인',desc:'수험생 한정 LG gram 노트북 할인, 수험생·가족 대상 사은품 1+1.\n방문하실 때 수험표를 꼭 가져와 주세요.',img:'images/events/csat-nov.jpg',hl:'수험생·가족 사은품 1+1 · 수험표 지참'}
  ];
  extra.forEach(function(x){
    for(var d=new Date(x.s); d<=new Date(x.e); d.setDate(d.getDate()+1)){
      var key=d.toISOString().slice(0,10);
      if(!calEvs[key]) calEvs[key]=[];
      if(!calEvs[key].some(function(e){return e.title===x.title;})) calEvs[key].push({title:x.title,desc:x.desc,img:x.img,strip:'',hl:x.hl,isRange:true,rangeStart:x.s,rangeEnd:x.e,isPeriod:true});
    }
  });
}
