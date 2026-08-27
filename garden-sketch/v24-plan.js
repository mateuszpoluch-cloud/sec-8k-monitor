(()=>{
  const state={align:'longest',turns:0,dimensions:true,format:'A4',orientation:'landscape',scale:'auto',offsetX:0,offsetY:0};
  const SCALE_CHOICES=[20,25,50,75,100,150,200,250,500,1000];

  function copyPoints(){try{return Array.isArray(pts)?pts.map(p=>({...p})):[];}catch(e){return[];}}
  function boundsOf(p){const xs=p.map(q=>q.x),ys=p.map(q=>q.y);return{minX:Math.min(...xs),maxX:Math.max(...xs),minY:Math.min(...ys),maxY:Math.max(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)};}
  function centreOf(p){return{x:p.reduce((s,q)=>s+q.x,0)/p.length,y:p.reduce((s,q)=>s+q.y,0)/p.length};}
  function edgeAngle(p,mode){
    if(p.length<2||mode==='raw')return 0;
    let i=0;
    if(mode==='longest'){
      let best=-1;
      for(let k=0;k<p.length;k++){
        const a=p[k],b=p[(k+1)%p.length],d=Math.hypot(b.x-a.x,b.y-a.y);
        if(d>best){best=d;i=k;}
      }
    }
    const a=p[i],b=p[(i+1)%p.length];
    let angle=Math.atan2(b.y-a.y,b.x-a.x);
    if(Math.cos(angle)<0)angle+=Math.PI;
    return angle;
  }
  function orientedPoints(){
    const p=copyPoints();if(!p.length)return p;
    const c=centreOf(p),angle=-edgeAngle(p,state.align)+state.turns*Math.PI/2,co=Math.cos(angle),si=Math.sin(angle);
    return p.map(q=>{const x=q.x-c.x,y=q.y-c.y;return{...q,x:x*co-y*si,y:x*si+y*co};});
  }
  function pageSpec(){
    let w=state.format==='A3'?420:297,h=state.format==='A3'?297:210;
    if(state.orientation==='portrait')[w,h]=[h,w];
    return{w,h,name:state.format};
  }
  function standardScale(required){return SCALE_CHOICES.find(v=>v>=required)||Math.ceil(required/500)*500;}
  function geometry(){
    const p=orientedPoints(),page=pageSpec();
    if(!p.length)return{p,page,scale:100,fit:true};
    const b=boundsOf(p),margin=12,titleH=24,plot={x:margin,y:margin,w:page.w-margin*2,h:page.h-margin*2-titleH};
    const required=Math.max((b.w*1000*1.10)/plot.w,(b.h*1000*1.10)/plot.h,1);
    const scale=state.scale==='auto'?standardScale(required):Number(state.scale);
    const mmPerM=1000/scale,drawW=b.w*mmPerM,drawH=b.h*mmPerM;
    const ox=plot.x+(plot.w-drawW)/2-b.minX*mmPerM+state.offsetX;
    const oy=plot.y+(plot.h-drawH)/2+b.maxY*mmPerM+state.offsetY;
    const map=q=>({x:ox+q.x*mmPerM,y:oy-q.y*mmPerM});
    const corners=p.map(map),cx=corners.map(q=>q.x),cy=corners.map(q=>q.y);
    const fit=drawW<=plot.w&&drawH<=plot.h&&Math.min(...cx)>=plot.x&&Math.max(...cx)<=plot.x+plot.w&&Math.min(...cy)>=plot.y&&Math.max(...cy)<=plot.y+plot.h;
    return{p,page,b,plot,scale,mmPerM,drawW,drawH,fit,map};
  }
  function niceBar(scale){
    const mmPerM=1000/scale;
    let best=1;
    for(const m of [0.5,1,2,5,10,20,50,100,200]){const mm=m*mmPerM;if(mm>=35&&mm<=85)return m;if(mm<85)best=m;}
    return best;
  }
  function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
  function planSvg(){
    const g=geometry();if(!g.p.length)return'';
    const {page,p,map,scale,fit}=g,mp=p.map(map),path=mp.map((q,i)=>(i?'L':'M')+q.x.toFixed(2)+' '+q.y.toFixed(2)).join(' ')+' Z';
    const centroid=centreOf(mp);
    let dims='';
    if(state.dimensions){
      dims=p.map((q,i)=>{
        const r=p[(i+1)%p.length],a=mp[i],b=mp[(i+1)%p.length],mx=(a.x+b.x)/2,my=(a.y+b.y)/2;
        let nx=-(b.y-a.y),ny=b.x-a.x,n=Math.hypot(nx,ny)||1;nx/=n;ny/=n;
        if((mx-centroid.x)*nx+(my-centroid.y)*ny<0){nx=-nx;ny=-ny;}
        const x=mx+nx*5,y=my+ny*5,label=Math.hypot(r.x-q.x,r.y-q.y).toFixed(2).replace('.',',')+' m';
        return`<text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="middle" class="dim">${label}</text>`;
      }).join('');
    }
    const dots=mp.map((q,i)=>`<circle cx="${q.x}" cy="${q.y}" r="1.5" class="vertex"/><text x="${q.x+2.3}" y="${q.y-2.3}" class="point">P${i+1}</text>`).join('');
    const barM=niceBar(scale),barMm=barM*1000/scale,segments=4,sx=14,sy=page.h-31,seg=barMm/segments;
    let bar='';for(let i=0;i<segments;i++)bar+=`<rect x="${sx+i*seg}" y="${sy}" width="${seg}" height="4" class="bar ${i%2?'bar-light':'bar-dark'}"/>`;
    bar+=`<line x1="${sx}" y1="${sy+4}" x2="${sx+barMm}" y2="${sy+4}" class="thin"/><text x="${sx}" y="${sy+9}" class="small">0</text><text x="${sx+barMm}" y="${sy+9}" text-anchor="end" class="small">${barM.toLocaleString('pl-PL')} m</text>`;
    const area=typeof window.area==='function'?window.area(copyPoints()):0,per=typeof window.perimeter==='function'?window.perimeter(copyPoints()):0;
    const warn=fit?'':`<g class="warning"><rect x="12" y="12" width="${page.w-24}" height="10" rx="2"/><text x="${page.w/2}" y="18.5" text-anchor="middle">Wybrana skala nie miesci rysunku na arkuszu</text></g>`;
    return`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${page.w} ${page.h}" width="${page.w}mm" height="${page.h}mm">
    <style>.sheet{fill:#fff}.border{fill:none;stroke:#173f35;stroke-width:.45}.shape{fill:#a9dbc2;fill-opacity:.45;stroke:#174c3e;stroke-width:.8;stroke-linejoin:round}.vertex{fill:#218b62;stroke:#fff;stroke-width:.5}.point{font:700 3px system-ui;fill:#174c3e}.dim{font:700 3.4px system-ui;fill:#173f35;paint-order:stroke;stroke:#fff;stroke-width:1.8px;stroke-linejoin:round}.title{font:800 5px system-ui;fill:#173f35}.meta{font:600 3px system-ui;fill:#355c52}.small{font:600 2.8px system-ui;fill:#173f35}.thin{stroke:#173f35;stroke-width:.35}.bar{stroke:#173f35;stroke-width:.3}.bar-dark{fill:#173f35}.bar-light{fill:#fff}.warning rect{fill:#fff0d4;stroke:#d39225;stroke-width:.4}.warning text{font:700 3px system-ui;fill:#8a5710}</style>
    <rect class="sheet" width="${page.w}" height="${page.h}"/><rect class="border" x="7" y="7" width="${page.w-14}" height="${page.h-14}"/>
    ${warn}<path class="shape" d="${path}"/>${dims}${dots}${bar}
    <line class="thin" x1="7" y1="${page.h-24}" x2="${page.w-7}" y2="${page.h-24}"/>
    <text class="title" x="${page.w-12}" y="${page.h-17}" text-anchor="end">SZKIC OGRODU</text>
    <text class="meta" x="${page.w-12}" y="${page.h-11}" text-anchor="end">Skala 1:${scale} • ${page.name} ${state.orientation==='landscape'?'poziomo':'pionowo'}</text>
    <text class="meta" x="${page.w/2}" y="${page.h-17}" text-anchor="middle">Powierzchnia: ${area.toFixed(1).replace('.',',')} m²</text>
    <text class="meta" x="${page.w/2}" y="${page.h-11}" text-anchor="middle">Obwód: ${per.toFixed(1).replace('.',',')} m</text>
    </svg>`;
  }
  function updatePreview(){
    const preview=document.querySelector('#preview');if(!preview||!copyPoints().length)return;
    const svg=planSvg();preview.innerHTML=svg;const g=geometry();
    preview.style.height='auto';preview.style.minHeight='0';preview.style.padding='10px';preview.style.background='#d9ddd9';preview.style.aspectRatio=`${g.page.w}/${g.page.h}`;
    const s=document.querySelector('#planScaleInfo');if(s)s.textContent=`Skala wynikowa: 1:${g.scale}${g.fit?'':' — nie mieści się'}`;
    document.querySelector('#exportPdfPlan')?.toggleAttribute('disabled',!g.fit);
  }
  function download(name,type,data){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),800);}
  function pdfEscape(s){return String(s).replace(/\\/g,'\\\\').replace(/\(/g,'\\(').replace(/\)/g,'\\)');}
  function makePdf(){
    const g=geometry();if(!g.fit){alert('Wybrana skala nie mieści rysunku na arkuszu. Wybierz skalę Auto, większy mianownik albo format A3.');return;}
    const k=72/25.4,W=g.page.w*k,H=g.page.h*k,py=y=>(g.page.h-y)*k,cmd=[];
    const line=(x1,y1,x2,y2)=>cmd.push(`${(x1*k).toFixed(2)} ${py(y1).toFixed(2)} m ${(x2*k).toFixed(2)} ${py(y2).toFixed(2)} l S`);
    const rect=(x,y,w,h,fill=false)=>cmd.push(`${(x*k).toFixed(2)} ${py(y+h).toFixed(2)} ${(w*k).toFixed(2)} ${(h*k).toFixed(2)} re ${fill?'f':'S'}`);
    const text=(s,x,y,size=8,align='left')=>{const approx=s.length*size*.26;let xp=x*k;if(align==='center')xp-=approx;if(align==='right')xp-=approx*2;cmd.push(`BT /F1 ${size} Tf ${xp.toFixed(2)} ${py(y).toFixed(2)} Td (${pdfEscape(s)}) Tj ET`);};
    cmd.push('1 1 1 rg');rect(0,0,g.page.w,g.page.h,true);cmd.push('0.09 0.25 0.21 RG 0.45 w');rect(7,7,g.page.w-14,g.page.h-14,false);
    const mp=g.p.map(g.map);cmd.push('0.66 0.86 0.76 rg 0.09 0.30 0.24 RG 1.7 w');
    cmd.push(`${(mp[0].x*k).toFixed(2)} ${py(mp[0].y).toFixed(2)} m`);for(let i=1;i<mp.length;i++)cmd.push(`${(mp[i].x*k).toFixed(2)} ${py(mp[i].y).toFixed(2)} l`);cmd.push('h B');
    const c=centreOf(mp);
    if(state.dimensions){
      g.p.forEach((q,i)=>{const r=g.p[(i+1)%g.p.length],a=mp[i],b=mp[(i+1)%mp.length],mx=(a.x+b.x)/2,my=(a.y+b.y)/2;let nx=-(b.y-a.y),ny=b.x-a.x,n=Math.hypot(nx,ny)||1;nx/=n;ny/=n;if((mx-c.x)*nx+(my-c.y)*ny<0){nx=-nx;ny=-ny;}const label=Math.hypot(r.x-q.x,r.y-q.y).toFixed(2).replace('.',',')+' m',x=mx+nx*5,y=my+ny*5;cmd.push('1 1 1 rg');rect(x-label.length*1.0,y-2.6,label.length*2.0,4.5,true);cmd.push('0.09 0.25 0.21 rg');text(label,x,y+.8,8,'center');});
    }
    cmd.push('0.13 0.55 0.38 rg');mp.forEach((q,i)=>{rect(q.x-1,q.y-1,2,2,true);cmd.push('0.09 0.25 0.21 rg');text('P'+(i+1),q.x+2.2,q.y-2.2,7);cmd.push('0.13 0.55 0.38 rg');});
    const barM=niceBar(g.scale),barMm=barM*1000/g.scale,sx=14,sy=g.page.h-31,seg=barMm/4;for(let i=0;i<4;i++){cmd.push(i%2?'1 1 1 rg':'0.09 0.25 0.21 rg');rect(sx+i*seg,sy,seg,4,true);cmd.push('0.09 0.25 0.21 RG 0.5 w');rect(sx+i*seg,sy,seg,4,false);}line(sx,sy+4,sx+barMm,sy+4);cmd.push('0.09 0.25 0.21 rg');text('0',sx,sy+9,7);text(String(barM)+' m',sx+barMm,sy+9,7,'right');
    line(7,g.page.h-24,g.page.w-7,g.page.h-24);text('SZKIC OGRODU',g.page.w-12,g.page.h-17,12,'right');text(`Skala 1:${g.scale}  ${g.page.name}`,g.page.w-12,g.page.h-11,8,'right');const ar=typeof window.area==='function'?window.area(copyPoints()):0,pe=typeof window.perimeter==='function'?window.perimeter(copyPoints()):0;text(`Powierzchnia: ${ar.toFixed(1)} m2`,g.page.w/2,g.page.h-17,8,'center');text(`Obwod: ${pe.toFixed(1)} m`,g.page.w/2,g.page.h-11,8,'center');
    const stream=cmd.join('\n'),objects=[];objects[1]='<< /Type /Catalog /Pages 2 0 R >>';objects[2]='<< /Type /Pages /Kids [3 0 R] /Count 1 >>';objects[3]=`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${W.toFixed(2)} ${H.toFixed(2)}] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>`;objects[4]='<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>';objects[5]=`<< /Length ${new TextEncoder().encode(stream).length} >>\nstream\n${stream}\nendstream`;
    let pdf='%PDF-1.4\n',offsets=[0];for(let i=1;i<=5;i++){offsets[i]=new TextEncoder().encode(pdf).length;pdf+=`${i} 0 obj\n${objects[i]}\nendobj\n`;}const xref=new TextEncoder().encode(pdf).length;pdf+='xref\n0 6\n0000000000 65535 f \n';for(let i=1;i<=5;i++)pdf+=String(offsets[i]).padStart(10,'0')+' 00000 n \n';pdf+=`trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`;
    download(`szkic-ogrodu-${state.format.toLowerCase()}-1-${g.scale}.pdf`,'application/pdf',pdf);
  }
  function installControls(){
    const result=document.querySelector('#result'),preview=document.querySelector('#preview');if(!result||!preview)return setTimeout(installControls,80);if(document.querySelector('#planControls'))return;
    const box=document.createElement('div');box.id='planControls';box.className='section';box.innerHTML=`<h3>Arkusz projektu</h3><p class="muted">Rzut jest prostowany i centrowany na arkuszu z zachowaniem rzeczywistej skali.</p><div class="plan-grid">
      <label>Ustawienie rzutu<select id="planAlign"><option value="longest">Najdłuższy bok poziomo</option><option value="first">P1–P2 poziomo</option><option value="raw">Bez prostowania</option></select></label>
      <label>Format<select id="planFormat"><option>A4</option><option>A3</option></select></label>
      <label>Arkusz<select id="planOrientation"><option value="landscape">Poziomo</option><option value="portrait">Pionowo</option></select></label>
      <label>Skala<select id="planScale"><option value="auto">Auto</option><option value="50">1:50</option><option value="100">1:100</option><option value="150">1:150</option><option value="200">1:200</option><option value="250">1:250</option><option value="500">1:500</option></select></label>
      <label class="check"><input id="planDimensions" type="checkbox" checked> Pokazuj wymiary</label>
      <button id="planRotate" class="btn secondary" type="button">↻ Obróć rzut 90°</button>
    </div><div id="planScaleInfo" class="plan-info"></div><button id="exportPdfPlan" class="btn primary" type="button">Pobierz PDF A4/A3</button>`;
    preview.after(box);
    const style=document.createElement('style');style.textContent=`#planControls{margin-top:16px}.plan-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;align-items:end}.plan-grid .check{display:flex;align-items:center;gap:8px;min-height:46px;padding:8px 10px;border:1px solid var(--line);border-radius:12px;background:#fff}.plan-grid .check input{min-height:0;width:20px;height:20px}.plan-info{margin:10px 0;padding:9px 12px;border-radius:12px;background:#edf7f2;color:#245b4c;font-weight:800}@media(max-width:700px){.plan-grid{grid-template-columns:1fr 1fr}.plan-grid .check{grid-column:1/-1}}#preview>svg{width:100%;height:auto;filter:drop-shadow(0 5px 12px #0003)}`;document.head.appendChild(style);
    document.querySelector('#planAlign').onchange=e=>{state.align=e.target.value;state.turns=0;updatePreview();};document.querySelector('#planFormat').onchange=e=>{state.format=e.target.value;updatePreview();};document.querySelector('#planOrientation').onchange=e=>{state.orientation=e.target.value;updatePreview();};document.querySelector('#planScale').onchange=e=>{state.scale=e.target.value;updatePreview();};document.querySelector('#planDimensions').onchange=e=>{state.dimensions=e.target.checked;updatePreview();};document.querySelector('#planRotate').onclick=()=>{state.turns=(state.turns+1)%4;updatePreview();};document.querySelector('#exportPdfPlan').onclick=makePdf;
    const oldSvg=document.querySelector('#exportSvg');if(oldSvg){oldSvg.textContent='Pobierz arkusz SVG';oldSvg.onclick=()=>download('szkic-ogrodu-arkusz.svg','image/svg+xml',planSvg());}
  }
  function install(){
    if(typeof renderResult!=='function')return setTimeout(install,80);installControls();const base=renderResult;renderResult=function(){const r=base.apply(this,arguments);installControls();setTimeout(updatePreview,0);return r;};
    if(!document.querySelector('#result')?.classList.contains('hidden'))setTimeout(updatePreview,0);
  }
  window.ekoosPlanApi={
    geometry,
    updatePreview,
    getOffset:()=>({x:state.offsetX,y:state.offsetY}),
    setOffset:(x,y)=>{state.offsetX=Number(x)||0;state.offsetY=Number(y)||0;updatePreview();},
    resetOffset:()=>{state.offsetX=0;state.offsetY=0;updatePreview();}
  };
  install();
})();
