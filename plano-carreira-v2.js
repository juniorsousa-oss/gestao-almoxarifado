/* PLANO DE CARREIRA — carregador isolado
   IMPORTANTE: este arquivo não altera o menu principal.
   O módulo estável é carregado de um commit conhecido. */
(function(){
  'use strict';

  var CORE='https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/7896dc3e9a527219e3be31ac5c0b1b1a6e20cb01/plano-carreira-v2.js';

  function load(src, onload){
    var s=document.createElement('script');
    s.src=src;
    s.async=false;
    s.onload=function(){ if(typeof onload==='function') onload(); };
    s.onerror=function(){ console.error('[Plano de Carreira] Falha ao carregar:',src); };
    document.head.appendChild(s);
  }

  load(CORE,function(){
    /* O editor dos indicadores é independente do Plano de Carreira. */
    if(!document.querySelector('script[data-dashboard-kpi-editor]')){
      var editor=document.createElement('script');
      editor.src='./dashboard-kpi-editor.js';
      editor.async=false;
      editor.dataset.dashboardKpiEditor='1';
      document.head.appendChild(editor);
    }
  });
})();