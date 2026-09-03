(()=>{
  const MIN_LOCK_DISTANCE=1;
  let direction=null,lastDeviation=0;
  function clear(){direction=null;lastDeviation=0;document.querySelector('#firstEdgeGuide')?.classList.remove('locked','show');}
  function install(){
    if(typeof frame!=='function'||typeof dist!=='function')return setTimeout(install,80);
    const actions=document.querySelector('.ar-actions');if(!actions)return setTimeout(install,80);
    const guide=document.createElement('button');guide.id='firstEdgeGuide';guide.type='button';guide.innerHTML='<strong>⦿ Ustaw kierunek P1→P2</strong><small>Odejdź min. 1 m i wyceluj wzdłuż krawędzi</small>';
    actions.before(guide);
    const style=document.createElement('style');style.textContent=`#firstEdgeGuide{display:none;width:100%;min-height:54px;margin:4px 0;border:1px solid #ffffff3b;border-radius:15px;background:#123b32;color:#fff;padding:8px 12px;font-weight:900}#firstEdgeGuide.show{display:block}#firstEdgeGuide strong,#firstEdgeGuide small{display:block}#firstEdgeGuide small{margin-top:3px;color:#bdd6cc;font-size:.68rem}#firstEdgeGuide.locked{display:block;background:#274e2e;border-color:#dfff73;color:#dfff73}#firstEdgeGuide.locked small{color:#e7ffc0}`;document.head.appendChild(style);
    guide.onclick=event=>{event.preventDefault();event.stopPropagation();if(!Array.isArray(pts)||pts.length!==1||!hit)return;const dx=hit.x-pts[0].x,dy=hit.y-pts[0].y,length=Math.hypot(dx,dy);if(length<MIN_LOCK_DISTANCE)return;direction={x:dx/length,y:dy/length};navigator.vibrate?.(35);guide.classList.add('locked');};
    const baseFrame=frame;
    frame=function(t,f){
      baseFrame(t,f);
      try{
        const active=Array.isArray(pts)&&pts.length===1&&hit,travel=active?dist(pts[0],hit):0;
        guide.classList.toggle('show',Boolean(active&&travel>=MIN_LOCK_DISTANCE));
        if(!active){if(!Array.isArray(pts)||pts.length!==1)clear();return;}
        if(direction){
          const dx=hit.x-pts[0].x,dy=hit.y-pts[0].y,along=dx*direction.x+dy*direction.y;
          const projected={...hit,x:pts[0].x+direction.x*along,y:pts[0].y+direction.y*along};
          lastDeviation=Math.abs(dx*direction.y-dy*direction.x);projected.wx=projected.x;projected.wz=-projected.y;hit=projected;
          guide.classList.add('locked');guide.querySelector('strong').textContent='✓ Kierunek P1→P2 zablokowany';guide.querySelector('small').textContent=`Korekta boczna: ${lastDeviation.toFixed(2).replace('.',',')} m`;
          updateMeasure?.();updateMiniMap?.();
        }else{guide.querySelector('strong').textContent='⦿ Ustaw kierunek P1→P2';guide.querySelector('small').textContent=`Aktualna odległość: ${travel.toFixed(2).replace('.',',')} m`;}
      }catch(error){}
    };
    document.querySelector('#startAr')?.addEventListener('click',clear);document.querySelector('#newOne')?.addEventListener('click',clear);
  }
  install();
})();
