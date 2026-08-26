/* Loader de compatibilidade.
   Mantém a sincronização cloud original e garante que o módulo Plano de Carreira
   seja inicializado de forma independente da sincronização antiga. */
(function(){
  'use strict';

  const ORIGINAL_SYNC = 'https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/85378684a950f306e1880dd3df6cb8fc7ac0178c/supabase-sync.js';
  const CAREER_MODULE = './plano-carreira-v2.js';
  let careerLoaded = false;
  let careerAttempts = 0;

  function loadScript(src,onload,onerror){
    const script=document.createElement('script');
    script.src=src;
    script.async=false;
    script.onload=()=>onload&&onload();
    script.onerror=()=>onerror&&onerror(src);
    document.head.appendChild(script);
  }

  function ensureCareer(){
    if(careerLoaded || document.getElementById('navCarreira') || typeof window.renderCareerModule==='function'){
      try{ window.renderCareerModule?.(); }catch(e){}
      return;
    }
    if(careerAttempts>=2)return;
    careerAttempts++;
    loadScript(
      CAREER_MODULE+'?boot='+careerAttempts,
      function(){
        careerLoaded=true;
        try{ window.renderCareerModule?.(); }catch(e){ console.warn('[CAREER] Falha ao renderizar:',e); }
      },
      function(src){
        console.error('[CAREER] Falha ao carregar:',src);
        setTimeout(ensureCareer,1000);
      }
    );
  }

  /* O Plano de Carreira não pode depender do carregamento da sincronização
     antiga. Se o arquivo remoto falhar, o módulo continua funcionando. */
  ensureCareer();
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',ensureCareer,{once:true});
  }else{
    setTimeout(ensureCareer,250);
  }
  setTimeout(ensureCareer,1500);

  /* Mantém a sincronização original como processo independente. */
  loadScript(
    ORIGINAL_SYNC,
    function(){ console.info('[BOOT] Sincronização original carregada.'); },
    function(src){ console.error('[BOOT] Falha ao carregar:',src); }
  );
})();
