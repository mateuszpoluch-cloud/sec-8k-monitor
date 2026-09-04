(()=>{
  let outer=null,obstacles=[],phase='outer',choice=null,cancelButton=null,baseFinish=null;
  const clone=points=>(points||[]).map(point=>({...point}));
  function inside(point,polygon){let result=false;for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){const a=polygon[i],b=polygon[j],crosses=(a.y>point.y)!==(b.y>point.y)&&point.x<(b.x-a.x)*(point.y-a.y)/(b.y-a.y)+a.x;if(crosses)result=!result;}return result;}
  function refreshAr(){try{renderPointStrip();updateMiniMap();updateArMode();}catch(error){}const count=document.querySelector('#count');if(count)count.textContent=pts.length;}
  function hideChoice(){choice?.classList.remove('show');document.querySelector('.ar-sheet')?.classList.remove('area-choice-open');}
  function showChoice(message){
    choice.querySelector('strong').textContent=message;choice.querySelector('small').textContent=obstacles.length?`Zapisane przeszkody: ${obstacles.length}`:'Możesz teraz zaznaczyć wyłączenie wewnątrz ogrodu.';
    choice.classList.add('show');document.querySelector('.ar-sheet')?.classList.add('area-choice-open');
  }
  function beginObstacle(){hideChoice();phase='obstacle';pts.splice(0,pts.length);editIndex=-1;obstacleMode=false;cancelButton.classList.add('show');refreshAr();try{toast('Dodaj punkty przeszkody i zamknij jej obrys.');}catch(error){}}
  function normalizeAreas(){
    const origin=outer[0],shift=poly=>poly.map(point=>({...point,x:point.x-origin.x,y:point.y-origin.y}));
    outer=shift(outer);obstacles=obstacles.map(shift);window.ekoosGardenAreas={outer:clone(outer),obstacles:obstacles.map(clone)};pts.splice(0,pts.length,...clone(outer));
  }
  async function finishAll(){
    hideChoice();cancelButton.classList.remove('show');normalizeAreas();await xrSession?.end?.();renderResult();
    const net=Math.max(0,area(outer)-obstacles.reduce((sum,poly)=>sum+area(poly),0)),metric=document.querySelector('#metrics .metric strong');if(metric)metric.textContent=`${net.toFixed(1)} m²`;
    let note=document.querySelector('#areaSummary');if(!note){note=document.createElement('div');note.id='areaSummary';note.className='notice';document.querySelector('#metrics')?.after(note);}note.textContent=`Powierzchnia użytkowa po odjęciu ${obstacles.length} przeszkód: ${net.toFixed(1).replace('.',',')} m²`;
    window.ekoosPlanApi?.updatePreview?.();
  }
  function cancelObstacle(){pts.splice(0,pts.length);phase='outerDone';cancelButton.classList.remove('show');refreshAr();showChoice('Przeszkoda anulowana');}
  function reset(){outer=null;obstacles=[];phase='outer';window.ekoosGardenAreas=null;hideChoice();cancelButton?.classList.remove('show');}
  function install(){
    const finish=document.querySelector('#arFinish'),actions=document.querySelector('.ar-actions');if(!finish||!actions||typeof renderResult!=='function')return setTimeout(install,80);if(document.querySelector('#areaFinishChoice'))return;
    choice=document.createElement('div');choice.id='areaFinishChoice';choice.innerHTML='<strong>Obrys główny gotowy</strong><small></small><div><button id="addInnerArea" type="button">＋ Dodaj przeszkodę</button><button id="finishAllAreas" type="button">✓ Zakończ pomiar</button></div>';actions.before(choice);
    cancelButton=document.createElement('button');cancelButton.id='cancelInnerArea';cancelButton.type='button';cancelButton.textContent='Anuluj rysowanie przeszkody';actions.before(cancelButton);
    const style=document.createElement('style');style.textContent=`#areaFinishChoice,#cancelInnerArea{display:none}#areaFinishChoice.show{display:block;padding:12px;border-radius:17px;background:#123b32;border:1px solid #dfff7366;text-align:center}#areaFinishChoice strong,#areaFinishChoice small{display:block}#areaFinishChoice small{margin:4px 0 10px;color:#c7ddd4;font-size:.7rem}#areaFinishChoice div{display:grid;grid-template-columns:1fr 1fr;gap:8px}#areaFinishChoice button,#cancelInnerArea{min-height:49px;border:0;border-radius:13px;padding:8px;background:#dfff73;color:#173f35;font-weight:950}#finishAllAreas{background:#42c08a!important}.ar-sheet.area-choice-open .ar-actions,.ar-sheet.area-choice-open #pointStrip,.ar-sheet.area-choice-open #firstEdgeGuide,.ar-sheet.area-choice-open #closeAreaButton{display:none!important}#cancelInnerArea.show{display:block;width:100%;margin:0 0 7px;background:#ffffff1c;color:#fff;border:1px solid #ffffff30}`;document.head.appendChild(style);
    choice.querySelector('#addInnerArea').onclick=beginObstacle;choice.querySelector('#finishAllAreas').onclick=finishAll;cancelButton.onclick=cancelObstacle;
    baseFinish=finish.onclick;finish.onclick=event=>{event?.stopPropagation?.();if(!Array.isArray(pts)||pts.length<3)return;if(phase==='outer'){outer=clone(pts);phase='outerDone';showChoice('Obrys główny gotowy');}else if(phase==='obstacle'){if(!pts.every(point=>inside(point,outer)))return alert('Przeszkoda musi znajdować się w całości wewnątrz obrysu głównego.');obstacles.push(clone(pts));phase='outerDone';cancelButton.classList.remove('show');showChoice('Przeszkoda zapisana');}};
    const baseFrame=frame;frame=function(t,f){baseFrame(t,f);if(phase==='obstacle'){const mode=document.querySelector('#arMode');if(mode)mode.textContent='Rysowanie przeszkody';const info=document.querySelector('#arInfo');if(info&&!document.querySelector('.ar-sheet')?.classList.contains('soft-snap-ready'))info.textContent='Obrysuj przeszkodę i wróć do jej P1';}};
    document.querySelector('#startAr')?.addEventListener('click',reset);document.querySelector('#newOne')?.addEventListener('click',reset);
  }
  window.ekoosAreasApi={get:()=>({outer:clone(outer),obstacles:obstacles.map(clone)})};install();
})();
