(()=>{
let lastDistance=0;
function parseNumber(text){
  const n=parseFloat(String(text||'').replace(',','.').replace(/[^0-9.\-]/g,''));
  return Number.isFinite(n)?n:null;
}
function scaleFor(d){
  for(const v of [1,2,5,10,20,50,100,200]) if(d<=v) return v;
  return Math.ceil(d/100)*100;
}
function currentDistance(){
  try{
    if(typeof pts!=='undefined'&&pts?.length&&typeof hit!=='undefined'&&hit){
      const anchor=(typeof editIndex!=='undefined'&&editIndex>=0)?pts[editIndex]:pts.at(-1);
      if(anchor&&typeof dist==='function'){
        const d=dist(anchor,hit);
        if(Number.isFinite(d)) return d;
      }
    }
  }catch(e){}
  const live=document.querySelector('#liveDistance');
  return parseNumber(live?.textContent);
}
function forceRuler(){
  const ar=document.querySelector('#ar');
  const ruler=document.querySelector('#ruler');
  if(!ar||!ruler) return;
  const active=ar.classList.contains('active');
  let hasPoint=false;
  try{hasPoint=typeof pts!=='undefined'&&Array.isArray(pts)&&pts.length>0;}catch(e){}
  if(!(active&&hasPoint)) return;

  ar.classList.add('ruler-locked');
  ruler.classList.add('show');
  ruler.style.setProperty('display','block','important');
  ruler.style.setProperty('visibility','visible','important');
  ruler.style.setProperty('opacity','1','important');
  ruler.style.setProperty('height','auto','important');
  ruler.style.setProperty('max-height','none','important');
  ruler.style.setProperty('overflow','visible','important');

  const d=currentDistance();
  if(Number.isFinite(d)) lastDistance=d;
  const value=Number.isFinite(d)?d:lastDistance;
  const txt=value.toFixed(2).replace('.',',')+' m';
  const rv=document.querySelector('#rulerValue');
  if(rv) rv.textContent=txt;

  const scale=scaleFor(Math.max(value,.001));
  const fill=document.querySelector('#rulerFill');
  if(fill) fill.style.setProperty('width',Math.min(100,value/scale*100)+'%','important');
  const mid=document.querySelector('#rulerMid');
  const max=document.querySelector('#rulerMax');
  if(mid) mid.textContent=(scale/2).toLocaleString('pl-PL',{maximumFractionDigits:1})+' m';
  if(max) max.textContent=scale.toLocaleString('pl-PL')+' m';
}
function install(){
  const ruler=document.querySelector('#ruler');
  if(!ruler) return setTimeout(install,50);
  const style=document.createElement('style');
  style.textContent=`#ar.ruler-locked #ruler{display:block!important;visibility:visible!important;opacity:1!important;height:auto!important;max-height:none!important;overflow:visible!important}#ar.ruler-locked #ruler *{visibility:visible!important;opacity:1!important}`;
  document.head.appendChild(style);

  const observer=new MutationObserver(forceRuler);
  observer.observe(ruler,{attributes:true,attributeFilter:['class','style']});
  const ar=document.querySelector('#ar');
  if(ar) observer.observe(ar,{attributes:true,attributeFilter:['class']});

  if(typeof updateMeasure==='function'){
    const original=updateMeasure;
    updateMeasure=function(){
      const result=original.apply(this,arguments);
      forceRuler();
      return result;
    };
  }

  setInterval(forceRuler,60);
  const loop=()=>{forceRuler();requestAnimationFrame(loop)};
  requestAnimationFrame(loop);
}
install();
})();