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
  function xmlEscape(value){return String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[char]));}
  function xsfNumber(value){return Number(value).toFixed(6).replace(/\.?0+$/,'');}
  function xsfGeometry(){
    const raw=copyPoints(),api=window.ekoosPlanApi,g=api?.geometry?.();
    const points=Array.isArray(g?.p)&&g.p.length>=3?g.p:raw;
    const page=g?.page||{w:297,h:210,name:'A4'};
    const xs=points.map(p=>p.x),ys=points.map(p=>p.y),width=Math.max(...xs)-Math.min(...xs),height=Math.max(...ys)-Math.min(...ys);
    const scales=[{n:100,v:0},{n:150,v:1},{n:200,v:2},{n:250,v:3},{n:300,v:4},{n:500,v:5},{n:1000,v:6}];
    const required=Math.max(width*1000/(page.w*.9),height*1000/(page.h*.9),100);
    const selected=scales.find(item=>item.n>=required)||scales.at(-1);
    const realW=page.w*selected.n/1000,realH=page.h*selected.n/1000;
    const minX=Math.min(...xs),minY=Math.min(...ys);
    return {points:points.map(p=>({x:p.x-minX+(realW-width)/2,y:p.y-minY+(realH-height)/2})),page,scale:selected};
  }
  function makeXsf(){
    const g=xsfGeometry(),closed=[...g.points,g.points[0]],pointXml=closed.map(p=>`        <d4p1:Point>\n          <d4p1:_x>${xsfNumber(p.x)}</d4p1:_x>\n          <d4p1:_y>${xsfNumber(p.y)}</d4p1:_y>\n        </d4p1:Point>`).join('\n');
    const orientation=g.page.w>=g.page.h?'Horizontal':'Vertical',pageName=/A3/i.test(g.page.name)?'A3':'A4';
    return `<?xml version="1.0" encoding="utf-8"?>
<Scene xmlns:i="http://www.w3.org/2001/XMLSchema-instance" z:Id="1" xmlns:z="http://schemas.microsoft.com/2003/10/Serialization/" xmlns="Thor.Common.Designer.Scene">
  <AuthorInfo z:Id="2" i:type="AuthorInfo"><AuthorName z:Id="3">Garden Sketch</AuthorName><Email z:Id="4"></Email><Phone z:Id="5"></Phone></AuthorInfo>
  <Ditches xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="6" z:Size="0" />
  <DrippingLines xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="7" z:Size="0" />
  <FlowerBeds xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="8" z:Size="0" />
  <Name z:Id="9">Szkic ogrodu</Name><Notes z:Id="10">Eksport z Garden Sketch v24</Notes>
  <Obstacles xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="11" z:Size="0" />
  <Parcels xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="12" z:Size="1">
    <d2p1:anyType z:Id="13" i:type="Parcel"><Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/System.Windows" z:Id="14" z:Size="${closed.length}">
${pointXml}
      </Points></d2p1:anyType>
  </Parcels>
  <SceneAccounting z:Id="15" i:type="SceneAccounting"><DitchPricePerMeter>0</DitchPricePerMeter></SceneAccounting>
  <SceneBackground z:Id="16" i:type="SceneBackground"><BackgroundImageBytes z:Id="17" /><BackgroundImageRotation>0</BackgroundImageRotation><BackgroundImageScale>1</BackgroundImageScale><BackgroundImageSizeMode>Normal</BackgroundImageSizeMode><ClipBackgroundImageToPage>false</ClipBackgroundImageToPage></SceneBackground>
  <ScenePrintSetup z:Id="18" i:type="ScenePrintSetup"><AssemblyCost>0</AssemblyCost><ContractorName i:nil="true" /><PrintDescription i:nil="true" /></ScenePrintSetup>
  <SceneSetup z:Id="19" i:type="SceneSetup"><PageOrientation>${orientation}</PageOrientation><PageSize>${pageName}</PageSize><ScaleSize>${g.scale.v}</ScaleSize></SceneSetup>
  <SectionDrivers xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="20" z:Size="0" />
  <Sections xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="21" z:Size="0" />
  <Sprinklers xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="22" z:Size="0" />
  <ValveBoxes xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" z:Id="23" z:Size="0" />
</Scene>`;
  }
  function downloadXsf(){
    if(copyPoints().length<3){alert('Najpierw utwórz poligon z co najmniej trzech punktów.');return;}
    const blob=new Blob([makeXsf()],{type:'application/xml;charset=utf-8'}),link=document.createElement('a');
    link.href=URL.createObjectURL(blob);link.download=`szkic-ogrodu-${new Date().toISOString().slice(0,10)}.xsf`;link.click();
    setTimeout(()=>URL.revokeObjectURL(link.href),1000);
  }
  function install(){
    const result=document.querySelector('#result');if(!result)return setTimeout(install,100);
    if(document.querySelector('#exportPanRysownik'))return;
    const anchor=document.querySelector('#exportPdfPlan')||document.querySelector('#exportJson');if(!anchor)return setTimeout(install,100);
    const button=document.createElement('button');button.id='exportPanRysownik';button.className='btn secondary';button.type='button';
    button.textContent='Pobierz do Pana Rysownika (JSON)';button.addEventListener('click',downloadProject);anchor.insertAdjacentElement('afterend',button);
    const xsf=document.createElement('button');xsf.id='exportXsf';xsf.className='btn primary';xsf.type='button';xsf.textContent='Pobierz projekt XSF';
    xsf.addEventListener('click',downloadXsf);button.insertAdjacentElement('beforebegin',xsf);
  }
  window.ekoosXsfApi={makeXsf};
  install();
})();
