/* Loader de compatibilidade — mantém a sincronização cloud original e garante
   que o Plano de Carreira seja carregado de forma independente.

   IMPORTANTE:
   - Não altera o index.html.
   - Não remove nem substitui a navegação existente.
   - Carrega o módulo de carreira uma única vez.
   - Se o módulo já estiver carregado pelo index, apenas o utiliza.
*/
(function(){
  'use strict';

  const ORIGINAL_SYNC='https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/85378684a950f306e1880dd3df6cb8fc7ac0178c/supabase-sync.js';
  const CAREER='./plano-carreira-v2.js';
  let careerLoading=false;

  function loadScript(src,onload,onerror){
    const s=document.createElement('script');
    s.src=src;
    s.async=false;
    s.onload=function(){if(onload)onload();};
    s.onerror=function(){if(onerror)onerror(src);};
    document.head.appendChild(s);
  }

  function careerAlreadyLoaded(){
    return typeof window.openCareerModule==='function' ||
           typeof window.renderCareerModule==='function' ||
           !!document.querySelector('script[src*="plano-carreira-v2.js"]');
  }

  function loadCareer(){
    if(careerAlreadyLoaded() || careerLoading)return;
    careerLoading=true;
    loadScript(CAREER+'?boot='+Date.now(),function(){
      careerLoading=false;
      try{
        if(typeof window.renderCareerModule==='function')window.renderCareerModule();
      }catch(e){
        console.error('[CAREER] Falha ao inicializar o módulo:',e);
      }
    },function(src){
      careerLoading=false;
      console.error('[CAREER] Falha ao carregar o módulo:',src);
    });
  }

  function bootCareer(){
    loadCareer();
    setTimeout(loadCareer,250);
    setTimeout(loadCareer,1000);
  }

  /* A sincronização original continua independente do Plano de Carreira. */
  loadScript(ORIGINAL_SYNC,function(){
    console.info('[BOOT] Sincronização cloud original carregada.');
  },function(src){
    console.error('[BOOT] Falha na sincronização cloud original:',src);
  });

  /* O módulo de carreira não depende do timing da sincronização. */
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',bootCareer,{once:true});
  }else{
    bootCareer();
  }
})();
