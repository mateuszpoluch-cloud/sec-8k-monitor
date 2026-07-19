(()=>{
let lastAim=null,lastPose=null,lostAt=0;
function placeReticle(){
  const sheet=document.querySelector('.ar-sheet');
  const ret=document.querySelector('#reticle');
  if(!sheet||!ret)return;
  const top=sheet.getBoundingClientRect().top;
  const y=Math.max(innerHeight*.29,Math.min(innerHeight*.53,top-86));
  ret.style.top=y+'px';
}
function reticleRay(view){
  if(!view)return null;
  const ret=document.querySelector('#reticle');
  const r=ret?.getBoundingClientRect();
  const cx=r?r.left+r.width/2:innerWidth/2;
  const cy=r?r.top+r.height/2:innerHeight*.52;
  const nx=cx/innerWidth*2-1;
  const ny=1-cy/innerHeight*2;
  const p=view.projectionMatrix;
  const m=view.transform.matrix;
  const x=nx/(p[0]||1),y=ny/(p[5]||1),z=-1;
  let dx=m[0]*x+m[4]*y+m[8]*z;
  let dy=m[1]*x+m[5]*y+m[9]*z;
  let dz=m[2]*x+m[6]*y+m[10]*z;
  const len=Math.hypot(dx,dy,dz)||1;
  dx/=len;dy/=len;dz/=len;
  return {o:{x:m[12],y:m[13],z:m[14]},d:{x:dx,y:dy,z:dz}};
}
function stableGroundPoint(view){
  if(groundY==null&&pts?.length&&Number.isFinite(pts[0].wy))groundY=pts[0].wy;
  if(groundY==null)return null;
  const ray=reticleRay(view);
  if(!ray)return null;
  let {x:dx,y:dy,z:dz}=ray.d;
  const o=ray.o;
  if(dy>-.012){
    dy=-.012;
    const len=Math.hypot(dx,dy,dz)||1;
    dx/=len;dy/=len;dz/=len;
  }
  let t=(groundY-o.y)/dy;
  if(!Number.isFinite(t)||t<=0)return null;
  t=Math.min(t,100);
  return {x:o.x+dx*t,y:-o.z-dz*t,wx:o.x+dx*t,wy:groundY,wz:o.z+dz*t,projected:true};
}
function blend(a,b){
  if(!a)return {...b};
  const jump=Math.hypot(a.x-b.x,a.y-b.y);
  const k=jump>3?.82:.62;
  const q={...b};
  for(const key of ['x','y','wx','wy','wz']){
    if(Number.isFinite(a[key])&&Number.isFinite(b[key]))q[key]=a[key]*(1-k)+b[key]*k;
  }
  return q;
}
function ensureHoldNote(){
  if(document.querySelector('#ekoosHoldNote'))return;
  const p=document.createElement('p');
  p.id='ekoosHoldNote';
  p.style.cssText='display:none;text-align:center;color:#ffe0a0;font-size:.68rem;margin:0 0 4px';
  p.textContent='Chwilowa utrata śledzenia — ostatni pomiar pozostaje widoczny.';
  document.querySelector('#ruler')?.before(p);
}
function install(){
  if(typeof frame!=='function'||typeof updateMeasure!=='function')return setTimeout(install,50);
  ensureHoldNote();
  groundProjection=stableGroundPoint;
  const baseFrame=frame;
  frame=function(t,f){
    let pose=null;
    try{pose=f.getViewerPose(refSpace)}catch(e){}
    if(pose)lastPose=pose;
    baseFrame(t,f);
    if(!pts?.length){lastAim=null;lostAt=0;return;}
    if(groundY==null&&Number.isFinite(pts[0]?.wy))groundY=pts[0].wy;
    let candidate=pose?.views?.length?stableGroundPoint(pose.views[0]):null;
    const directOk=!obstacleMode&&rawHit&&Number.isFinite(rawHit.wy)&&groundY!=null&&Math.abs(rawHit.wy-groundY)<.15;
    if(directOk)candidate={...rawHit,projected:false};
    if(candidate){
      candidate=blend(lastAim,candidate);
      lastAim={...candidate};
      hit=candidate;
      usingProjection=!!candidate.projected;
      lostAt=0;
    }else if(lastAim){
      hit={...lastAim,projected:true};
      usingProjection=true;
      if(!lostAt)lostAt=performance.now();
    }else{
      hit={...pts.at(-1),projected:true};
      usingProjection=true;
      if(!lostAt)lostAt=performance.now();
    }
    try{
      updateMeasure();
      updateMiniMap();
      updateWorldOverlay(pose||lastPose);
      updateArMode();
    }catch(e){}
    document.querySelector('#ruler')?.classList.add('show');
    document.querySelector('#distanceCard')?.classList.add('show');
    const add=document.querySelector('#arAdd');
    if(add)add.disabled=!hit;
    const ret=document.querySelector('#reticle');
    if(ret){
      ret.classList.toggle('ok',!!hit&&!usingProjection);
      ret.classList.toggle('projected',!!hit&&usingProjection);
    }
    const note=document.querySelector('#ekoosHoldNote');
    if(note)note.style.display=lostAt&&performance.now()-lostAt>350?'block':'none';
    placeReticle();
  };
  if(typeof addHit==='function'){
    const baseAdd=addHit;
    addHit=function(){
      if(hit&&groundY==null&&Number.isFinite(hit.wy))groundY=hit.wy;
      const result=baseAdd.apply(this,arguments);
      if(hit)lastAim={...hit};
      setTimeout(placeReticle,0);
      return result;
    };
  }
  document.querySelector('#startAr')?.addEventListener('click',()=>{
    lastAim=null;lastPose=null;lostAt=0;
    setTimeout(placeReticle,250);
    setTimeout(placeReticle,800);
  });
  addEventListener('resize',placeReticle,{passive:true});
  addEventListener('orientationchange',()=>setTimeout(placeReticle,250),{passive:true});
  const sheet=document.querySelector('.ar-sheet');
  if(sheet&&window.ResizeObserver)new ResizeObserver(placeReticle).observe(sheet);
  setTimeout(placeReticle,100);
}
install();
})();