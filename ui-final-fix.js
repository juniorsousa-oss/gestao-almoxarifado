/* UI FINAL FIX — somente ajustes visuais solicitados */
(function(){
  'use strict';
  const STYLE='ui-final-fix-style';
  function css(){
    if(document.getElementById(STYLE))return;
    const s=document.createElement('style');s.id=STYLE;s.textContent=`
/* MENU: mesma coluna visual para todos os ícones */
.sidebar .nav button{position:relative!important;padding-left:43px!important;display:flex!important;align-items:center!important;min-height:46px!important;height:46px!important;line-height:1.15!important;white-space:normal!important}
.sidebar .nav button::before{left:11px!important;top:50%!important;transform:translateY(-50%)!important;width:22px!important;height:22px!important;line-height:22px!important;text-align:center!important}

/* ORGANOGRAMA: fotos pequenas, sem cartões gigantes, hierarquia limpa */
#equipes .free-org-area{min-height:500px!important;max-height:700px!important;overflow:auto!important;padding:38px 34px 50px!important;background:#0b100e!important;border:1px solid #303b35!important;border-radius:14px!important}
#equipes .org-canvas{position:relative!important;width:max-content!important;min-width:100%!important;min-height:430px!important;padding:10px 35px 40px!important}
#equipes .org-tree{position:relative!important;width:max-content!important;min-width:100%!important;margin:0 auto!important;display:flex!important;flex-direction:column!important;align-items:center!important}
#equipes .org-wrap{position:relative!important;width:max-content!important;min-width:0!important;display:flex!important;flex-direction:column!important;align-items:center!important;flex:0 0 auto!important}
#equipes .org-node{width:68px!important;min-width:68px!important;height:68px!important;min-height:68px!important;padding:4px!important;margin:0!important;border:2px solid #59645e!important;border-radius:50%!important;background:#141a17!important;display:grid!important;place-items:center!important;box-shadow:0 6px 18px rgba(0,0,0,.32)!important;cursor:grab!important;position:relative!important;z-index:3!important}
#equipes .org-node.root{border-color:var(--yellow)!important;box-shadow:0 0 0 4px rgba(255,210,10,.08),0 8px 20px rgba(0,0,0,.35)!important}
#equipes .org-node:hover{transform:translateY(-3px)!important;border-color:var(--yellow)!important}
#equipes .org-node img,#equipes .org-node .ge-avatar-fallback,#equipes .org-node .fallback,#equipes .org-photo{width:56px!important;height:56px!important;min-width:56px!important;min-height:56px!important;border-radius:50%!important;object-fit:cover!important;border:2px solid var(--yellow)!important;margin:0!important;display:block!important}
#equipes .org-node strong,#equipes .org-node small,#equipes .org-info,#equipes .org-name,#equipes .org-role{display:none!important}
#equipes .org-children{position:relative!important;display:flex!important;flex-direction:row!important;justify-content:center!important;align-items:flex-start!important;gap:42px!important;width:max-content!important;margin:42px 0 0!important;padding:34px 0 0!important}
#equipes .org-children::before{content:""!important;position:absolute!important;top:0!important;left:calc(50% - 1px)!important;width:2px!important;height:34px!important;background:#59645e!important}
#equipes .org-children::after{content:""!important;position:absolute!important;top:34px!important;left:calc(var(--first-x, 0px))!important;width:calc(var(--last-x, 0px) - var(--first-x, 0px))!important;height:2px!important;background:#59645e!important}
#equipes .org-child{position:relative!important;width:68px!important;min-width:68px!important;padding-top:0!important;display:flex!important;flex-direction:column!important;align-items:center!important}
#equipes .org-child::before{content:""!important;position:absolute!important;top:-34px!important;left:50%!important;width:2px!important;height:34px!important;transform:translateX(-50%)!important;background:#59645e!important}
#equipes .org-child>.org-children{margin-top:42px!important}
#equipes .org-connector{display:none!important}
#equipes .org-root-drop{height:24px!important;margin-top:18px!important}

/* EXPORTAR IMAGENS: bloco discreto no final da view */
.export-images-bottom{width:100%!important;display:flex!important;justify-content:flex-end!important;align-items:center!important;margin:30px 0 10px!important;padding-top:18px!important;border-top:1px solid #29332f!important}
.export-images-bottom button{min-width:260px!important;height:42px!important}
@media(max-width:700px){
 .sidebar .nav button{height:44px!important;min-height:44px!important}
 #equipes .free-org-area{padding:28px 16px 40px!important}
 #equipes .org-node{width:58px!important;height:58px!important;min-width:58px!important;min-height:58px!important}
 #equipes .org-node img,#equipes .org-node .ge-avatar-fallback,#equipes .org-node .fallback,#equipes .org-photo{width:48px!important;height:48px!important;min-width:48px!important;min-height:48px!important}
 #equipes .org-children{gap:24px!important}
 .export-images-bottom{justify-content:stretch!important}.export-images-bottom button{width:100%!important}
}
`;
    document.head.appendChild(s);
  }
  function moveExport(){
    const btn=[...document.querySelectorAll('button')].find(b=>b.textContent.trim().toUpperCase().includes('EXPORTAR IMAGENS'));
    if(!btn)return;
    const view=btn.closest('.view');if(!view)return;
    if(btn.closest('.export-images-bottom'))return;
    const box=document.createElement('div');box.className='export-images-bottom';
    box.appendChild(btn);view.appendChild(box);
  }
  function connectorVars(){
    document.querySelectorAll('#equipes .org-children').forEach(row=>{
      const kids=[...row.querySelectorAll(':scope > .org-child')];if(!kids.length)return;
      const a=kids.map(k=>k.offsetLeft+k.offsetWidth/2);row.style.setProperty('--first-x',a[0]+'px');row.style.setProperty('--last-x',a[a.length-1]+'px');
    });
  }
  function run(){css();moveExport();connectorVars();}
  const original=window.showView;
  if(typeof original==='function'&&!window.__uiFinalFixPatched){
    window.__uiFinalFixPatched=true;
    window.showView=function(){const r=original.apply(this,arguments);setTimeout(run,80);return r;};
  }
  new MutationObserver(()=>{moveExport();connectorVars();}).observe(document.body,{childList:true,subtree:true});
  window.addEventListener('resize',()=>{clearTimeout(window.__uiFinalResize);window.__uiFinalResize=setTimeout(connectorVars,120)});
  setTimeout(run,100);
})();
