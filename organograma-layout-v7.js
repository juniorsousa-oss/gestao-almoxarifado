/* ============================================================
   ORGANOGRAMA V8 — hierarquia limpa e responsiva
   Aplicar SOMENTE na aba Gestão de Equipes.
   Não altera Dashboard, indicadores ou gráficos.
   Mantém os dados e as relações existentes do organograma.
   ============================================================ */
(function(){
  'use strict';

  const STYLE_ID='organograma-layout-v8-style';

  function installStyle(){
    if(document.getElementById(STYLE_ID)) return;
    const s=document.createElement('style');
    s.id=STYLE_ID;
    s.textContent=`
      /* ===== Navegação lateral: alinhamento profissional ===== */
      .sidebar .nav{gap:6px !important;align-items:stretch !important}
      .sidebar .nav button{
        width:100% !important;
        min-height:46px !important;
        height:46px !important;
        margin:0 !important;
        padding:0 14px !important;
        display:flex !important;
        align-items:center !important;
        justify-content:flex-start !important;
        text-align:left !important;
        white-space:nowrap !important;
        line-height:1 !important;
        border:1px solid transparent !important;
        border-radius:10px !important;
        transition:background .16s ease,border-color .16s ease,color .16s ease,transform .16s ease !important;
      }
      .sidebar .nav button:hover{background:#181e1b !important;border-color:#2c3531 !important;color:#fff !important}
      .sidebar .nav button.active{background:var(--yellow) !important;border-color:var(--yellow) !important;color:#111 !important;box-shadow:0 5px 14px rgba(255,210,10,.10) !important}
      .sidebar .nav button:focus-visible{outline:2px solid var(--yellow) !important;outline-offset:2px !important}

      /* ===== Área do organograma ===== */
      #equipes .free-org-area{
        position:relative !important;
        min-height:500px !important;
        padding:30px 20px 36px !important;
        overflow:auto !important;
        background:#0d1210 !important;
        border:1px dashed #3c4842 !important;
        border-radius:12px !important;
        scrollbar-color:#4b5751 #0b100e !important;
      }
      #equipes .free-org-area::-webkit-scrollbar{height:10px;width:10px}
      #equipes .free-org-area::-webkit-scrollbar-track{background:#0b100e;border-radius:10px}
      #equipes .free-org-area::-webkit-scrollbar-thumb{background:#46524c;border-radius:10px;border:2px solid #0b100e}
      #equipes .org-v8-canvas{position:relative;width:max-content;min-width:100%;min-height:420px;padding:4px 12px 28px}
      #equipes .org-v8-tree{position:relative;display:flex;justify-content:center;align-items:flex-start;width:max-content;min-width:100%}
      #equipes .org-v8-root-list{display:flex;justify-content:center;align-items:flex-start;gap:54px;width:max-content}
      #equipes .org-v8-node-wrap{position:relative;display:flex;flex-direction:column;align-items:center;flex:0 0 auto}
      #equipes .org-v8-node{
        position:relative;
        z-index:2;
        width:156px !important;
        min-width:156px !important;
        max-width:156px !important;
        min-height:112px !important;
        padding:12px 10px 10px !important;
        margin:0 !important;
        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:flex-start !important;
        border:1px solid #46524c !important;
        border-radius:12px !important;
        background:linear-gradient(145deg,#171e1b,#101513) !important;
        box-shadow:0 8px 22px rgba(0,0,0,.20) !important;
        cursor:grab;
        user-select:none;
        transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease !important;
      }
      #equipes .org-v8-node:hover{transform:translateY(-2px) !important;border-color:#727d77 !important;box-shadow:0 10px 26px rgba(0,0,0,.28) !important}
      #equipes .org-v8-node.dragging{opacity:.38;cursor:grabbing !important}
      #equipes .org-v8-node.selected-anchor{border-color:var(--yellow) !important;box-shadow:0 0 0 2px rgba(255,210,10,.14),0 10px 28px rgba(0,0,0,.28) !important}
      #equipes .org-v8-photo{
        width:56px !important;height:56px !important;min-width:56px !important;min-height:56px !important;
        border-radius:50% !important;object-fit:cover !important;display:block !important;
        border:2px solid var(--yellow) !important;background:#252d29 !important;
        margin:0 0 7px !important;
      }
      #equipes .org-v8-photo.initials{display:grid !important;place-items:center !important;color:#fff !important;font-size:19px !important;font-weight:900 !important}
      #equipes .org-v8-name{max-width:136px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#fff;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.2px;text-align:center}
      #equipes .org-v8-role{max-width:136px;margin-top:3px;color:#9da7a2;font-size:8.5px;line-height:1.25;text-align:center;min-height:21px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

      /* Conectores: cada pai gera uma linha vertical e uma barra horizontal somente sobre seus filhos. */
      #equipes .org-v8-children{
        position:relative;
        display:flex;
        justify-content:center;
        align-items:flex-start;
        gap:28px;
        margin-top:52px;
        padding-top:30px;
        width:max-content;
      }
      #equipes .org-v8-children:before{
        content:"";
        position:absolute;
        top:0;
        left:50%;
        width:2px;
        height:30px;
        transform:translateX(-50%);
        background:#56615b;
      }
      #equipes .org-v8-children:after{
        content:"";
        position:absolute;
        top:30px;
        left:calc(var(--first-center,0px));
        width:calc(var(--last-center,0px) - var(--first-center,0px));
        height:2px;
        background:#56615b;
      }
      #equipes .org-v8-children > .org-v8-node-wrap:before{
        content:"";
        position:absolute;
        top:-30px;
        left:50%;
        width:2px;
        height:30px;
        transform:translateX(-50%);
        background:#56615b;
        z-index:0;
      }
      #equipes .org-v8-root-list > .org-v8-node-wrap:not(:first-child){margin-left:0}
      #equipes .org-v8-empty{padding:100px 20px;color:#66716c;text-align:center;font-size:12px}
      #equipes .org-v8-root-drop{min-height:26px;width:100%;margin-top:18px}

      @media(max-width:900px){
        #equipes .org-v8-node{width:145px !important;min-width:145px !important}
        #equipes .org-v8-root-list{gap:34px}
        #equipes .org-v8-children{gap:20px}
      }
      @media(max-width:700px){
        .sidebar .nav button{min-height:44px !important;height:44px !important}
        #equipes .free-org-area{min-height:470px !important;padding:24px 12px 30px !important}
        #equipes .org-v8-node{width:132px !important;min-width:132px !important;padding:10px 8px 9px !important}
        #equipes .org-v8-photo{width:50px !important;height:50px !important;min-width:50px !important;min-height:50px !important}
        #equipes .org-v8-children{gap:16px;margin-top:46px;padding-top:26px}
        #equipes .org-v8-children:before{height:26px}
        #equipes .org-v8-children:after{top:26px}
        #equipes .org-v8-children > .org-v8-node-wrap:before{top:-26px;height:26px}
      }
    `;
    document.head.appendChild(s);
  }

  function byIdMap(){
    return new Map((state.collaborators||[]).map(p=>[String(p.id),p]));
  }

  function childrenOf(id){
    const m=freeOrgData(), parent=String(id||'');
    return m.order.filter(x=>m.selected.includes(String(x)) && String(m.parents[String(x)]||'')===parent);
  }

  function avatar(p){
    return p?.photo
      ? `<img class="org-v8-photo" src="${p.photo}" alt="">`
      : `<div class="org-v8-photo initials">${esc((p?.name||'?')[0])}</div>`;
  }

  function roleText(p){
    return String(p?.role||p?.cargo||p?.position||'').trim();
  }

  function nodeHtml(id,map){
    const sid=String(id), p=map.get(sid);
    if(!p) return '';
    const kids=childrenOf(sid);
    const anchor=String(freeOrgAnchorId||'')===sid;
    return `<div class="org-v8-node-wrap" data-org-id="${esc(sid)}">
      <div class="org-v8-node ${anchor?'selected-anchor':''}" draggable="true" data-org-node-id="${esc(sid)}" title="Arraste para reorganizar — ${esc(p.name||'Colaborador')}">
        ${avatar(p)}
        <div class="org-v8-name">${esc(p.name||'Colaborador')}</div>
        <div class="org-v8-role">${esc(roleText(p))}</div>
      </div>
      ${kids.length?`<div class="org-v8-children">${kids.map(k=>nodeHtml(k,map)).join('')}</div>`:''}
    </div>`;
  }

  function positionChildConnectorBar(parent){
    parent.querySelectorAll(':scope > .org-v8-children').forEach(children=>{
      const nodes=[...children.querySelectorAll(':scope > .org-v8-node-wrap')];
      if(!nodes.length) return;
      const centers=nodes.map(n=>n.offsetLeft + n.offsetWidth/2);
      const first=centers[0], last=centers[centers.length-1];
      children.style.setProperty('--first-center',first+'px');
      children.style.setProperty('--last-center',last+'px');
    });
  }

  function render(){
    const area=document.getElementById('freeOrgArea');
    if(!area) return;
    const map=byIdMap(), roots=childrenOf('');
    area.innerHTML=`<div class="org-v8-canvas"><div class="org-v8-tree">${roots.length
      ? `<div class="org-v8-root-list">${roots.map(id=>nodeHtml(id,map)).join('')}</div>`
      : `<div class="org-v8-empty">Clique em uma foto dos colaboradores para adicioná-la ao organograma.</div>`
    }</div><div class="org-v8-root-drop" data-org-root-drop="1"></div></div>`;
    bindDragDrop();
    requestAnimationFrame(()=>{
      area.querySelectorAll('.org-v8-node-wrap').forEach(positionChildConnectorBar);
    });
  }

  function bindDragDrop(){
    const area=document.getElementById('freeOrgArea');
    if(!area) return;
    area.querySelectorAll('[data-org-node-id]').forEach(node=>{
      node.addEventListener('dragstart',e=>{
        const id=String(node.dataset.orgNodeId||'');
        e.dataTransfer.effectAllowed='move';
        e.dataTransfer.setData('text/plain',id);
        node.classList.add('dragging');
      });
      node.addEventListener('dragend',()=>node.classList.remove('dragging'));
      node.addEventListener('dragover',e=>{
        e.preventDefault();
        e.dataTransfer.dropEffect='move';
      });
      node.addEventListener('drop',e=>{
        e.preventDefault();
        const child=String(e.dataTransfer.getData('text/plain')||''),target=String(node.dataset.orgNodeId||'');
        if(!child||!target||child===target) return;
        if(wouldCreateFreeOrgCycle(child,target)){
          alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');
          return;
        }
        setFreeOrgParent(child,target);
      });
    });
    const root=area.querySelector('[data-org-root-drop]');
    if(root){
      root.addEventListener('dragover',e=>{e.preventDefault();e.dataTransfer.dropEffect='move'});
      root.addEventListener('drop',e=>{
        e.preventDefault();
        const child=String(e.dataTransfer.getData('text/plain')||'');
        if(child) setFreeOrgParent(child,'');
      });
    }
  }

  window.renderFreeOrg=render;
  window.freeOrgDrop=function(e,targetId){
    e.preventDefault();
    const child=String(e.dataTransfer.getData('text/plain')||''),target=String(targetId||'');
    if(!child) return;
    const m=freeOrgData();
    if(!m.selected.includes(child)) return;
    if(!target){setFreeOrgParent(child,'');return;}
    if(child===target) return;
    if(wouldCreateFreeOrgCycle(child,target)){
      alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');
      return;
    }
    setFreeOrgParent(child,target);
  };

  window.addEventListener('resize',()=>{
    clearTimeout(window.__orgV8ResizeTimer);
    window.__orgV8ResizeTimer=setTimeout(()=>{
      const area=document.getElementById('freeOrgArea');
      area?.querySelectorAll('.org-v8-node-wrap').forEach(positionChildConnectorBar);
    },100);
  });

  const originalShowView=window.showView;
  if(typeof originalShowView==='function'&&!window.__orgV8ShowViewPatched){
    window.__orgV8ShowViewPatched=true;
    window.showView=function(id,btn){
      const r=originalShowView.apply(this,arguments);
      if(id==='equipes') setTimeout(render,50);
      return r;
    };
  }

  installStyle();
  render();
})();
