(()=>{
  const HIDE_NEAR_P1=.8,ANGLE_READY=2;
  function reticleCenter(){const r=document.querySelector('#reticle')?.getBoundingClientRect();return r?{x:r.left+r.width/2,y:r.top+r.height/2}:{x:innerWidth/2,y:innerHeight/2};}
  function approximateTarget(point,view,origin){
    if(!point||!view||!Number.isFinite(point.wx))return{x:origin.x-innerWidth*2,y:origin.y};
    const m=view.transform.matrix,vx=point.wx-m[12],vy=point.wy-m[13],vz=point.wz-m[14],right=vx*m[0]+vy*m[1]+vz*m[2],up=vx*m[4]+vy*m[5]+vz*m[6],len=Math.hypot(right,up)||1;
    return{x:origin.x+right/len*Math.max(innerWidth,innerHeight)*2,y:origin.y-up/len*Math.max(innerWidth,innerHeight)*2};
  }
  function clippedTarget(origin,target){
    const sheetTop=document.querySelector('.ar-sheet')?.getBoundingClientRect().top||innerHeight-16,minX=16,maxX=innerWidth-16,minY=92,maxY=Math.max(130,sheetTop-16),dx=target.x-origin.x,dy=target.y-origin.y;let t=1;
    if(dx>0)t=Math.min(t,(maxX-origin.x)/dx);if(dx<0)t=Math.min(t,(minX-origin.x)/dx);if(dy>0)t=Math.min(t,(maxY-origin.y)/dy);if(dy<0)t=Math.min(t,(minY-origin.y)/dy);
    return{x:origin.x+dx*Math.max(0,Math.min(1,t)),y:origin.y+dy*Math.max(0,Math.min(1,t)),clipped:t<.999};
  }
  function closingAngle(poly,current){
    const first={x:poly[1].x-poly[0].x,y:poly[1].y-poly[0].y},closing={x:poly[0].x-current.x,y:poly[0].y-current.y},den=Math.hypot(first.x,first.y)*Math.hypot(closing.x,closing.y);if(!den)return null;
    const angle=Math.acos(Math.max(-1,Math.min(1,(first.x*closing.x+first.y*closing.y)/den)))*180/Math.PI;return Math.min(angle,180-angle);
  }
  function install(){
    if(typeof frame!=='function'||typeof projectScreen!=='function'||typeof dist!=='function')return setTimeout(install,80);
    const ar=document.querySelector('#ar');if(!ar)return setTimeout(install,80);
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.id='p1GuideSvg';svg.setAttribute('aria-hidden','true');svg.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:4;pointer-events:none;overflow:hidden';ar.appendChild(svg);
    const style=document.createElement('style');style.textContent=`#p1GuideSvg .p1-guide{stroke:#7fe4ff;stroke-width:4;stroke-dasharray:11 9;stroke-linecap:round;filter:drop-shadow(0 2px 3px #08271f)}#p1GuideSvg .p1-guide.ready{stroke:#dfff73;stroke-width:6}#p1GuideSvg .p1-dot{fill:#7fe4ff;stroke:#fff;stroke-width:3}#p1GuideSvg .p1-dot.ready{fill:#dfff73}#p1GuideSvg .p1-label{font-size:17px;font-weight:950;fill:#7fe4ff;stroke:#12372e;stroke-width:6px;paint-order:stroke;stroke-linejoin:round}#p1GuideSvg .p1-label.ready{fill:#dfff73}`;document.head.appendChild(style);
    const clear=()=>{svg.innerHTML='';};
    function draw(pose){
      if(!Array.isArray(pts)||pts.length<3||!hit||editIndex>=0||!pose?.views?.length||dist(hit,pts[0])<=HIDE_NEAR_P1)return clear();
      const view=pose.views[0],origin=reticleCenter(),screen=projectScreen(pts[0],view),raw=screen&&Number.isFinite(screen.x)&&Number.isFinite(screen.y)?screen:approximateTarget(pts[0],view,origin),target=clippedTarget(origin,raw),distance=dist(hit,pts[0]),angle=closingAngle(pts,hit),ready=angle!==null&&Math.abs(90-angle)<=ANGLE_READY;
      const dx=target.x-origin.x,dy=target.y-origin.y,len=Math.hypot(dx,dy)||1,ux=dx/len,uy=dy/len,labelX=target.x-ux*44,labelY=target.y-uy*44;
      svg.setAttribute('viewBox',`0 0 ${innerWidth} ${innerHeight}`);svg.innerHTML=`<line class="p1-guide ${ready?'ready':''}" x1="${origin.x}" y1="${origin.y}" x2="${target.x}" y2="${target.y}"/><circle class="p1-dot ${ready?'ready':''}" cx="${target.x}" cy="${target.y}" r="9"/><text class="p1-label ${ready?'ready':''}" x="${labelX}" y="${labelY}" text-anchor="middle">P1 • ${distance.toFixed(2).replace('.',',')} m${angle===null?'':` • ${angle.toFixed(1).replace('.',',')}°`}</text>`;
    }
    const baseFrame=frame;frame=function(t,f){baseFrame(t,f);let pose=null;try{pose=f.getViewerPose(refSpace);}catch(error){}try{draw(pose);}catch(error){clear();}};
    document.querySelector('#startAr')?.addEventListener('click',clear);document.querySelector('#newOne')?.addEventListener('click',clear);
  }
  window.ekoosP1GuideApi={closingAngle,clippedTarget};
  install();
})();
