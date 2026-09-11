/* ============================================================
   GESTÃO DE EQUIPES — CARREIRA COMO ABA INTERNA
   Mantém o módulo Plano de Carreira existente e apenas altera
   sua navegação/posição visual para dentro de Gestão de Equipes.
   ============================================================ */
(function(){
  'use strict';

  var STYLE_ID='equipesCareerTabStyle';
  var BTN_ID='equipesTabCarreira';
  var HOST_ID='equipesCareerHost';

  function installStyle(){
    if(document.getElementById(STYLE_ID)) return;
    var s=document.createElement('style');
    s.id=STYLE_ID;
    s.textContent=`
      /* O acesso antigo continua existindo para compatibilidade,
         mas não aparece mais no menu lateral. */
      #navCarreira{display:none!important;}

      #equipes .equipes-internal-nav{
        display:flex!important;
        align-items:center!important;
        gap:7px!important;
        flex-wrap:wrap!important;
        margin-bottom:13px!important;
      }

      #equipes .equipes-internal-nav .indicator-tab{
        cursor:pointer!important;
      }

      #equipes #${HOST_ID}{display:none;}
      #equipes.career-tab-active #${HOST_ID}{display:block;}
      #equipes #${HOST_ID} #carreira{display:block!important;}
      #equipes #${HOST_ID} #carreira .topbar{margin-top:0!important;}
    `;
    document.head.appendChild(s);
  }

  function getEquipes(){ return document.getElementById('equipes'); }

  function getInternalNav(){
    var e=getEquipes();
    return e ? (e.querySelector('.subnav') || e.querySelector('[class*="subnav"]')) : null;
  }

  function createHost(){
    var e=getEquipes();
    if(!e) return null;

    var host=document.getElementById(HOST_ID);
    if(!host){
      host=document.createElement('div');
      host.id=HOST_ID;
      var n=getInternalNav();
      if(n) n.insertAdjacentElement('afterend',host);
      else e.appendChild(host);
    }
    return host;
  }

  function setSidebarEquipesActive(){
    document.querySelectorAll('.sidebar .nav button').forEach(function(x){
      x.classList.remove('active');
    });

    var team=Array.prototype.slice.call(document.querySelectorAll('.sidebar .nav button')).find(function(x){
      var t=String(x.textContent||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase();
      return t.indexOf('GESTAO DE EQUIPES')>=0;
    });

    if(team) team.classList.add('active');
  }

  function activateCareer(){
    var e=getEquipes();
    var b=document.getElementById(BTN_ID);
    var host=createHost();
    if(!e || !b || !host) return;

    e.classList.add('career-tab-active');

    var n=getInternalNav();
    if(n){
      n.querySelectorAll('.indicator-tab').forEach(function(x){
        x.classList.remove('active');
      });
    }
    b.classList.add('active');

    /* O módulo original é chamado somente para garantir que seus dados,
       controles e renderização continuem sendo exatamente os mesmos. */
    var career=document.getElementById('carreira');
    if(!career){
      var oldButton=document.getElementById('navCarreira');
      if(oldButton && typeof oldButton.onclick==='function'){
        oldButton.onclick(new MouseEvent('click',{bubbles:false,cancelable:true}));
      }
    }

    setTimeout(function(){
      career=document.getElementById('carreira');
      if(!career) return;

      host.appendChild(career);
      career.classList.add('active');
      career.style.display='block';

      /* Mantém Gestão de Equipes como a tela principal. */
      document.querySelectorAll('.view').forEach(function(v){
        if(v!==e && v!==career) v.classList.remove('active');
      });
      e.classList.add('active');
      setSidebarEquipesActive();
    },120);
  }

  function leaveCareer(){
    var e=getEquipes();
    var b=document.getElementById(BTN_ID);
    if(!e) return;

    e.classList.remove('career-tab-active');
    if(b) b.classList.remove('active');

    var career=document.getElementById('carreira');
    if(career){
      career.classList.remove('active');
      career.style.display='';
    }
  }

  function install(){
    var e=getEquipes();
    var n=getInternalNav();
    var oldCareerButton=document.getElementById('navCarreira');

    if(!e || !n || !oldCareerButton) return false;

    installStyle();
    oldCareerButton.style.display='none';
    n.classList.add('equipes-internal-nav');

    if(!document.getElementById(BTN_ID)){
      var b=document.createElement('button');
      b.id=BTN_ID;
      b.type='button';
      b.className='indicator-tab';
      b.textContent='CARREIRA';
      b.addEventListener('click',function(ev){
        ev.preventDefault();
        ev.stopPropagation();
        activateCareer();
      });
      n.appendChild(b);
    }

    /* As outras abas retornam ao conteúdo normal da Gestão de Equipes. */
    n.querySelectorAll('.indicator-tab').forEach(function(t){
      if(t.id===BTN_ID) return;
      if(!t.dataset.careerHooked){
        t.dataset.careerHooked='1';
        t.addEventListener('click',function(){ leaveCareer(); });
      }
    });

    return true;
  }

  function boot(){
    if(install()) return;
    setTimeout(boot,150);
  }

  boot();
})();
