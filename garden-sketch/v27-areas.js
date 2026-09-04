(()=>{
  let lawns=[],phase='lawn',activeLawn=-1,choice=null,cancelButton=null;
  const clone=points=>(points||[]).map(point=>({...point}));
  const cloneLawns=()=>lawns.map(lawn=>({polygon:clone(lawn.polygon),obstacles:lawn.obstacles.map(clone)}));
  function inside(point,polygon){let result=false;for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){const a=polygon[i],b=polygon[j],crosses=(a.y>point.y)!==(b.y>point.y)&&point.x<(b.x-a.x)*(point.y-a.y)/(b.y-a.y)+a.x;if(crosses)result=!result;}return result;}
  function refreshAr(){try{renderPointStrip();updateMiniMap();updateArMode();}catch(error){}const count=document.querySelector('#count');if(count)count.textContent=pts.length;}
  function hideChoice(){choice?.classList.remove('show');document.querySelector('.ar-sheet')?.classList.remove('area-choice-open');}
  function savedObstacles(){return lawns.reduce((sum,lawn)=>sum+lawn.obstacles.length,0);}
  function showChoice(message){
    choice.querySelector('strong').textContent=message;
    choice.querySelector('small').textContent=`Zapisane trawniki: ${lawns.length} • przeszkody: ${savedObstacles()}`;
    choice.classList.add('show');document.querySelector('.ar-sheet')?.classList.add('area-choice-open');
    choice.querySelector('#addInnerArea').disabled=activeLawn<0;
  }
  function clearDrawing(){pts.splice(0,pts.length);editIndex=-1;obstacleMode=false;window.ekoosFirstEdgeGuide?.reset?.();refreshAr();}
  function beginLawn(){hideChoice();phase='lawn';activeLawn=-1;clearDrawing();cancelButton.textContent='Anuluj rysowanie trawnika';cancelButton.classList.add('show');try{toast(`Obrysuj trawnik ${lawns.length+1} i zamknij jego obrys.`);}catch(error){}}
  function beginObstacle(){if(activeLawn<0)return;hideChoice();phase='obstacle';clearDrawing();cancelButton.textContent='Anuluj rysowanie przeszkody';cancelButton.classList.add('show');try{toast(`Obrysuj przeszkodę w trawniku ${activeLawn+1}.`);}catch(error){}}
  function normalizeAreas(){
    const origin=lawns[0].polygon[0],shift=poly=>poly.map(point=>({...point,x:point.x-origin.x,y:point.y-origin.y}));
    lawns=lawns.map(lawn=>({polygon:shift(lawn.polygon),obstacles:lawn.obstacles.map(shift)}));
    const first=lawns[0];window.ekoosGardenAreas={outer:clone(first.polygon),obstacles:first.obstacles.map(clone),lawns:cloneLawns()};
    pts.splice(0,pts.length,...clone(first.polygon));
  }
  function lawnNet(lawn){return Math.max(0,area(lawn.polygon)-lawn.obstacles.reduce((sum,poly)=>sum+area(poly),0));}
  async function finishAll(){
    if(!lawns.length)return;hideChoice();cancelButton.classList.remove('show');normalizeAreas();await xrSession?.end?.();renderResult();
    const total=lawns.reduce((sum,lawn)=>sum+lawnNet(lawn),0),totalPerimeter=lawns.reduce((sum,lawn)=>sum+perimeter(lawn.polygon),0),totalPoints=lawns.reduce((sum,lawn)=>sum+lawn.polygon.length,0),metrics=document.querySelectorAll('#metrics .metric strong');if(metrics[0])metrics[0].textContent=`${total.toFixed(1)} m²`;if(metrics[1])metrics[1].textContent=`${totalPerimeter.toFixed(1)} m`;if(metrics[2])metrics[2].textContent=totalPoints;
    let note=document.querySelector('#areaSummary');if(!note){note=document.createElement('div');note.id='areaSummary';note.className='notice';document.querySelector('#metrics')?.after(note);}
    const details=lawns.map((lawn,index)=>`Trawnik ${index+1}: ${lawnNet(lawn).toFixed(1).replace('.',',')} m²`).join(' • ');
    note.textContent=`${details} • Razem: ${total.toFixed(1).replace('.',',')} m²`;
    window.ekoosPlanApi?.updatePreview?.();
  }
  function cancelCurrent(){clearDrawing();phase='done';cancelButton.classList.remove('show');showChoice('Rysowanie anulowane');}
  function reset(){lawns=[];phase='lawn';activeLawn=-1;window.ekoosGardenAreas=null;hideChoice();cancelButton?.classList.remove('show');}
  function install(){
    const finish=document.querySelector('#arFinish'),actions=document.querySelector('.ar-actions');if(!finish||!actions||typeof renderResult!=='function')return setTimeout(install,80);if(document.querySelector('#areaFinishChoice'))return;
    choice=document.createElement('div');choice.id='areaFinishChoice';choice.innerHTML='<strong>Obszar gotowy</strong><small></small><div><button id="addLawn" type="button">＋ Dodaj trawnik</button><button id="addInnerArea" type="button">＋ Dodaj przeszkodę</button><button id="finishAllAreas" type="button">✓ Zakończ pomiar</button></div>';actions.before(choice);
    cancelButton=document.createElement('button');cancelButton.id='cancelInnerArea';cancelButton.type='button';actions.before(cancelButton);
    const style=document.createElement('style');style.textContent=`#areaFinishChoice,#cancelInnerArea{display:none}#areaFinishChoice.show{display:block;padding:12px;border-radius:17px;background:#123b32;border:1px solid #dfff7366;text-align:center}#areaFinishChoice strong,#areaFinishChoice small{display:block}#areaFinishChoice small{margin:4px 0 10px;color:#c7ddd4;font-size:.7rem}#areaFinishChoice div{display:grid;grid-template-columns:1fr 1fr;gap:8px}#areaFinishChoice button,#cancelInnerArea{min-height:49px;border:0;border-radius:13px;padding:8px;background:#dfff73;color:#173f35;font-weight:950}#areaFinishChoice button:disabled{opacity:.4}#finishAllAreas{grid-column:1/-1;background:#42c08a!important}.ar-sheet.area-choice-open .ar-actions,.ar-sheet.area-choice-open #pointStrip,.ar-sheet.area-choice-open #firstEdgeGuide,.ar-sheet.area-choice-open #closeAreaButton{display:none!important}#cancelInnerArea.show{display:block;width:100%;margin:0 0 7px;background:#ffffff1c;color:#fff;border:1px solid #ffffff30}`;document.head.appendChild(style);
    choice.querySelector('#addLawn').onclick=beginLawn;choice.querySelector('#addInnerArea').onclick=beginObstacle;choice.querySelector('#finishAllAreas').onclick=finishAll;cancelButton.onclick=cancelCurrent;
    finish.onclick=event=>{event?.stopPropagation?.();if(!Array.isArray(pts)||pts.length<3)return;
      if(phase==='lawn'){lawns.push({polygon:clone(pts),obstacles:[]});activeLawn=lawns.length-1;phase='done';cancelButton.classList.remove('show');showChoice(`Trawnik ${lawns.length} zapisany`);}
      else if(phase==='obstacle'){const lawn=lawns[activeLawn];if(!pts.every(point=>inside(point,lawn.polygon)))return alert(`Przeszkoda musi znajdować się w całości wewnątrz trawnika ${activeLawn+1}.`);lawn.obstacles.push(clone(pts));phase='done';cancelButton.classList.remove('show');showChoice(`Przeszkoda trawnika ${activeLawn+1} zapisana`);}
    };
    const baseFrame=frame;frame=function(t,f){baseFrame(t,f);if(phase==='obstacle'||phase==='lawn'&&lawns.length){const mode=document.querySelector('#arMode');if(mode)mode.textContent=phase==='obstacle'?`Przeszkoda • trawnik ${activeLawn+1}`:`Rysowanie trawnika ${lawns.length+1}`;const info=document.querySelector('#arInfo');if(info&&!document.querySelector('.ar-sheet')?.classList.contains('soft-snap-ready'))info.textContent=phase==='obstacle'?'Obrysuj przeszkodę i wróć do jej P1':'Obrysuj kolejny trawnik w tej samej sesji';}};
    document.querySelector('#startAr')?.addEventListener('click',reset);document.querySelector('#newOne')?.addEventListener('click',reset);
  }
  window.ekoosAreasApi={get:()=>({lawns:cloneLawns(),outer:clone(lawns[0]?.polygon),obstacles:(lawns[0]?.obstacles||[]).map(clone)})};install();
})();
