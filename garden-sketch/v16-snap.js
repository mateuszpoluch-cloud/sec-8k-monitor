(()=>{
  const ENTER_RADIUS=0.60;
  const EXIT_RADIUS=0.90;
  let snapped=false;
  let lastCandidate=null;

  function install(){
    if(typeof frame!=='function'||typeof dist!=='function'||typeof projectScreen!=='function'){
      return setTimeout(install,80);
    }

    const ar=document.querySelector('#ar');
    const sheet=document.querySelector('.ar-sheet');
    const actions=document.querySelector('.ar-actions');
    if(!ar||!sheet||!actions)return setTimeout(install,80);

    const closeButton=document.createElement('button');
    closeButton.id='closeAreaButton';
    closeButton.type='button';
    closeButton.innerHTML='<span>◎ Zamknij obszar</span><small>Punkt P1 został złapany</small>';
    actions.before(closeButton);

    const snapSvg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    snapSvg.id='ekoosSnapSvg';
    snapSvg.setAttribute('aria-hidden','true');
    snapSvg.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:4;pointer-events:none;overflow:visible';
    ar.appendChild(snapSvg);

    const style=document.createElement('style');
    style.textContent=`
      #closeAreaButton{display:none;width:100%;min-height:68px;border:0;border-radius:18px;padding:10px 16px;background:linear-gradient(135deg,#b8e95f,#48bf82);color:#153d35;font-weight:950;box-shadow:0 10px 28px #0005;margin:5px 0 2px}
      #closeAreaButton span{display:block;font-size:1.18rem;line-height:1.15}
      #closeAreaButton small{display:block;margin-top:3px;font-size:.7rem;font-weight:800;opacity:.78}
      .ar-sheet.snap-ready #closeAreaButton{display:block}
      .ar-sheet.snap-ready .ar-actions{display:none}
      .ar-sheet.snap-ready #pointStrip{display:none!important}
      .ar-sheet.snap-ready .ar-info{color:#dfff9a}
      #reticle.snap-ready{border-color:#dfff73!important;box-shadow:0 0 0 15px #c9f36b3d,0 0 28px #c9f36baa!important;animation:ekoosReticlePulse .85s ease-in-out infinite alternate}
      #reticle.snap-ready:before,#reticle.snap-ready:after{background:#dfff73!important}
      #ekoosSnapSvg .snap-link{stroke:#dfff73;stroke-width:5;stroke-dasharray:10 8;stroke-linecap:round;filter:drop-shadow(0 2px 3px #153d35)}
      #ekoosSnapSvg .snap-ring{fill:#c9f36b25;stroke:#dfff73;stroke-width:6;transform-box:fill-box;transform-origin:center;animation:ekoosSnapPulse .75s ease-in-out infinite alternate;filter:drop-shadow(0 2px 4px #153d35)}
      #ekoosSnapSvg .snap-core{fill:#dfff73;stroke:#fff;stroke-width:3}
      #ekoosSnapSvg .snap-label{font-size:19px;font-weight:950;fill:#dfff73;stroke:#153d35;stroke-width:6;paint-order:stroke;stroke-linejoin:round}
      @keyframes ekoosSnapPulse{from{transform:scale(.82);opacity:.65}to{transform:scale(1.18);opacity:1}}
      @keyframes ekoosReticlePulse{from{transform:translate(-50%,-50%) scale(.82)}to{transform:translate(-50%,-50%) scale(.91)}}
    `;
    document.head.appendChild(style);

    function reticleCenter(){
      const r=document.querySelector('#reticle')?.getBoundingClientRect();
      return r?{x:r.left+r.width/2,y:r.top+r.height/2}:{x:innerWidth/2,y:innerHeight*.5};
    }

    function drawSnap(pose){
      if(!snapped||!pose?.views?.length||!pts?.[0]){
        snapSvg.innerHTML='';
        return;
      }
      const p=projectScreen(pts[0],pose.views[0]);
      if(!p||!Number.isFinite(p.x)||!Number.isFinite(p.y)){
        snapSvg.innerHTML='';
        return;
      }
      const ret=reticleCenter();
      snapSvg.setAttribute('viewBox',`0 0 ${innerWidth} ${innerHeight}`);
      snapSvg.innerHTML=`
        <line class="snap-link" x1="${ret.x}" y1="${ret.y}" x2="${p.x}" y2="${p.y}"/>
        <circle class="snap-ring" cx="${p.x}" cy="${p.y}" r="30"/>
        <circle class="snap-core" cx="${p.x}" cy="${p.y}" r="9"/>
        <text class="snap-label" x="${p.x}" y="${p.y-39}" text-anchor="middle">P1 • ZAMKNIJ</text>
      `;
    }

    function leaveSnap(){
      if(!snapped)return;
      snapped=false;
      sheet.classList.remove('snap-ready');
      document.querySelector('#reticle')?.classList.remove('snap-ready');
      snapSvg.innerHTML='';
    }

    function applySnap(candidate,pose){
      const enough=Array.isArray(pts)&&pts.length>=3&&pts[0]&&candidate;
      if(!enough){
        leaveSnap();
        return;
      }

      const distanceToStart=dist(candidate,pts[0]);
      if(!snapped&&distanceToStart<=ENTER_RADIUS){
        snapped=true;
        navigator.vibrate?.([35,35,70]);
      }else if(snapped&&distanceToStart>EXIT_RADIUS){
        leaveSnap();
        return;
      }

      if(!snapped){
        if(distanceToStart<1.25&&typeof updateArMode==='function'){
          const info=document.querySelector('#arInfo');
          if(info)info.textContent=`Zbliżasz się do P1 — ${distanceToStart.toFixed(2).replace('.',',')} m`;
        }
        return;
      }

      hit={...pts[0],projected:!!pts[0].projected,_ekoosSnap:true};
      usingProjection=!!pts[0].projected;
      sheet.classList.add('snap-ready');
      document.querySelector('#reticle')?.classList.add('snap-ready');

      try{updateMeasure();}catch(e){}
      try{updateMiniMap();}catch(e){}
      try{updateWorldOverlay(pose);}catch(e){}

      const info=document.querySelector('#arInfo');
      if(info)info.textContent='Punkt P1 złapany — zamknij obszar';
      const from=document.querySelector('#distanceFrom');
      if(from)from.textContent=`P${pts.length} → P1`;
      const mode=document.querySelector('#arMode');
      if(mode)mode.textContent='Magnetyczne domknięcie P1';
      drawSnap(pose);
    }

    const baseFrame=frame;
    frame=function(t,f){
      baseFrame(t,f);
      let pose=null;
      try{pose=f.getViewerPose(refSpace);}catch(e){}

      let candidate=null;
      try{
        if(hit&&!hit._ekoosSnap){
          candidate={...hit};
          lastCandidate={...candidate};
        }else if(lastCandidate){
          candidate={...lastCandidate};
        }
      }catch(e){}

      try{applySnap(candidate,pose);}catch(e){leaveSnap();}
    };

    closeButton.addEventListener('click',e=>{
      e.preventDefault();
      e.stopPropagation();
      if(!snapped||!Array.isArray(pts)||pts.length<3)return;
      navigator.vibrate?.(80);
      const finish=document.querySelector('#arFinish');
      if(finish){
        finish.disabled=false;
        finish.click();
      }
    });

    document.querySelector('#arUndo')?.addEventListener('click',()=>setTimeout(()=>{
      if(!Array.isArray(pts)||pts.length<3)leaveSnap();
    },0));
    document.querySelector('#startAr')?.addEventListener('click',()=>{
      snapped=false;
      lastCandidate=null;
      sheet.classList.remove('snap-ready');
      snapSvg.innerHTML='';
    });
  }

  install();
})();