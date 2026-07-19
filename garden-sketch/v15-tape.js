(()=>{
  let lastDirection={x:-1,y:0};

  function install(){
    if(typeof updateWorldOverlay!=='function') return setTimeout(install,80);
    const ar=document.querySelector('#ar');
    if(!ar) return setTimeout(install,80);

    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.id='ekoosTapeSvg';
    svg.setAttribute('aria-hidden','true');
    svg.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:3;pointer-events:none;overflow:visible';
    ar.appendChild(svg);

    const style=document.createElement('style');
    style.textContent=`
      #ekoosTapeSvg .ekoos-live-tape{stroke-linecap:round;stroke-width:7;stroke-dasharray:18 12;filter:drop-shadow(0 2px 2px #12382f)}
      #ekoosTapeSvg .ekoos-tape-edge{stroke:#fff;stroke-width:3}
      #ekoosTapeSvg .ekoos-tape-label{font-size:20px;font-weight:950;paint-order:stroke;stroke:#153d35;stroke-width:6px;stroke-linejoin:round}
    `;
    document.head.appendChild(style);

    function reticleCenter(){
      const r=document.querySelector('#reticle')?.getBoundingClientRect();
      return r?{x:r.left+r.width/2,y:r.top+r.height/2}:{x:innerWidth/2,y:innerHeight*.5};
    }

    function approximateDirection(anchor,view,ret){
      try{
        if(anchor&&Number.isFinite(anchor.wx)&&view){
          const m=view.transform.matrix;
          const vx=anchor.wx-m[12],vy=anchor.wy-m[13],vz=anchor.wz-m[14];
          const right=vx*m[0]+vy*m[1]+vz*m[2];
          const up=vx*m[4]+vy*m[5]+vz*m[6];
          const length=Math.hypot(right,up);
          if(length>.0001) return {x:right/length,y:-up/length};
        }
      }catch(e){}
      return lastDirection;
    }

    function screenTarget(anchor,view,ret){
      try{
        const p=projectScreen(anchor,view);
        if(p&&Number.isFinite(p.x)&&Number.isFinite(p.y)){
          const dx=p.x-ret.x,dy=p.y-ret.y,len=Math.hypot(dx,dy);
          if(len>5) lastDirection={x:dx/len,y:dy/len};
          return {x:p.x,y:p.y};
        }
      }catch(e){}
      const d=approximateDirection(anchor,view,ret);
      lastDirection=d;
      const reach=Math.max(innerWidth,innerHeight)*2;
      return {x:ret.x+d.x*reach,y:ret.y+d.y*reach};
    }

    function clipToVisibleArea(ret,target){
      const sheetTop=document.querySelector('.ar-sheet')?.getBoundingClientRect().top||innerHeight-12;
      const minX=12,maxX=innerWidth-12,minY=100,maxY=Math.max(120,sheetTop-14);
      const dx=target.x-ret.x,dy=target.y-ret.y;
      let t=1;
      if(dx>0)t=Math.min(t,(maxX-ret.x)/dx);
      if(dx<0)t=Math.min(t,(minX-ret.x)/dx);
      if(dy>0)t=Math.min(t,(maxY-ret.y)/dy);
      if(dy<0)t=Math.min(t,(minY-ret.y)/dy);
      if(!Number.isFinite(t)||t<0)t=0;
      t=Math.min(1,t);
      return {x:ret.x+dx*t,y:ret.y+dy*t,clipped:t<.999};
    }

    function draw(pose){
      let points=[],currentHit=null,currentEdit=-1,projected=false;
      try{points=Array.isArray(pts)?pts:[];currentHit=hit;currentEdit=editIndex;projected=!!usingProjection;}catch(e){}
      if(!ar.classList.contains('active')||!points.length||!currentHit||!pose?.views?.length){svg.innerHTML='';return;}

      const anchor=currentEdit>=0?points[currentEdit]:points.at(-1);
      if(!anchor){svg.innerHTML='';return;}
      const ret=reticleCenter();
      const target=screenTarget(anchor,pose.views[0],ret);
      const start=clipToVisibleArea(ret,target);
      const color=projected?'#ffc65a':'#d7ef85';
      let value=0;
      try{value=dist(anchor,currentHit);}catch(e){}
      const text=Number.isFinite(value)?value.toFixed(2).replace('.',',')+' m':'';
      const mx=start.x+(ret.x-start.x)*.48,my=start.y+(ret.y-start.y)*.48-12;
      svg.setAttribute('viewBox',`0 0 ${innerWidth} ${innerHeight}`);
      svg.innerHTML=`
        <line class="ekoos-live-tape" x1="${start.x}" y1="${start.y}" x2="${ret.x}" y2="${ret.y}" stroke="${color}"/>
        ${start.clipped?`<circle class="ekoos-tape-edge" cx="${start.x}" cy="${start.y}" r="7" fill="${color}"/>`:''}
        <text class="ekoos-tape-label" x="${mx}" y="${my}" text-anchor="middle" fill="${color}">${text}</text>
      `;
    }

    const baseUpdateWorldOverlay=updateWorldOverlay;
    updateWorldOverlay=function(pose){
      const result=baseUpdateWorldOverlay.apply(this,arguments);
      try{draw(pose);}catch(e){svg.innerHTML='';}
      return result;
    };

    document.querySelector('#startAr')?.addEventListener('click',()=>{lastDirection={x:-1,y:0};svg.innerHTML='';});
  }

  install();
})();