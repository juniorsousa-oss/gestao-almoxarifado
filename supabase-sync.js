/* Loader de compatibilidade — sincronização cloud original + fallback seguro do Plano de Carreira.
   O módulo principal continua sendo carregado diretamente pelo index.html.
   Este arquivo NÃO substitui o módulo e NÃO o carrega em duplicidade.
*/
(function(){
  'use strict';

  const ORIGINAL_SYNC='https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/85378684a950f306e1880dd3df6cb8fc7ac0178c/supabase-sync.js';
  const CAREER='./plano-carreira-v2.js';
  let fallbackLoading=false;

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

  function ensureCareerNav(){
    const nav=document.querySelector('.nav');
    if(!nav)return false;

    let btn=document.getElementById('navCarreira');
    if(!btn){
      btn=document.createElement('button');
      btn.id='navCarreira';
      btn.type='button';
      btn.innerHTML='PLANO DE CARREIRA';
      const teamBtn=Array.from(nav.querySelectorAll('button')).find(b=>normalize(b.textContent).includes('GESTAO DE EQUIPES'));
      if(teamBtn)teamBtn.insertAdjacentElement('afterend',btn);
      else nav.appendChild(btn);
    }

    btn.onclick=function(){
      if(typeof window.openCareerModule==='function'){
        window.openCareerModule();
        return;
      }
      if(fallbackLoading)return;
      fallbackLoading=true;
      loadScript(CAREER+'?fallback='+Date.now(),function(){
        fallbackLoading=false;
        if(typeof window.openCareerModule==='function')window.openCareerModule();
        else if(typeof window.renderCareerModule==='function')window.renderCareerModule();
        else alert('Não foi possível inicializar o Plano de Carreira.');
      },function(){
        fallbackLoading=false;
        alert('Não foi possível carregar o Plano de Carreira.');
      });
    };
    return true;
  }

  function installProfessionalSidebar(){
    if(document.getElementById('professional-sidebar-v2'))return;
    const style=document.createElement('style');
    style.id='professional-sidebar-v2';
    style.textContent=`
      .sidebar{width:264px!important;padding:26px 14px 18px!important;background:#090c0b!important;border-right:1px solid #222a26!important;box-shadow:8px 0 30px rgba(0,0,0,.10)!important}
      .brand{height:78px!important;margin:0 8px 24px!important;padding:0!important;justify-content:center!important;border-bottom:1px solid rgba(255,255,255,.055)}
      .brand img{max-width:168px!important;max-height:60px!important}.placeholder{font-size:34px!important}
      .nav{display:flex!important;flex-direction:column!important;gap:5px!important;width:100%!important}
      .nav button{position:relative!important;width:100%!important;min-height:48px!important;height:48px!important;margin:0!important;padding:0 14px!important;display:grid!important;grid-template-columns:30px minmax(0,1fr)!important;align-items:center!important;column-gap:8px!important;border:1px solid transparent!important;border-radius:10px!important;background:transparent!important;color:#b9c1bd!important;text-align:left!important;font-size:12px!important;font-weight:800!important;letter-spacing:.15px!important;line-height:1!important;white-space:nowrap!important;overflow:hidden!important;transition:background .16s ease,color .16s ease,transform .16s ease!important}
      .nav button:hover{background:#151b18!important;color:#f5f7f6!important;transform:translateX(1px)!important}
      .nav button.active{background:#ffd20a!important;color:#111!important;border-color:#ffd20a!important;box-shadow:0 6px 18px rgba(255,210,10,.13)!important}
      .nav button .menu-icon{width:30px!important;height:30px!important;display:grid!important;place-items:center!important;color:#aeb8b3!important}.nav button.active .menu-icon{color:#111!important}
      .nav button .menu-icon svg{width:17px!important;height:17px!important;display:block!important;stroke:currentColor!important;fill:none!important;stroke-width:1.8!important;stroke-linecap:round!important;stroke-linejoin:round!important}
      .nav button .menu-label{min-width:0!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
      .sidebar-footer{margin-top:auto!important;padding:12px 10px 4px!important;color:#59625e!important}
      @media(max-width:1050px){.sidebar{width:224px!important}.main{margin-left:224px!important;width:calc(100% - 224px)!important}}
      @media(max-width:700px){.sidebar{width:100%!important;padding:16px!important}.brand{margin-bottom:12px!important}.nav{flex-direction:row!important;overflow-x:auto!important;gap:5px!important}.nav button{min-width:160px!important}}
    `;
    document.head.appendChild(style);

    const icons={
      'DASHBOARD':'<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
      'ALIMENTAR INDICADORES':'<svg viewBox="0 0 24 24"><path d="M5 19 19 5"/><path d="m14 5 5 5"/><path d="M4 20h4"/></svg>',
      'HISTÓRICO':'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/></svg>',
      'GESTÃO DE EQUIPES':'<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3"/><path d="M6 20c.7-3.3 2.7-5 6-5s5.3 1.7 6 5"/><path d="M5 11H3m18 0h-2"/></svg>',
      'PLANO DE CARREIRA':'<svg viewBox="0 0 24 24"><path d="M12 20V5"/><path d="m7 10 5-5 5 5"/><path d="M7 20h10"/></svg>',
      'CONFIGURAÇÕES':'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.4-2.3.9a8 8 0 0 0-1.7-1L14.5 3h-5l-.4 2.9a8 8 0 0 0-1.7 1L5.1 6.1l-2 3.4L5.1 11a7 7 0 0 0 0 2l-2 1.5 2 3.4 2.3-.9a8 8 0 0 0 1.7 1l.4 2.9h5l.4-2.9a8 8 0 0 0 1.7-1l2.3.9 2-3.4-2-1.5c.1-.3.1-.7.1-1Z"/></svg>'
    };

    function normalizeLabel(text){
      return normalize(String(text||'').replace(/[\u{1F300}-\u{1FAFF}\u2600-\u27BF]/gu,'').replace(/\s+/g,' '));
    }
    function formatButton(btn){
      if(!btn||btn.dataset.menuV2==='1')return;
      const label=normalizeLabel(btn.textContent);
      const key=Object.keys(icons).find(k=>label===normalize(k)||label.includes(normalize(k)));
      if(!key)return;
      btn.dataset.menuV2='1';
      btn.setAttribute('aria-label',key);
      btn.innerHTML='<span class="menu-icon">'+icons[key]+'</span><span class="menu-label">'+key+'</span>';
    }
    function apply(){
      const nav=document.querySelector('.nav');
      if(!nav)return false;
      ensureCareerNav();
      nav.querySelectorAll('button').forEach(formatButton);
      return true;
    }
    apply();setTimeout(apply,50);setTimeout(apply,300);setTimeout(apply,1000);setTimeout(apply,2500);
  }

  function bootCareerFallback(){
    ensureCareerNav();
    installProfessionalSidebar();
    setTimeout(ensureCareerNav,250);
    setTimeout(ensureCareerNav,1000);
    setTimeout(ensureCareerNav,2500);
  }

  loadScript(ORIGINAL_SYNC,function(){console.info('[BOOT] Sincronização cloud original carregada.');},function(src){console.error('[BOOT] Falha na sincronização cloud original:',src);});

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bootCareerFallback,{once:true});
  else bootCareerFallback();
})();
