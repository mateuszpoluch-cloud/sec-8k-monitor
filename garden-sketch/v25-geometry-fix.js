(()=>{
  const ANGLE_TOLERANCE=7;
  let previous=null;
  function copy(){try{return Array.isArray(pts)?pts.map(p=>({...p})):[];}catch(error){return[];}}
  function angleDelta(a,b){let d=Math.abs(a-b)%Math.PI;return Math.min(d,Math.PI-d);}
  function orientation(a,b,c){return Math.sign((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x));}
  function simple(poly){for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length];for(let j=i+1;j<poly.length;j++){if(j===i||j===i+1||(i===0&&j===poly.length-1))continue;const c=poly[j],d=poly[(j+1)%poly.length];if(orientation(a,b,c)!==orientation(a,b,d)&&orientation(c,d,a)!==orientation(c,d,b))return false;}}return true;}
  function cross(a,b){return a.x*b.y-a.y*b.x;}
  function edgeSpec(a,b,ref){
    const dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy),angle=Math.atan2(dy,dx),quarter=Math.round((angle-ref)/(Math.PI/2)),target=ref+quarter*Math.PI/2;
    return{dx,dy,length,target,snap:angleDelta(angle,target)<=ANGLE_TOLERANCE*Math.PI/180,unit:{x:Math.cos(target),y:Math.sin(target)}};
  }
  function lineIntersection(p,r,q,s){const den=cross(r,s);if(Math.abs(den)<1e-8)return null;const qp={x:q.x-p.x,y:q.y-p.y},t=cross(qp,s)/den;return{x:p.x+t*r.x,y:p.y+t*r.y};}
  function candidate(poly){
    if(poly.length<3)return null;const ref=Math.atan2(poly[1].y-poly[0].y,poly[1].x-poly[0].x),out=[{...poly[0]}];let corrected=0,maxMove=0;
    for(let i=1;i<poly.length-1;i++){
      const spec=edgeSpec(poly[i-1],poly[i],ref),a=out[i-1],next=spec.snap?{...poly[i],x:a.x+spec.unit.x*spec.length,y:a.y+spec.unit.y*spec.length}:{...poly[i],x:a.x+spec.dx,y:a.y+spec.dy};
      if(spec.snap&&i>1)corrected++;maxMove=Math.max(maxMove,Math.hypot(next.x-poly[i].x,next.y-poly[i].y));out.push(next);
    }
    const lastIndex=poly.length-1,incoming=edgeSpec(poly[lastIndex-1],poly[lastIndex],ref),closing=edgeSpec(poly[lastIndex],poly[0],ref),anchor=out[lastIndex-1];
    let last={...poly[lastIndex],x:anchor.x+incoming.dx,y:anchor.y+incoming.dy};
    if(incoming.snap&&closing.snap){const intersection=lineIntersection(anchor,incoming.unit,out[0],closing.unit);if(intersection)last={...last,...intersection};else last={...last,x:anchor.x+incoming.unit.x*incoming.length,y:anchor.y+incoming.unit.y*incoming.length};}
    else if(incoming.snap)last={...last,x:anchor.x+incoming.unit.x*incoming.length,y:anchor.y+incoming.unit.y*incoming.length};
    else if(closing.snap)last={...last,x:out[0].x-closing.unit.x*closing.length,y:out[0].y-closing.unit.y*closing.length};
    if(incoming.snap)corrected++;if(closing.snap)corrected++;maxMove=Math.max(maxMove,Math.hypot(last.x-poly[lastIndex].x,last.y-poly[lastIndex].y));out.push(last);
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
