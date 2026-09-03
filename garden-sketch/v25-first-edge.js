(()=>{
  const MIN_LOCK_DISTANCE=1;
  let direction=null,lastDeviation=0;
  function clear(){direction=null;lastDeviation=0;document.querySelector('#firstEdgeGuide')?.classList.remove('locked','show');document.querySelector('#firstEdgeMeter')?.classList.remove('show','straight');}
  function install(){
    if(typeof frame!=='function'||typeof dist!=='function')return setTimeout(install,80);
    const actions=document.querySelector('.ar-actions');if(!actions)return setTimeout(install,80);
    const guide=document.createElement('button');guide.id='firstEdgeGuide';guide.type='button';guide.innerHTML='<strong>⦿ Ustaw P1→P2 jako oś projektu</strong><small>Odejdź min. 1 m i wyceluj wzdłuż krawędzi</small>';
    actions.before(guide);
    const meter=document.createElement('div');meter.id='firstEdgeMeter';meter.innerHTML='<small>OŚ PROJEKTU P1→P2</small><strong id="firstEdgeAngle">0,0°</strong><span id="firstEdgeSide">IDEALNIE PROSTO</span><div class="edge-level"><i></i></div>';document.querySelector('#ar')?.appendChild(meter);
    const style=document.createElement('style');style.textContent=`#firstEdgeGuide{display:none;width:100%;min-height:54px;margin:4px 0;border:1px solid #ffffff3b;border-radius:15px;background:#123b32;color:#fff;padding:8px 12px;font-weight:900}#firstEdgeGuide.show{display:block}#firstEdgeGuide strong,#firstEdgeGuide small{display:block}#firstEdgeGuide small{margin-top:3px;color:#bdd6cc;font-size:.68rem}#firstEdgeGuide.locked{display:block;background:#274e2e;border-color:#dfff73;color:#dfff73}#firstEdgeGuide.locked small{color:#e7ffc0}#firstEdgeMeter{display:none;position:absolute;z-index:7;right:14px;top:max(178px,calc(env(safe-area-inset-top) + 166px));width:142px;padding:9px 11px;border-radius:15px;background:#092a23ef;border:1px solid #ffffff35;text-align:center;box-shadow:0 8px 24px #0005}#firstEdgeMeter.show{display:block}#firstEdgeMeter small{display:block;color:#b9d1c8;font-size:.57rem;font-weight:900}#firstEdgeMeter strong{display:block;color:#ffd17a;font-size:1.45rem;line-height:1.15}#firstEdgeMeter span{display:block;color:#ffd17a;font-size:.65rem;font-weight:900}.edge-level{position:relative;height:7px;margin-top:7px;border-radius:9px;background:linear-gradient(90deg,#df8b4b,#dfff73 45%,#dfff73 55%,#df8b4b)}.edge-level:after{content:'';position:absolute;left:50%;top:-3px;width:2px;height:13px;background:#fff}.edge-level i{position:absolute;left:50%;top:50%;width:13px;height:13px;border-radius:50%;background:#fff;border:2px solid #173f35;transform:translate(-50%,-50%);transition:left .12s}#firstEdgeMeter.straight{border-color:#dfff73;box-shadow:0 0 0 3px #dfff7325,0 8px 24px #0005}#firstEdgeMeter.straight strong,#firstEdgeMeter.straight span{color:#dfff73}`;document.head.appendChild(style);
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
          const cross=direction.x*dy-direction.y*dx,signedAngle=Math.atan2(cross,Math.max(.01,along))*180/Math.PI;
          lastDeviation=Math.abs(cross);projected.wx=projected.x;projected.wz=-projected.y;hit=projected;
          const straight=Math.abs(signedAngle)<=1,side=cross>0?'W PRAWO':cross<0?'W LEWO':'IDEALNIE PROSTO';
          guide.classList.add('locked');guide.querySelector('strong').textContent='✓ Oś projektu P1→P2 ustawiona';guide.querySelector('small').textContent='P2 zostanie zapisany dokładnie na tej osi';
          meter.classList.add('show');meter.classList.toggle('straight',straight);meter.querySelector('#firstEdgeAngle').textContent=`${Math.abs(signedAngle).toFixed(1).replace('.',',')}°`;
          meter.querySelector('#firstEdgeSide').textContent=straight?'IDEALNIE PROSTO':`${side} • ${lastDeviation.toFixed(2).replace('.',',')} m`;meter.querySelector('.edge-level i').style.left=`${Math.max(6,Math.min(94,50+signedAngle/8*44))}%`;
          updateMeasure?.();updateMiniMap?.();
        }else{meter.classList.remove('show','straight');guide.querySelector('strong').textContent='⦿ Ustaw P1→P2 jako oś projektu';guide.querySelector('small').textContent=`Aktualna odległość: ${travel.toFixed(2).replace('.',',')} m`;}
      }catch(error){}
    };
    document.querySelector('#startAr')?.addEventListener('click',clear);document.querySelector('#newOne')?.addEventListener('click',clear);
  }
  install();
})();
