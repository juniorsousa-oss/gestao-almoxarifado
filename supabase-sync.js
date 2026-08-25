/* Loader de compatibilidade.
   Mantém a sincronização cloud original.
   O módulo Plano de Carreira é carregado diretamente pelo index.html. */
(function(){
  'use strict';

  const ORIGINAL_SYNC = 'https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/85378684a950f306e1880dd3df6cb8fc7ac0178c/supabase-sync.js';

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
      console.log('[BOOT] Sincronização cloud original carregada.');
    },
    function(src){
      console.error('[BOOT] Falha ao carregar:',src);
    }
  );
})();
