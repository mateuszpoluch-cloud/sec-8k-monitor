(()=>{
  const GUIDE_ANGLES=[45,90,135,180];

  function install(){
    if(typeof updateMiniMap!=='function'||typeof updateWorldOverlay!=='function'||typeof projectScreen!=='function'){
      return setTimeout(install,80);
    }
    if(document.querySelector('#ekoosAngleCard'))return;

    const ar=document.querySelector('#ar');
    if(!ar)return setTimeout(install,80);

    const angleCard=document.createElement('div');
    angleCard.id='ekoosAngleCard';
    angleCard.innerHTML='<small>KĄT W NAROŻNIKU</small><strong id="ekoosAngleValue">—</strong><span id="ekoosAngleHint">P2</span>';
    ar.appendChild(angleCard);

    const angleSvg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    angleSvg.id='ekoosAngleSvg';
    angleSvg.setAttribute('aria-hidden','true');
    angleSvg.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:4;pointer-events:none;overflow:visible';
    ar.appendChild(angleSvg);

    const style=document.createElement('style');
    style.textContent=`
      #ekoosAngleCard{display:none;position:absolute;z-index:6;left:14px;top:max(178px,calc(env(safe-area-inset-top) + 166px));min-width:116px;padding:9px 12px;border-radius:16px;background:#08271fe8;border:1px solid #ffffff2d;box-shadow:0 10px 28px #0004;text-align:center}
      #ekoosAngleCard.show{display:block}
      #ekoosAngleCard small{display:block;color:#bad3ca;font-size:.58rem;font-weight:900;letter-spacing:.04em}
      #ekoosAngleCard strong{display:block;margin-top:1px;color:#fff;font-size:1.55rem;line-height:1.05}
      #ekoosAngleCard span{display:block;margin-top:2px;color:#bcd3ca;font-size:.65rem;font-weight:800}
      #ekoosAngleCard.guide{background:#183e25ed;border-color:#c9f36b99;box-shadow:0 0 0 3px #c9f36b25,0 10px 28px #0004}
      #ekoosAngleCard.guide strong,#ekoosAngleCard.guide span{color:#dfff73}
      #ekoosAngleSvg .angle-ray{stroke:#dfff73;stroke-width:3;stroke-linecap:round;opacity:.82}
      #ekoosAngleSvg .angle-arc{fill:none;stroke:#dfff73;stroke-width:5;stroke-linecap:round;filter:drop-shadow(0 2px 3px #153d35)}
      #ekoosAngleSvg .angle-label{font-size:18px;font-weight:950;fill:#dfff73;stroke:#153d35;stroke-width:6;paint-order:stroke;stroke-linejoin:round}
      @media(max-width:700px){#ekoosAngleCard{left:12px;top:max(174px,calc(env(safe-area-inset-top) + 160px));min-width:104px;padding:8px 10px}#ekoosAngleCard strong{font-size:1.38rem}}
    `;
    document.head.appendChild(style);

    function rotatePreview(points){
      if(!points.length)return points;
      let a=0,b=null;
      if(points.length>=2)b=points[1];
      else if(points.length===1&&typeof hit!=='undefined'&&hit)b=hit;
      if(!b)return points.map(p=>({...p}));
      const p0=points[0];
      const dx=b.x-p0.x,dy=b.y-p0.y;
      if(Math.hypot(dx,dy)<.001)return points.map(p=>({...p}));
      const angle=Math.PI/2-Math.atan2(dy,dx);
      const co=Math.cos(angle),si=Math.sin(angle);
      return points.map(p=>{
        const x=p.x-p0.x,y=p.y-p0.y;
        return{...p,x:x*co-y*si,y:x*si+y*co};
      });
    }

    updateMiniMap=function(){
      let preview=[];
      try{
        preview=Array.isArray(pts)?pts.map(p=>({...p})):[];
        if(hit&&typeof editIndex!=='undefined'&&editIndex>=0)preview[editIndex]={...hit};
        else if(hit&&preview.length)preview.push({...hit});
      }catch(e){}
      const svg=document.querySelector('#miniMapSvg');
      if(!svg)return;
      if(!preview.length){
        svg.innerHTML='<text x="63" y="48" text-anchor="middle" fill="#adc8bd" font-size="10">Dodaj pierwszy punkt</text>';
        return;
      }
      const rotated=rotatePreview(preview);
      const xs=rotated.map(p=>p.x),ys=rotated.map(p=>p.y);
      const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
      const w=Math.max(maxX-minX,.2),h=Math.max(maxY-minY,.2),pad=9;
      const scale=Math.min((126-pad*2)/w,(92-pad*2)/h);
      const tx=x=>pad+(x-minX)*scale;
      const ty=y=>92-pad-(y-minY)*scale;
      const line=rotated.map((p,i)=>(i?'L':'M')+tx(p.x).toFixed(2)+' '+ty(p.y).toFixed(2)).join(' ');
      const savedCount=(typeof pts!=='undefined'&&Array.isArray(pts))?pts.length:0;
      const dots=rotated.map((p,i)=>{
        const live=i>=savedCount;
        return`<circle cx="${tx(p.x)}" cy="${ty(p.y)}" r="${live?4.4:3.7}" fill="${live?'#dfff73':p.projected?'#ffc65a':'#76c49c'}" ${live?'stroke="#fff" stroke-width="1.2"':''}/>`;
      }).join('');
      svg.innerHTML=`<path d="${line}" fill="none" stroke="#76c49c" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>${dots}`;
    };

    function liveAngle(){
      try{
        if(!Array.isArray(pts)||pts.length<2||!hit||editIndex>=0)return null;
        const previous=pts[pts.length-2],vertex=pts[pts.length-1],next=hit;
        const ax=previous.x-vertex.x,ay=previous.y-vertex.y;
        const bx=next.x-vertex.x,by=next.y-vertex.y;
        const la=Math.hypot(ax,ay),lb=Math.hypot(bx,by);
        if(la<.03||lb<.03)return null;
        const cosine=Math.max(-1,Math.min(1,(ax*bx+ay*by)/(la*lb)));
        return Math.acos(cosine)*180/Math.PI;
      }catch(e){return null;}
    }

    function nearestGuide(value){
      let best=GUIDE_ANGLES[0],delta=Infinity;
      for(const guide of GUIDE_ANGLES){const d=Math.abs(value-guide);if(d<delta){delta=d;best=guide;}}
      return{guide:best,delta};
    }

    function reticleCenter(){
      const r=document.querySelector('#reticle')?.getBoundingClientRect();
      return r?{x:r.left+r.width/2,y:r.top+r.height/2}:{x:innerWidth/2,y:innerHeight*.5};
    }

    function drawAngle(pose,value){
      if(value==null||!pose?.views?.length||!Array.isArray(pts)||pts.length<2){angleSvg.innerHTML='';return;}
      const view=pose.views[0],previous=pts[pts.length-2],vertex=pts[pts.length-1];
      const p0=projectScreen(previous,view),pv=projectScreen(vertex,view),pn=reticleCenter();
      if(!p0||!pv||!Number.isFinite(p0.x)||!Number.isFinite(pv.x)){angleSvg.innerHTML='';return;}
      const a1=Math.atan2(p0.y-pv.y,p0.x-pv.x),a2=Math.atan2(pn.y-pv.y,pn.x-pv.x);
      let delta=a2-a1;while(delta>Math.PI)delta-=Math.PI*2;while(delta<-Math.PI)delta+=Math.PI*2;
      const r=42,start={x:pv.x+Math.cos(a1)*r,y:pv.y+Math.sin(a1)*r},end={x:pv.x+Math.cos(a1+delta)*r,y:pv.y+Math.sin(a1+delta)*r};
      const mid=a1+delta/2,label={x:pv.x+Math.cos(mid)*(r+22),y:pv.y+Math.sin(mid)*(r+22)};
      angleSvg.setAttribute('viewBox',`0 0 ${innerWidth} ${innerHeight}`);
      angleSvg.innerHTML=`<line class="angle-ray" x1="${pv.x}" y1="${pv.y}" x2="${start.x}" y2="${start.y}"/><line class="angle-ray" x1="${pv.x}" y1="${pv.y}" x2="${end.x}" y2="${end.y}"/><path class="angle-arc" d="M ${start.x} ${start.y} A ${r} ${r} 0 0 ${delta>=0?1:0} ${end.x} ${end.y}"/><text class="angle-label" x="${label.x}" y="${label.y}" text-anchor="middle" dominant-baseline="middle">${value.toFixed(1).replace('.',',')}°</text>`;
    }

    function updateAngle(pose){
      const value=liveAngle();
      if(value==null||!ar.classList.contains('active')){
        angleCard.classList.remove('show','guide');
        angleSvg.innerHTML='';
        return;
      }
      const near=nearestGuide(value);
      angleCard.classList.add('show');
      angleCard.classList.toggle('guide',near.delta<=3);
      document.querySelector('#ekoosAngleValue').textContent=value.toFixed(1).replace('.',',')+'°';
      document.querySelector('#ekoosAngleHint').textContent=near.delta<=3?`PRAWIE ${near.guide}°`:`w P${pts.length}`;
      drawAngle(pose,value);
    }

    const baseWorld=updateWorldOverlay;
    updateWorldOverlay=function(pose){
      const result=baseWorld.apply(this,arguments);
      try{updateAngle(pose);}catch(e){angleCard.classList.remove('show','guide');angleSvg.innerHTML='';}
      return result;
    };

    document.querySelector('#startAr')?.addEventListener('click',()=>{
      angleCard.classList.remove('show','guide');
      angleSvg.innerHTML='';
    });
  }

  install();
})();