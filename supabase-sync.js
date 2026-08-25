/* Loader de compatibilidade.
   Mantém a sincronização cloud original e carrega o módulo Plano de Carreira.
   O código original é referenciado por SHA imutável para evitar recursão. */
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
      loadScript(CAREER_MODULE);
    },
    function(src){
      console.error('[BOOT] Falha ao carregar:',src);
    }
  );
})();
