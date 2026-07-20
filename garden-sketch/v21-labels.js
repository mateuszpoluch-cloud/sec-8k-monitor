(()=>{
  function install(){
    const ar=document.querySelector('#ar');
    const tools=document.querySelector('.ar-tools');
    const count=document.querySelector('#count');
    if(!ar||!tools||!count)return setTimeout(install,80);
    if(document.querySelector('#labelsToggle'))return;

    const button=document.createElement('button');
    button.id='labelsToggle';
    button.type='button';
    button.className='iconbtn labels-toggle';
    button.setAttribute('aria-label','Ukryj napisy na poligonie');
    button.setAttribute('aria-pressed','true');
    button.title='Włącz lub wyłącz napisy na zapisanym poligonie';
    button.innerHTML='<span>Aa</span><i></i>';
    tools.insertBefore(button,count);

    const style=document.createElement('style');
    style.textContent=`
      #labelsToggle{position:relative;overflow:hidden;font-weight:950}
      #labelsToggle span{font-size:1.05rem;line-height:1;letter-spacing:-.05em}
      #labelsToggle i{display:none;position:absolute;left:16%;right:16%;top:49%;height:3px;border-radius:3px;background:#ffcf6b;transform:rotate(-38deg);box-shadow:0 1px 2px #153d35}
      #labelsToggle.off{background:#4a332bee!important;border-color:#ffcf6b99!important;color:#ffcf6b!important}
      #labelsToggle.off i{display:block}
      #ar.labels-off #worldSvg text{display:none!important}
      @media(max-width:700px){
        .ar-tools{gap:6px!important}
        .ar-tools .iconbtn{width:56px!important;height:56px!important;min-width:56px!important;border-radius:18px!important}
        #labelsToggle span{font-size:.95rem}
      }
    `;
    document.head.appendChild(style);

    let visible=true;
    function apply(){
      ar.classList.toggle('labels-off',!visible);
      button.classList.toggle('off',!visible);
      button.setAttribute('aria-pressed',String(visible));
      button.setAttribute('aria-label',visible?'Ukryj napisy na poligonie':'Pokaż napisy na poligonie');
      button.title=visible?'Ukryj długości i oznaczenia zapisanych punktów':'Pokaż długości i oznaczenia zapisanych punktów';
    }

    button.addEventListener('click',e=>{
      e.preventDefault();
      e.stopPropagation();
      visible=!visible;
      apply();
      try{toast(visible?'Napisy na poligonie włączone':'Napisy na poligonie wyłączone');}catch(err){}
      navigator.vibrate?.(25);
    });

    document.querySelector('#startAr')?.addEventListener('click',()=>{
      visible=true;
      apply();
    });

    apply();
  }
  install();
})();