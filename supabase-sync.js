/* Loader de compatibilidade — NÃO altera o aplicativo principal.
   1) Mantém a sincronização cloud original.
   2) Garante que o menu Plano de Carreira exista mesmo se o módulo externo
      carregar depois ou falhar na inicialização automática.
*/
(function(){
  'use strict';

  const ORIGINAL_SYNC='https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/85378684a950f306e1880dd3df6cb8fc7ac0178c/supabase-sync.js';
  const CAREER='./plano-carreira-v2.js';
  const NAV_ID='navCarreira';
  let careerLoading=false;

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

  function openCareer(){
    if(careerLoading)return;

    /* Se o módulo já expôs sua API pública, abre diretamente. */
    if(typeof window.openCareerModule==='function'){
      window.openCareerModule();
      return;
    }

    careerLoading=true;

    /*
       O módulo de carreira atual é um IIFE e registra o próprio onclick
       no botão #navCarreira. Como o loader também cria esse botão, removemos
       somente o botão de compatibilidade antes de recarregar o módulo.
       Assim o próprio módulo assume o controle da navegação sem alterar
       qualquer outra parte do aplicativo.
    */
    const old=document.getElementById(NAV_ID);
    if(old)old.remove();

    loadScript(CAREER+'?open='+Date.now(),function(){
      careerLoading=false;
      const moduleButton=document.getElementById(NAV_ID);
      if(moduleButton){
        moduleButton.click();
        return;
      }
      if(typeof window.openCareerModule==='function'){
        window.openCareerModule();
        return;
      }
      console.error('[CAREER] Módulo carregado, mas o botão não foi registrado.');
      alert('O Plano de Carreira foi carregado, mas não conseguiu registrar a navegação.');
      bootCareerNav();
    },function(src){
      careerLoading=false;
      console.error('[CAREER] Falha ao carregar módulo:',src);
      alert('Não foi possível carregar o Plano de Carreira.');
      bootCareerNav();
    });
  }

  function ensureCareerNav(){
    const nav=document.querySelector('.nav');
    if(!nav || document.getElementById(NAV_ID))return;

    const btn=document.createElement('button');
    btn.id=NAV_ID;
    btn.type='button';
    btn.innerHTML='<span style="display:inline-block;width:18px;text-align:center;margin-right:3px;font-size:15px">⇧</span> PLANO DE CARREIRA';
    btn.onclick=openCareer;

    const teamBtn=[...nav.querySelectorAll('button')].find(b=>normalize(b.textContent).includes('GESTAO DE EQUIPES'));
    if(teamBtn)teamBtn.insertAdjacentElement('afterend',btn);
    else nav.appendChild(btn);
  }

  function bootCareerNav(){
    ensureCareerNav();
    setTimeout(ensureCareerNav,100);
    setTimeout(ensureCareerNav,500);
    setTimeout(ensureCareerNav,1500);
  }

  /* A navegação é criada independentemente do módulo de carreira. */
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bootCareerNav,{once:true});
  else bootCareerNav();

  /* Sincronização cloud original permanece independente. */
  loadScript(ORIGINAL_SYNC,function(){
    console.info('[BOOT] Sincronização cloud original carregada.');
  },function(src){
    console.error('[BOOT] Falha na sincronização original:',src);
  });
})();
