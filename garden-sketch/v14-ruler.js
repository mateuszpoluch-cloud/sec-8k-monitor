(()=>{
  let lastValue=0;

  function scaleFor(d){
    for(const v of [1,2,5,10,20,50,100,200]) if(d<=v) return v;
    return Math.ceil(d/100)*100;
  }

  function readDistance(){
    try{
      if(Array.isArray(pts)&&pts.length&&hit&&typeof dist==='function'){
        const anchor=(typeof editIndex!=='undefined'&&editIndex>=0)?pts[editIndex]:pts.at(-1);
        if(anchor){
          const value=dist(anchor,hit);
          if(Number.isFinite(value)) return value;
        }
      }
    }catch(e){}
    const text=document.querySelector('#liveDistance')?.textContent||'';
    const parsed=parseFloat(text.replace(',','.').replace(/[^0-9.-]/g,''));
    return Number.isFinite(parsed)?parsed:null;
  }

  function hasPoint(){
    try{return Array.isArray(pts)&&pts.length>0;}catch(e){return false;}
  }

  function install(){
    const ar=document.querySelector('#ar');
    const sheet=document.querySelector('.ar-sheet');
    if(!ar||!sheet) return setTimeout(install,80);

    const old=document.querySelector('#ruler');
    if(old) old.style.setProperty('display','none','important');

    const box=document.createElement('div');
    box.id='ekoosPermanentRuler';
    box.innerHTML=`
      <div class="epr-head"><span>LINIJKA</span><strong id="eprValue">0,00 m</strong></div>
      <div class="epr-track"><div id="eprFill" class="epr-fill"></div></div>
      <div class="epr-labels"><span>0</span><span id="eprMid">0,5 m</span><span id="eprMax">1 m</span></div>
    `;

    const strip=document.querySelector('#pointStrip');
    sheet.insertBefore(box,strip||document.querySelector('.ar-actions'));

    const style=document.createElement('style');
    style.textContent=`
      #ruler{display:none!important}
      #ekoosPermanentRuler{display:none;margin:4px 0 8px;visibility:visible!important;opacity:1!important}
      #ekoosPermanentRuler.active{display:block!important}
      #ekoosPermanentRuler .epr-head{display:flex;justify-content:space-between;align-items:end;margin-bottom:4px}
      #ekoosPermanentRuler .epr-head span{font-size:.7rem;color:#bdd5cc}
      #ekoosPermanentRuler .epr-head strong{font-size:1.35rem;color:#fff}
      #ekoosPermanentRuler.projected .epr-head strong{color:#ffe0a0}
      #ekoosPermanentRuler .epr-track{position:relative;height:28px;border-radius:11px;overflow:hidden;border:1px solid #ffffff35;background:repeating-linear-gradient(90deg,#ffffff1c 0 1px,transparent 1px 10%,#ffffff45 10% 10.5%,transparent 10.5% 20%)}
      #ekoosPermanentRuler .epr-fill{position:absolute;inset:0 auto 0 0;width:0;background:linear-gradient(90deg,#95d65d,#d8f58e);opacity:.9;transition:width .08s linear}
      #ekoosPermanentRuler.projected .epr-fill{background:linear-gradient(90deg,#d99b32,#ffe195)}
      #ekoosPermanentRuler .epr-labels{display:flex;justify-content:space-between;margin-top:3px;font-size:.67rem;color:#c5ddd4}
    `;
    document.head.appendChild(style);

    function refresh(){
      const active=ar.classList.contains('active')&&hasPoint();
      box.classList.toggle('active',active);
      if(!active) return;

      const current=readDistance();
      if(Number.isFinite(current)) lastValue=current;
      const value=Number.isFinite(current)?current:lastValue;
      const scale=scaleFor(Math.max(value,.001));

      document.querySelector('#eprValue').textContent=value.toFixed(2).replace('.',',')+' m';
      document.querySelector('#eprFill').style.width=Math.min(100,value/scale*100)+'%';
      document.querySelector('#eprMid').textContent=(scale/2).toLocaleString('pl-PL',{maximumFractionDigits:1})+' m';
      document.querySelector('#eprMax').textContent=scale.toLocaleString('pl-PL')+' m';

      let projected=false;
      try{projected=!!usingProjection;}catch(e){}
      box.classList.toggle('projected',projected);
    }

    setInterval(refresh,100);
    document.querySelector('#startAr')?.addEventListener('click',()=>{lastValue=0;setTimeout(refresh,250)});
    document.querySelector('#arUndo')?.addEventListener('click',()=>setTimeout(refresh,0));
    document.querySelector('#arAdd')?.addEventListener('click',()=>setTimeout(refresh,0));
  }

  install();
})();