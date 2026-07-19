(()=>{
  function hasPoints(){
    try{return Array.isArray(pts)&&pts.length>0;}catch(e){return false;}
  }
  function syncRulerLock(){
    const ar=document.querySelector('#ar');
    if(!ar)return;
    ar.classList.toggle('ruler-fixed',ar.classList.contains('active')&&hasPoints());
  }
  function install(){
    const ar=document.querySelector('#ar');
    const ruler=document.querySelector('#ruler');
    if(!ar||!ruler)return setTimeout(install,80);

    const style=document.createElement('style');
    style.textContent=`
      #ar.ruler-fixed #ruler{
        display:block!important;
        visibility:visible!important;
        opacity:1!important;
      }
    `;
    document.head.appendChild(style);

    if(typeof updateMeasure==='function'){
      const baseUpdateMeasure=updateMeasure;
      updateMeasure=function(){
        const result=baseUpdateMeasure.apply(this,arguments);
        syncRulerLock();
        return result;
      };
    }

    if(typeof addHit==='function'){
      const baseAddHit=addHit;
      addHit=function(){
        const result=baseAddHit.apply(this,arguments);
        setTimeout(syncRulerLock,0);
        return result;
      };
    }

    document.querySelector('#arUndo')?.addEventListener('click',()=>setTimeout(syncRulerLock,0));
    document.querySelector('#startAr')?.addEventListener('click',()=>{
      ar.classList.remove('ruler-fixed');
      setTimeout(syncRulerLock,300);
    });
    ar.addEventListener('click',()=>setTimeout(syncRulerLock,0));
  }
  install();
})();