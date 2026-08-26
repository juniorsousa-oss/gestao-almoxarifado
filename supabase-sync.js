/* Loader de compatibilidade — sincronização cloud original.
   O Plano de Carreira é carregado diretamente pelo index.html e possui
   sua própria navegação. Este arquivo NÃO cria, remove ou substitui o
   botão do Plano de Carreira, evitando conflito entre os dois módulos.
*/
(function(){
  'use strict';

  const ORIGINAL_SYNC='https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/85378684a950f306e1880dd3df6cb8fc7ac0178c/supabase-sync.js';

  function loadScript(src,onload,onerror){
    const s=document.createElement('script');
    s.src=src;
    s.async=false;
    s.onload=function(){if(onload)onload();};
    s.onerror=function(){if(onerror)onerror(src);};
    document.head.appendChild(s);
  }

  loadScript(ORIGINAL_SYNC,function(){
    console.info('[BOOT] Sincronização cloud original carregada.');
  },function(src){
    console.error('[BOOT] Falha na sincronização cloud original:',src);
  });
})();
