(()=>{
  function install(){
    if(typeof frame!=='function')return setTimeout(install,80);
    const baseFrame=frame;
    frame=function(t,f){
      baseFrame(t,f);
      try{
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
