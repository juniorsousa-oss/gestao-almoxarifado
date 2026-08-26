/* Loader de compatibilidade.
   Mantém a sincronização cloud original e garante que o módulo Plano de Carreira
   seja inicializado somente depois da sincronização original. */
(function(){
  'use strict';

  const ORIGINAL_SYNC = 'https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/85378684a950f306e1880dd3df6cb8fc7ac0178c/supabase-sync.js';
  const CAREER_MODULE = './plano-carreira-v2.js';

  function loadScript(src, onload, onerror){
    const script=document.createElement('script');
    script.src=src;
    script.async=false;
    script.onload=()=>onload&&onload();
    script.onerror=()=>onerror&&onerror(src);
    document.head.appendChild(script);
  }

  loadScript(
    ORIGINAL_SYNC,
    function(){
      /* O index.html já carrega o módulo. Se ele já inicializou,
         apenas pedimos uma nova renderização para garantir que o item
         permaneça na navegação. Caso ainda não exista, carregamos o arquivo. */
      if(typeof window.renderCareerModule==='function'){
        try{ window.renderCareerModule(); }catch(e){ console.warn('[CAREER] Falha ao atualizar módulo:',e); }
        return;
      }
      loadScript(CAREER_MODULE, null, function(src){
        console.error('[BOOT] Falha ao carregar:',src);
      });
    },
    function(src){
      console.error('[BOOT] Falha ao carregar:',src);
    }
  );
})();
