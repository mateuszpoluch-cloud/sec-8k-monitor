(()=>{
  const CONTRACT='ekoos.garden-polygon',VERSION=1;
  function copyPoints(){try{return Array.isArray(pts)?pts.map(point=>({x:Number(point.x),y:Number(point.y),projected:Boolean(point.projected)})):[];}catch(error){return[];}}
  function downloadProject(){
    const polygon=copyPoints();
    if(polygon.length<3){alert('Najpierw utwórz poligon z co najmniej trzech punktów.');return;}
    const payload={contract:CONTRACT,version:VERSION,unit:'m',source:'garden-sketch-v24',createdAt:new Date().toISOString(),polygon,
      metadata:{area:typeof window.area==='function'?window.area(polygon):null,perimeter:typeof window.perimeter==='function'?window.perimeter(polygon):null}};
    const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),link=document.createElement('a');
    link.href=URL.createObjectURL(blob);link.download=`projekt-ogrodu-${new Date().toISOString().slice(0,10)}.ekoos.json`;link.click();
    setTimeout(()=>URL.revokeObjectURL(link.href),1000);
  }
  function install(){
    const result=document.querySelector('#result');if(!result)return setTimeout(install,100);
    if(document.querySelector('#exportPanRysownik'))return;
    const anchor=document.querySelector('#exportPdfPlan')||document.querySelector('#exportJson');if(!anchor)return setTimeout(install,100);
    const button=document.createElement('button');button.id='exportPanRysownik';button.className='btn secondary';button.type='button';
    button.textContent='Pobierz do Pana Rysownika';button.addEventListener('click',downloadProject);anchor.insertAdjacentElement('afterend',button);
  }
  install();
})();
