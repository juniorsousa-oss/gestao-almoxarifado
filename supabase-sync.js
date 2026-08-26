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
  let careerAttempts=0;

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
    if(typeof window.openCareerModule==='function'){
      window.openCareerModule();
      return;
    }
    if(careerLoading)return;
    if(careerAttempts>=2){
      console.error('[CAREER] Módulo não registrou a navegação após 2 tentativas.');
      alert('Não foi possível abrir o Plano de Carreira. Atualize a página e tente novamente.');
      return;
    }

    careerLoading=true;
    careerAttempts++;
    loadScript(CAREER+'?boot='+careerAttempts+'&t='+Date.now(),function(){
      careerLoading=false;
      if(typeof window.openCareerModule==='function'){
        window.openCareerModule();
        return;
      }
      if(typeof window.renderCareerModule==='function'){
        window.renderCareerModule();
        return;
      }
      console.error('[CAREER] Arquivo carregado, mas a API do módulo não foi registrada.');
      setTimeout(function(){
        if(typeof window.openCareerModule==='function')window.openCareerModule();
        else if(typeof window.renderCareerModule==='function')window.renderCareerModule();
        else alert('O Plano de Carreira foi carregado, mas a navegação não foi registrada.');
      },100);
    },function(src){
      careerLoading=false;
      console.error('[CAREER] Falha ao carregar módulo:',src);
      if(careerAttempts<2)setTimeout(openCareer,250);
      else alert('Não foi possível carregar o Plano de Carreira.');
    });
  }

  function ensureCareerNav(){
    const nav=document.querySelector('.nav');
    if(!nav)return;

    let btn=document.getElementById(NAV_ID);
    if(!btn){
      btn=document.createElement('button');
      btn.id=NAV_ID;
      btn.type='button';
      btn.innerHTML='<span style="display:inline-block;width:18px;text-align:center;margin-right:3px;font-size:15px">⇧</span> PLANO DE CARREIRA';
      const teamBtn=[...nav.querySelectorAll('button')].find(b=>normalize(b.textContent).includes('GESTAO DE EQUIPES'));
      if(teamBtn)teamBtn.insertAdjacentElement('afterend',btn);
      else nav.appendChild(btn);
    }
    btn.onclick=openCareer;
  }

  function bootCareerNav(){
    ensureCareerNav();
    setTimeout(ensureCareerNav,100);
    setTimeout(ensureCareerNav,500);
    setTimeout(ensureCareerNav,1500);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bootCareerNav,{once:true});
  else bootCareerNav();

  loadScript(ORIGINAL_SYNC,function(){
    console.info('[BOOT] Sincronização cloud original carregada.');
  },function(src){
    console.error('[BOOT] Falha na sincronização cloud original:',src);
  });
})();
