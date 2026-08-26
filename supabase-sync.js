/* Loader de compatibilidade — sincronização cloud original + fallback seguro do Plano de Carreira.
   O módulo principal continua sendo carregado diretamente pelo index.html.
   Este arquivo NÃO substitui o módulo e NÃO o carrega em duplicidade.
*/
(function(){
  'use strict';

  const ORIGINAL_SYNC='https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/85378684a950f306e1880dd3df6cb8fc7ac0178c/supabase-sync.js';
  const CAREER='./plano-carreira-v2.js';
  let fallbackLoading=false;

  function loadScript(src,onload,onerror){
    const s=document.createElement('script');
    s.src=src;
    s.async=false;
    s.onload=function(){if(onload)onload();};
    s.onerror=function(){if(onerror)onerror(src);};
    document.head.appendChild(s);
  }

  function normalize(v){
    return String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim();
  }

  function ensureCareerNav(){
    const nav=document.querySelector('.nav');
    if(!nav)return false;

    let btn=document.getElementById('navCarreira');
    if(!btn){
      btn=document.createElement('button');
      btn.id='navCarreira';
      btn.type='button';
      btn.innerHTML='<span style="display:inline-block;width:18px;text-align:center;margin-right:3px;font-size:15px;font-weight:900">⇧</span> PLANO DE CARREIRA';
      const teamBtn=Array.from(nav.querySelectorAll('button')).find(b=>normalize(b.textContent).includes('GESTAO DE EQUIPES'));
      if(teamBtn)teamBtn.insertAdjacentElement('afterend',btn);
      else nav.appendChild(btn);
    }

    btn.onclick=function(){
      if(typeof window.openCareerModule==='function'){
        window.openCareerModule();
        return;
      }
      if(fallbackLoading)return;
      fallbackLoading=true;
      loadScript(CAREER+'?fallback='+Date.now(),function(){
        fallbackLoading=false;
        if(typeof window.openCareerModule==='function')window.openCareerModule();
        else if(typeof window.renderCareerModule==='function')window.renderCareerModule();
        else alert('Não foi possível inicializar o Plano de Carreira.');
      },function(){
        fallbackLoading=false;
        alert('Não foi possível carregar o Plano de Carreira.');
      });
    };
    return true;
  }

  function bootCareerFallback(){
    ensureCareerNav();
    setTimeout(ensureCareerNav,250);
    setTimeout(ensureCareerNav,1000);
    setTimeout(ensureCareerNav,2500);
  }

  /* Sincronização original permanece isolada do módulo de carreira. */
  loadScript(ORIGINAL_SYNC,function(){
    console.info('[BOOT] Sincronização cloud original carregada.');
  },function(src){
    console.error('[BOOT] Falha na sincronização cloud original:',src);
  });

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',bootCareerFallback,{once:true});
  }else{
    bootCareerFallback();
  }
})();
