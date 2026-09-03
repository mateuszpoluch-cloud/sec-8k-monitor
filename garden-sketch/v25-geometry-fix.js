(()=>{
  const ANGLE_TOLERANCE=7;
  let previous=null;
  function copy(){try{return Array.isArray(pts)?pts.map(p=>({...p})):[];}catch(error){return[];}}
  function angleDelta(a,b){let d=Math.abs(a-b)%Math.PI;return Math.min(d,Math.PI-d);}
  function orientation(a,b,c){return Math.sign((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x));}
  function simple(poly){for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length];for(let j=i+1;j<poly.length;j++){if(j===i||j===i+1||(i===0&&j===poly.length-1))continue;const c=poly[j],d=poly[(j+1)%poly.length];if(orientation(a,b,c)!==orientation(a,b,d)&&orientation(c,d,a)!==orientation(c,d,b))return false;}}return true;}
  function candidate(poly){
    if(poly.length<3)return null;const ref=Math.atan2(poly[1].y-poly[0].y,poly[1].x-poly[0].x),out=[{...poly[0]}];let corrected=0,maxMove=0;
    for(let i=1;i<poly.length;i++){
      const sourceA=poly[i-1],sourceB=poly[i],dx=sourceB.x-sourceA.x,dy=sourceB.y-sourceA.y,length=Math.hypot(dx,dy),angle=Math.atan2(dy,dx);
      const quarter=Math.round((angle-ref)/(Math.PI/2)),target=ref+quarter*Math.PI/2,shouldSnap=angleDelta(angle,target)<=ANGLE_TOLERANCE*Math.PI/180;
      const a=out[i-1],next=shouldSnap?{...sourceB,x:a.x+Math.cos(target)*length,y:a.y+Math.sin(target)*length}:{...sourceB,x:a.x+dx,y:a.y+dy};
      if(shouldSnap&&i>1)corrected++;maxMove=Math.max(maxMove,Math.hypot(next.x-sourceB.x,next.y-sourceB.y));out.push(next);
    }
    return{points:out,corrected,maxMove};
  }
  function apply(){
    const before=copy(),fix=candidate(before);if(!fix||!fix.corrected)return alert('Nie znaleziono boków zbliżonych do kierunku P1→P2 ani do kąta 90° względem niego.');
    if(!simple(fix.points))return alert('Prostowanie spowodowałoby skrzyżowanie boków. Geometria nie została zmieniona.');
    if(!confirm(`Wyprostować ${fix.corrected} bok(i) względem P1→P2?\nNajwiększe przesunięcie punktu: ${fix.maxMove.toFixed(2).replace('.',',')} m`))return;
    previous=before;pts.splice(0,pts.length,...fix.points);renderResult();document.querySelector('#undoGeometryFix').disabled=false;try{toast('Geometria została poprawiona względem P1→P2.');}catch(error){}
  }
  function install(){
    const actions=document.querySelector('.plan-edit-actions');if(!actions)return setTimeout(install,100);if(document.querySelector('#fixGeometry'))return;
    const button=document.createElement('button');button.id='fixGeometry';button.className='btn ghost';button.type='button';button.textContent='⌗ Popraw geometrię';button.onclick=apply;
    const undo=document.createElement('button');undo.id='undoGeometryFix';undo.className='btn ghost';undo.type='button';undo.textContent='Cofnij prostowanie';undo.disabled=true;undo.onclick=()=>{if(!previous)return;pts.splice(0,pts.length,...previous);previous=null;undo.disabled=true;renderResult();};
    actions.append(button,undo);const title=document.querySelector('.plan-edit-head strong');if(title)title.textContent='Testowy edytor v25';document.querySelector('#newOne')?.addEventListener('click',()=>{previous=null;undo.disabled=true;});
  }
  window.ekoosGeometryFixApi={candidate};
  install();
})();
