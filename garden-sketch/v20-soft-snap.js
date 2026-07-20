(()=>{
  const HINT_RADIUS=0.80;
  const READY_RADIUS=0.25;
  const RELEASE_RADIUS=0.38;
  let ready=false;

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
    closeButton.innerHTML='<span>◎ Zamknij obszar</span><small>P1 jest blisko — domknięcie nastąpi po kliknięciu</small>';
    actions.before(closeButton);

    const snapSvg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    snapSvg.id='ekoosSoftSnapSvg';
    snapSvg.setAttribute('aria-hidden','true');
    snapSvg.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:4;pointer-events:none;overflow:visible';
    ar.appendChild(snapSvg);

    const style=document.createElement('style');
    style.textContent=`
      #closeAreaButton{display:none;width:100%;min-height:66px;border:0;border-radius:18px;padding:10px 16px;background:linear-gradient(135deg,#c8ef72,#55c68a);color:#153d35;font-weight:950;box-shadow:0 10px 28px #0005;margin:5px 0 2px}
      #closeAreaButton span{display:block;font-size:1.15rem;line-height:1.15}
      #closeAreaButton small{display:block;margin-top:3px;font-size:.67rem;font-weight:800;opacity:.78}
      .ar-sheet.soft-snap-ready #closeAreaButton{display:block}
      .ar-sheet.soft-snap-ready .ar-actions{display:none}
      .ar-sheet.soft-snap-ready #pointStrip{display:none!important}
      .ar-sheet.soft-snap-ready .ar-info{color:#dfff9a}
      #reticle.soft-snap-ready{border-color:#dfff73!important;box-shadow:0 0 0 9px #c9f36b24,0 0 20px #c9f36b66!important}
      #reticle.soft-snap-ready:before,#reticle.soft-snap-ready:after{background:#dfff73!important}
      #ekoosSoftSnapSvg .soft-ring{fill:#c9f36b18;stroke:#dfff73;stroke-width:4;filter:drop-shadow(0 2px 4px #153d35)}
      #ekoosSoftSnapSvg .soft-core{fill:#dfff73;stroke:#fff;stroke-width:3}
      #ekoosSoftSnapSvg .soft-link{stroke:#dfff73;stroke-width:3;stroke-dasharray:7 8;stroke-linecap:round;opacity:.8}
      #ekoosSoftSnapSvg .soft-label{font-size:16px;font-weight:950;fill:#dfff73;stroke:#153d35;stroke-width:5;paint-order:stroke;stroke-linejoin:round}
    `;
    document.head.appendChild(style);

    function reticleCenter(){
      const r=document.querySelector('#reticle')?.getBoundingClientRect();
      return r?{x:r.left+r.width/2,y:r.top+r.height/2}:{x:innerWidth/2,y:innerHeight*.5};
    }

    function clearReady(){
      ready=false;
      sheet.classList.remove('soft-snap-ready');
      document.querySelector('#reticle')?.classList.remove('soft-snap-ready');
      snapSvg.innerHTML='';
    }

    function drawReady(pose){
      if(!ready||!pose?.views?.length||!Array.isArray(pts)||!pts[0]){
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
        <line class="soft-link" x1="${ret.x}" y1="${ret.y}" x2="${p.x}" y2="${p.y}"/>
        <circle class="soft-ring" cx="${p.x}" cy="${p.y}" r="22"/>
        <circle class="soft-core" cx="${p.x}" cy="${p.y}" r="8"/>
        <text class="soft-label" x="${p.x}" y="${p.y-30}" text-anchor="middle">P1 • GOTOWE</text>
      `;
    }

    function updateSoftSnap(candidate,pose){
      const enough=Array.isArray(pts)&&pts.length>=3&&pts[0]&&candidate;
      if(!enough){clearReady();return;}

      const d=dist(candidate,pts[0]);
      if(!ready&&d<=READY_RADIUS){
        ready=true;
        navigator.vibrate?.([25,30,45]);
      }else if(ready&&d>RELEASE_RADIUS){
        clearReady();
      }

      const info=document.querySelector('#arInfo');
      if(ready){
        sheet.classList.add('soft-snap-ready');
        document.querySelector('#reticle')?.classList.add('soft-snap-ready');
        if(info)info.textContent='P1 jest blisko — kliknij „Zamknij obszar”';
        const mode=document.querySelector('#arMode');
        if(mode)mode.textContent='Miękkie domknięcie P1';
        drawReady(pose);
      }else{
        snapSvg.innerHTML='';
        if(d<=HINT_RADIUS&&info)info.textContent=`Zbliżasz się do P1 — ${d.toFixed(2).replace('.',',')} m`;
      }
    }

    const baseFrame=frame;
    frame=function(t,f){
      baseFrame(t,f);
      let pose=null,candidate=null;
      try{pose=f.getViewerPose(refSpace);}catch(e){}
      try{if(hit)candidate={...hit};}catch(e){}
      try{updateSoftSnap(candidate,pose);}catch(e){clearReady();}
    };

    closeButton.addEventListener('click',e=>{
      e.preventDefault();
      e.stopPropagation();
      if(!ready||!Array.isArray(pts)||pts.length<3)return;
      navigator.vibrate?.(70);
      const finish=document.querySelector('#arFinish');
      if(finish){
        finish.disabled=false;
        finish.click();
      }
    });

    document.querySelector('#arUndo')?.addEventListener('click',()=>setTimeout(()=>{
      if(!Array.isArray(pts)||pts.length<3)clearReady();
    },0));
    document.querySelector('#startAr')?.addEventListener('click',clearReady);
  }

  install();
})();