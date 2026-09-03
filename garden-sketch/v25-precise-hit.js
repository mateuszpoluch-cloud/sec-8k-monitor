(()=>{
  function install(){
    if(typeof frame!=='function')return setTimeout(install,80);
    const baseFrame=frame;
    frame=function(t,f){
      const reticle=document.querySelector('#reticle');
      // Standardowy WebXR hit-test z viewerSpace biegnie przez środek widoku.
      // Symbol celownika musi wskazywać dokładnie ten sam piksel.
      if(reticle)reticle.style.top='50%';
      baseFrame(t,f);
      try{
        if(reticle)reticle.style.top='50%';
        const firstEdgeLocked=window.ekoosFirstEdgeGuide?.isLocked?.()&&Array.isArray(pts)&&pts.length===1;
        const direct=!obstacleMode&&!usingProjection&&rawHit&&Number.isFinite(rawHit.x)&&Number.isFinite(rawHit.y);
        if(direct&&!firstEdgeLocked){
          hit={...rawHit,projected:false};
          updateMeasure?.();updateMiniMap?.();
          let pose=null;try{pose=f.getViewerPose(refSpace);}catch(error){}
          updateWorldOverlay?.(pose);
        }
      }catch(error){}
    };
  }
  install();
})();
