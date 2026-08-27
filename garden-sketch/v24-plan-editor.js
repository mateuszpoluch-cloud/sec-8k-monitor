(() => {
  const history = [];
  let baseline = null, enabled = false, mode = 'vertex', selected = [], drag = null;
  let viewZoom = 1, pinching = false, pinchDistance = 0, pinchZoom = 1, viewPan = null;

  function points() { try { return Array.isArray(pts) ? pts : []; } catch { return []; } }
  const clonePoints = () => points().map(point => ({ ...point }));
  const planApi = () => window.ekoosPlanApi;
  const currentOffset = () => planApi()?.getOffset?.() || { x: 0, y: 0 };
  const snapshot = () => ({ points: clonePoints(), offset: { ...currentOffset() } });
  function restore(saved) {
    if (!saved) return;
    points().splice(0, points().length, ...saved.points.map(point => ({ ...point })));
    planApi()?.setOffset?.(saved.offset.x, saved.offset.y);
  }
  function notify(message) { try { toast(message); } catch { window.alert(message); } }
  function orientation(a, b, c) { return Math.sign((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)); }
  function segmentsCross(a,b,c,d) { return orientation(a,b,c)!==orientation(a,b,d)&&orientation(c,d,a)!==orientation(c,d,b); }
  function isSimplePolygon(poly) {
    if (poly.length < 3) return false;
    for (let i=0;i<poly.length;i++) {
      const a=poly[i],b=poly[(i+1)%poly.length];
      if (Math.hypot(b.x-a.x,b.y-a.y)<.03) return false;
      for (let j=i+1;j<poly.length;j++) {
        if (j===i||j===i+1||(i===0&&j===poly.length-1)) continue;
        const c=poly[j],d=poly[(j+1)%poly.length];
        if (segmentsCross(a,b,c,d)) return false;
      }
    }
    return true;
  }
  function angleAt(poly,index) {
    const p=poly[index],a=poly[(index-1+poly.length)%poly.length],b=poly[(index+1)%poly.length];
    const ax=a.x-p.x,ay=a.y-p.y,bx=b.x-p.x,by=b.y-p.y,den=Math.hypot(ax,ay)*Math.hypot(bx,by);
    return den?Math.acos(Math.max(-1,Math.min(1,(ax*bx+ay*by)/den)))*180/Math.PI:0;
  }
  function pointInfo(index) {
    const poly=points(),p=poly[index]; if(!p)return'Dotknij punktu, aby go zaznaczyć.';
    const a=poly[(index-1+poly.length)%poly.length],b=poly[(index+1)%poly.length];
    const left=Math.hypot(p.x-a.x,p.y-a.y),right=Math.hypot(b.x-p.x,b.y-p.y);
    return `P${index+1} • kąt ${angleAt(poly,index).toFixed(1).replace('.',',')}° • boki ${left.toFixed(2).replace('.',',')} m / ${right.toFixed(2).replace('.',',')} m`;
  }
  function svgPoint(svg,clientX,clientY) { const p=svg.createSVGPoint();p.x=clientX;p.y=clientY;return p.matrixTransform(svg.getScreenCTM().inverse()); }
  function inverseTransform(poly,vertices) {
    let first=-1,second=-1;
    for(let i=0;i<poly.length&&first<0;i++)for(let j=i+1;j<poly.length;j++)if(Math.hypot(poly[j].x-poly[i].x,poly[j].y-poly[i].y)>.001){first=i;second=j;break;}
    if(first<0||!vertices[first]||!vertices[second])return null;
    const dx=poly[second].x-poly[first].x,dy=poly[second].y-poly[first].y;
    const du=+vertices[second].getAttribute('cx')-+vertices[first].getAttribute('cx'),dv=+vertices[second].getAttribute('cy')-+vertices[first].getAttribute('cy');
    const den=dx*dx+dy*dy,A=(du*dx-dv*dy)/den,B=(du*dy+dv*dx)/den,s=A*A+B*B;
    return s>0?{A,B,s}:null;
  }
  function rerender(){const top=scrollY;if(typeof renderResult==='function')renderResult();requestAnimationFrame(()=>scrollTo(0,top));}
  function updateVertexPreview(du,dv){
    const x=drag.startVertex.x+du,y=drag.startVertex.y+dv;
    for(const el of[drag.vertex,drag.handle]){el.setAttribute('cx',x);el.setAttribute('cy',y);}
    if(drag.label){drag.label.setAttribute('x',x+2.3);drag.label.setAttribute('y',y-2.3);}
    drag.rendered[drag.index]={x,y};
    drag.path?.setAttribute('d',drag.rendered.map((p,i)=>`${i?'L':'M'}${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' ')+' Z');
  }
  function onPointerDown(event){
    if(!enabled||pinching||event.button>0)return;
    const svg=event.currentTarget,handle=event.target.closest('.plan-edit-handle');
    if(mode==='move'){
      if(!event.target.closest('.shape')&&!handle)return;
      event.preventDefault();svg.setPointerCapture(event.pointerId);
      drag={kind:'move',pointerId:event.pointerId,svg,start:svgPoint(svg,event.clientX,event.clientY),before:snapshot(),changed:false,moving:[...svg.querySelectorAll('.shape,.vertex,.point,.dim,.plan-edit-handle')]};return;
    }
    if(!handle)return;
    const vertices=[...svg.querySelectorAll('circle.vertex:not(.plan-edit-handle)')],poly=clonePoints(),transform=inverseTransform(poly,vertices),index=+handle.dataset.index;
    if(!transform||!poly[index]||!vertices[index])return;
    event.preventDefault();handle.setPointerCapture(event.pointerId);handle.classList.add('dragging');
    drag={kind:'vertex',pointerId:event.pointerId,svg,handle,vertex:vertices[index],label:[...svg.querySelectorAll('text.point')][index],path:svg.querySelector('path.shape'),rendered:vertices.map(v=>({x:+v.getAttribute('cx'),y:+v.getAttribute('cy')})),startVertex:{x:+vertices[index].getAttribute('cx'),y:+vertices[index].getAttribute('cy')},start:svgPoint(svg,event.clientX,event.clientY),transform,index,before:snapshot(),changed:false};setInfo(pointInfo(index));
  }
  function onPointerMove(event){
    if(pinching||!drag||event.pointerId!==drag.pointerId)return;event.preventDefault();
    const now=svgPoint(drag.svg,event.clientX,event.clientY),du=now.x-drag.start.x,dv=now.y-drag.start.y;drag.changed||=Math.hypot(du,dv)>.08;
    if(drag.kind==='move'){drag.moving.forEach(el=>el.setAttribute('transform',`translate(${du} ${dv})`));setInfo(`Przesunięcie na arkuszu: ${du.toFixed(1)} mm / ${dv.toFixed(1)} mm`);return;}
    const {A,B,s}=drag.transform,dx=(A*du+B*dv)/s,dy=(B*du-A*dv)/s,start=drag.before.points[drag.index];
    points()[drag.index]={...start,x:start.x+dx,y:start.y+dy};updateVertexPreview(du,dv);setInfo(pointInfo(drag.index));
  }
  function toggleSelection(index){const found=selected.indexOf(index);if(found>=0)selected.splice(found,1);else{if(selected.length===2)selected.shift();selected.push(index);}updateUi();decorateSelection();}
  function finishDrag(event){
    if(!drag||event.pointerId!==drag.pointerId)return;const done=drag;drag=null;if(done.kind==='vertex')done.handle.classList.remove('dragging');
    if(!done.changed){if(done.kind==='vertex')toggleSelection(done.index);return;}
    if(done.kind==='move'){
      const now=svgPoint(done.svg,event.clientX,event.clientY),du=now.x-done.start.x,dv=now.y-done.start.y;history.push(done.before);planApi()?.setOffset?.(done.before.offset.x+du,done.before.offset.y+dv);notify('Przesunięto obrys na arkuszu');
    }else if(!isSimplePolygon(points())){restore(done.before);notify('Nie można skrzyżować boków ani połączyć dwóch punktów.');}
    else{history.push(done.before);notify(`P${done.index+1} poprawiony`);}
    if(history.length>30)history.shift();rerender();updateUi();
  }
  function selectedForwardInterior(){if(selected.length!==2)return[];const out=[],n=points().length;let i=(selected[0]+1)%n;while(i!==selected[1]&&out.length<n){out.push(i);i=(i+1)%n;}return out;}
  function removeIndices(indices,message){
    const unique=[...new Set(indices)].sort((a,b)=>b-a);if(!unique.length)return notify('Nie ma punktów do usunięcia.');
    if(points().length-unique.length<3)return notify('Poligon musi mieć co najmniej 3 punkty.');
    const before=snapshot(),candidate=clonePoints();unique.forEach(index=>candidate.splice(index,1));if(!isSimplePolygon(candidate))return notify('Ta operacja utworzyłaby nieprawidłowy poligon.');
    history.push(before);restore({points:candidate,offset:before.offset});selected=[];rerender();updateUi();notify(message);
  }
  function deleteSelected(){if(selected.length!==1)return notify('Zaznacz jeden punkt do usunięcia.');removeIndices(selected,'Usunięto punkt i połączono sąsiednie boki.');}
  function connectSelected(){
    if(selected.length!==2)return notify('Zaznacz kolejno punkt początkowy i końcowy.');const between=selectedForwardInterior();
    if(!between.length)return notify('Wybrane punkty są już połączone jednym bokiem.');const a=selected[0]+1,b=selected[1]+1;removeIndices(between,`Połączono P${a} z P${b}.`);
  }
  function collinearCandidates(){
    const poly=points(),out=[];for(let i=0;i<poly.length;i++){
      const a=poly[(i-1+poly.length)%poly.length],p=poly[i],b=poly[(i+1)%poly.length],ab=Math.hypot(b.x-a.x,b.y-a.y),ap=Math.hypot(p.x-a.x,p.y-a.y),pb=Math.hypot(b.x-p.x,b.y-p.y);if(!ab)continue;
      const deviation=Math.abs((b.x-a.x)*(a.y-p.y)-(a.x-p.x)*(b.y-a.y))/ab;if(Math.abs(180-angleAt(poly,i))<=5&&deviation<=Math.max(.08,Math.min(ap,pb)*.03))out.push(i);
    }return out;
  }
  function simplify(){const candidates=collinearCandidates();if(!candidates.length)return notify('Nie znaleziono zbędnych punktów na prostych.');const removable=candidates.slice(0,Math.max(0,points().length-3));if(!confirm(`Usunąć ${removable.length} punkt(y) leżące prawie na prostych?`))return;removeIndices(removable,`Usunięto ${removable.length} zbędnych punktów.`);}
  function setInfo(text){const el=document.querySelector('#planEditInfo');if(el)el.textContent=text;}
  function clampZoom(value){return Math.max(.7,Math.min(4,Number(value)||1));}
  function applyViewZoom(value){
    viewZoom=clampZoom(value);const svg=document.querySelector('#preview>svg');
    if(svg){svg.style.width=`${viewZoom*100}%`;svg.style.maxWidth='none';svg.style.height='auto';}
    const label=document.querySelector('#planZoomValue');if(label)label.textContent=`${Math.round(viewZoom*100)}%`;
  }
  function enterFullscreen(){
    document.body.classList.add('plan-editor-fullscreen');enabled=true;
    const toggle=document.querySelector('#planEditToggle');if(toggle){toggle.classList.add('active');toggle.textContent='Zakończ edycję';}
    document.querySelector('#preview>svg')?.classList.add('plan-editing');
    document.documentElement.requestFullscreen?.().catch(()=>{});applyViewZoom(Math.max(1,viewZoom));updateUi();
  }
  function leaveFullscreen(){
    document.body.classList.remove('plan-editor-fullscreen');if(document.fullscreenElement)document.exitFullscreen?.().catch(()=>{});applyViewZoom(1);
  }
  function touchDistance(touches){const a=touches[0],b=touches[1];return Math.hypot(b.clientX-a.clientX,b.clientY-a.clientY);}
  function installPinch(preview){
    preview.addEventListener('touchstart',event=>{
      if(!document.body.classList.contains('plan-editor-fullscreen'))return;
      if(event.touches.length!==2||drag?.changed)return;
      viewPan=null;if(drag?.handle)drag.handle.classList.remove('dragging');drag=null;pinching=true;pinchDistance=touchDistance(event.touches);pinchZoom=viewZoom;event.preventDefault();
    },{passive:false});
    preview.addEventListener('touchmove',event=>{
      if(pinching&&event.touches.length===2){event.preventDefault();applyViewZoom(pinchZoom*touchDistance(event.touches)/Math.max(1,pinchDistance));return;}
    },{passive:false});
    preview.addEventListener('touchend',event=>{if(pinching&&event.touches.length<2)pinching=false;},{passive:true});
    preview.addEventListener('touchcancel',()=>{pinching=false;viewPan=null;},{passive:true});
    preview.addEventListener('wheel',event=>{
      if(!document.body.classList.contains('plan-editor-fullscreen')||!event.ctrlKey)return;event.preventDefault();applyViewZoom(viewZoom*(event.deltaY>0?.9:1.1));
    },{passive:false});
  }
  function installPointerPan(preview){
    preview.addEventListener('pointerdown',event=>{
      if(!document.body.classList.contains('plan-editor-fullscreen')||pinching||event.button>0)return;
      const editingHandle=event.target.closest?.('.plan-edit-handle');
      const movingShape=mode==='move'&&event.target.closest?.('.shape');
      if(editingHandle||movingShape)return;
      event.preventDefault();preview.setPointerCapture?.(event.pointerId);
      viewPan={pointerId:event.pointerId,x:event.clientX,y:event.clientY,left:preview.scrollLeft,top:preview.scrollTop};
    });
    preview.addEventListener('pointermove',event=>{
      if(!viewPan||pinching||event.pointerId!==viewPan.pointerId)return;
      event.preventDefault();preview.scrollLeft=viewPan.left-(event.clientX-viewPan.x);preview.scrollTop=viewPan.top-(event.clientY-viewPan.y);
    });
    const finish=event=>{if(viewPan&&event.pointerId===viewPan.pointerId)viewPan=null;};
    preview.addEventListener('pointerup',finish);preview.addEventListener('pointercancel',finish);
  }
  function decorateSelection(){document.querySelectorAll('.plan-edit-handle').forEach(h=>h.classList.toggle('selected',selected.includes(+h.dataset.index)));}
  function updateUi(){
    const byId=id=>document.querySelector(id);if(byId('#planEditUndo'))byId('#planEditUndo').disabled=!history.length;if(byId('#planEditReset'))byId('#planEditReset').disabled=!baseline;
    if(byId('#planDeletePoint'))byId('#planDeletePoint').disabled=selected.length!==1;if(byId('#planConnectPoints'))byId('#planConnectPoints').disabled=selected.length!==2;byId('#planMoveMode')?.classList.toggle('active',mode==='move');
    if(!drag)setInfo(selected.length===1?pointInfo(selected[0]):selected.length===2?`Połącz P${selected[0]+1} → P${selected[1]+1}: usunie ${selectedForwardInterior().length} punkt(y) pomiędzy.`:mode==='move'?'Przeciągnij obrys, aby ustawić go na arkuszu.':'Dotknij punktu, aby go zaznaczyć, albo przeciągnij go.');
  }
  function decoratePreview(){
    const preview=document.querySelector('#preview'),svg=preview?.querySelector('svg');if(!svg||svg.dataset.planEditorV24==='1')return;if(!baseline&&points().length>=3)baseline=snapshot();
    svg.dataset.planEditorV24='1';svg.classList.toggle('plan-editing',enabled);svg.classList.toggle('move-mode',mode==='move');
    [...svg.querySelectorAll('circle.vertex')].forEach((vertex,index)=>{const handle=document.createElementNS('http://www.w3.org/2000/svg','circle');handle.setAttribute('cx',vertex.getAttribute('cx'));handle.setAttribute('cy',vertex.getAttribute('cy'));handle.setAttribute('r','4.8');handle.setAttribute('class','plan-edit-handle');handle.dataset.index=index;svg.appendChild(handle);});
    svg.addEventListener('pointerdown',onPointerDown);svg.addEventListener('pointermove',onPointerMove);svg.addEventListener('pointerup',finishDrag);svg.addEventListener('pointercancel',finishDrag);decorateSelection();updateUi();
  }
  function install(){
    const preview=document.querySelector('#preview');if(!preview)return setTimeout(install,80);if(document.querySelector('#planEditTools'))return;
    const tools=document.createElement('div');tools.id='planEditTools';tools.innerHTML=`<div class="plan-edit-head"><strong>Testowy edytor v24</strong><span id="planEditInfo">Włącz edycję, aby poprawić obrys.</span></div><div class="plan-edit-actions"><button id="planFullscreen" class="btn primary" type="button">⛶ Pełny ekran</button><button id="planFullscreenClose" class="btn primary" type="button">✕ Zamknij</button><button id="planEditToggle" class="btn secondary" type="button">Włącz edycję</button><button id="planMoveMode" class="btn ghost" type="button">Przesuń obrys</button><button id="planDeletePoint" class="btn ghost" type="button" disabled>Usuń punkt</button><button id="planConnectPoints" class="btn ghost" type="button" disabled>Połącz skrajne</button><button id="planSimplify" class="btn ghost" type="button">Uprość proste</button><button id="planEditUndo" class="btn ghost" type="button" disabled>↶ Cofnij</button><button id="planEditReset" class="btn ghost" type="button" disabled>Przywróć pomiar</button><div class="plan-zoom"><button id="planZoomOut" type="button" aria-label="Pomniejsz">−</button><strong id="planZoomValue">100%</strong><button id="planZoomIn" type="button" aria-label="Powiększ">＋</button><button id="planZoomReset" type="button">Dopasuj</button></div></div>`;preview.before(tools);
    const style=document.createElement('style');style.textContent=`#planEditTools{margin:12px 0 9px;padding:13px;border:1px solid var(--line);border-radius:15px;background:#f5faf7}.plan-edit-head{margin-bottom:10px}.plan-edit-head strong,.plan-edit-head span{display:block}.plan-edit-head span{margin-top:3px;color:var(--mut);font-size:.78rem}.plan-edit-actions{display:flex;gap:7px;flex-wrap:wrap}.plan-edit-actions .btn{min-height:39px;padding:8px 11px}#planFullscreenClose,.plan-zoom{display:none}#planEditToggle.active,#planMoveMode.active{background:#173f35;color:#fff;border-color:#173f35}.plan-zoom{align-items:center;gap:5px;margin-left:auto}.plan-zoom button{min-height:39px;padding:7px 12px;border:1px solid #b9d2c9;border-radius:10px;background:#fff;color:#173f35;font-weight:900}.plan-zoom strong{min-width:52px;text-align:center}#preview svg .plan-edit-handle{display:none;fill:#dfff73;fill-opacity:.92;stroke:#173f35;stroke-width:.8;vector-effect:non-scaling-stroke;cursor:grab;pointer-events:all}#preview svg.plan-editing{touch-action:none;user-select:none}#preview svg.plan-editing .plan-edit-handle{display:block}#preview svg.plan-editing .plan-edit-handle.selected{fill:#fff;stroke:#e08b20;stroke-width:1.5}#preview svg.plan-editing .plan-edit-handle.dragging{fill:#fff;stroke:#e08b20;stroke-width:1.5;cursor:grabbing}#preview svg.move-mode .shape{cursor:move;pointer-events:all}body.plan-editor-fullscreen{overflow:hidden}body.plan-editor-fullscreen #planEditTools{position:fixed;z-index:5002;inset:0 0 auto;margin:0;border:0;border-radius:0;padding:max(8px,env(safe-area-inset-top)) 9px 8px;background:#eef7f3;box-shadow:0 3px 14px #0003}body.plan-editor-fullscreen .plan-edit-head{margin:0 0 6px}body.plan-editor-fullscreen .plan-edit-head strong{font-size:.86rem}body.plan-editor-fullscreen #planFullscreen,body.plan-editor-fullscreen #planEditToggle{display:none}body.plan-editor-fullscreen #planFullscreenClose,body.plan-editor-fullscreen .plan-zoom{display:flex}body.plan-editor-fullscreen #preview{position:fixed;z-index:5001;inset:112px 0 0;height:auto!important;min-height:0!important;aspect-ratio:auto!important;margin:0!important;padding:18px!important;border:0!important;border-radius:0!important;overflow:auto;background:#2e3a36!important;display:block;touch-action:none!important;overscroll-behavior:contain}body.plan-editor-fullscreen #preview>svg{display:block;margin:auto;max-width:none!important;filter:drop-shadow(0 8px 20px #0008);touch-action:none!important}body.plan-editor-fullscreen #preview .plan-edit-handle,body.plan-editor-fullscreen #preview .shape{touch-action:none}@media(max-width:700px){.plan-edit-actions{display:grid;grid-template-columns:1fr 1fr}.plan-edit-actions .btn{width:100%}body.plan-editor-fullscreen #planEditTools{max-height:126px;overflow:auto}body.plan-editor-fullscreen #preview{inset:126px 0 0}.plan-zoom{margin:0;grid-column:1/-1;justify-content:center}}`;document.head.appendChild(style);
    document.querySelector('#planEditToggle').onclick=e=>{enabled=!enabled;e.currentTarget.classList.toggle('active',enabled);e.currentTarget.textContent=enabled?'Zakończ edycję':'Włącz edycję';preview.querySelector('svg')?.classList.toggle('plan-editing',enabled);updateUi();};
    document.querySelector('#planFullscreen').onclick=enterFullscreen;document.querySelector('#planFullscreenClose').onclick=leaveFullscreen;
    document.querySelector('#planZoomIn').onclick=()=>applyViewZoom(viewZoom*1.2);document.querySelector('#planZoomOut').onclick=()=>applyViewZoom(viewZoom/1.2);document.querySelector('#planZoomReset').onclick=()=>applyViewZoom(1);
    document.querySelector('#planMoveMode').onclick=()=>{mode=mode==='move'?'vertex':'move';selected=[];preview.querySelector('svg')?.classList.toggle('move-mode',mode==='move');updateUi();decorateSelection();};
    document.querySelector('#planDeletePoint').onclick=deleteSelected;document.querySelector('#planConnectPoints').onclick=connectSelected;document.querySelector('#planSimplify').onclick=simplify;
    document.querySelector('#planEditUndo').onclick=()=>{const previous=history.pop();if(!previous)return;restore(previous);selected=[];rerender();updateUi();notify('Cofnięto ostatnią zmianę.');};
    document.querySelector('#planEditReset').onclick=()=>{if(!baseline||!confirm('Przywrócić kształt bez wszystkich korekt wykonanych na arkuszu?'))return;restore(baseline);history.length=0;selected=[];rerender();updateUi();notify('Przywrócono wynik pomiaru.');};
    document.querySelector('#newOne')?.addEventListener('click',()=>{baseline=null;history.length=0;selected=[];leaveFullscreen();});document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement)document.body.classList.remove('plan-editor-fullscreen');});installPinch(preview);installPointerPan(preview);new MutationObserver(()=>{decoratePreview();applyViewZoom(viewZoom);}).observe(preview,{childList:true});decoratePreview();
  }
  install();
})();
