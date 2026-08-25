/* ============================================================
   ORGANOGRAMA V7 — layout hierárquico real
   Aplicar SOMENTE na aba Gestão de Equipes.
   Não altera Dashboard, indicadores ou gráficos.
   ============================================================ */
(function(){
  'use strict';

  const STYLE_ID='organograma-layout-v7-style';
  if(!document.getElementById(STYLE_ID)){
    const s=document.createElement('style');
    s.id=STYLE_ID;
    s.textContent=`
      #equipes .free-org-area{position:relative !important;min-height:430px !important;padding:28px 22px 42px !important;overflow:auto !important;background:#0d1210 !important;border:1px dashed #3c4842 !important;border-radius:12px !important}
      #equipes .org-v7-canvas{position:relative;width:max-content;min-width:100%;min-height:350px;margin:0 auto}
      #equipes .org-v7-svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible;z-index:0}
      #equipes .org-v7-tree{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;width:max-content;min-width:100%}
      #equipes .org-v7-level{display:flex;justify-content:center;align-items:flex-start;gap:54px;width:max-content}
      #equipes .org-v7-node-wrap{position:relative;display:flex;flex-direction:column;align-items:center;flex:0 0 auto}
      #equipes .org-v7-node{width:58px !important;height:58px !important;min-width:58px !important;min-height:58px !important;max-width:58px !important;max-height:58px !important;padding:3px !important;margin:0 !important;display:block !important;border:2px solid var(--yellow) !important;border-radius:50% !important;background:#151b18 !important;box-shadow:0 0 0 3px rgba(255,210,10,.06) !important;cursor:grab;user-select:none;position:relative;z-index:2}
      #equipes .org-v7-node:hover{transform:scale(1.045);box-shadow:0 0 0 4px rgba(255,210,10,.11) !important}
      #equipes .org-v7-node.dragging{opacity:.4;cursor:grabbing}
      #equipes .org-v7-node.selected-anchor{box-shadow:0 0 0 4px rgba(255,210,10,.20) !important}
      #equipes .org-v7-node .free-org-photo{width:50px !important;height:50px !important;min-width:50px !important;min-height:50px !important;max-width:50px !important;max-height:50px !important;margin:0 !important;border:0 !important;border-radius:50% !important;object-fit:cover !important;display:block !important}
      #equipes .org-v7-node .free-org-photo.initials{display:grid !important;place-items:center !important;background:#252d29 !important;color:#fff !important;font-size:22px !important;font-weight:900 !important}
      #equipes .org-v7-node .free-org-name,#equipes .org-v7-node .free-org-role,#equipes .org-v7-node .free-org-info,#equipes .org-v7-node .free-org-actions,#equipes .org-v7-node .free-org-drag{display:none !important}
      #equipes .org-v7-children{display:flex;justify-content:center;align-items:flex-start;gap:54px;margin-top:64px;width:max-content}
      #equipes .org-v7-root-list{display:flex;justify-content:center;align-items:flex-start;gap:54px;width:max-content}
      #equipes .org-v7-empty{padding:75px 20px;color:#66716c;text-align:center}
      #equipes .org-v7-root-drop{width:100%;min-height:24px}
      @media(max-width:700px){#equipes .free-org-area{padding:24px 12px 34px !important}#equipes .org-v7-level,#equipes .org-v7-children,#equipes .org-v7-root-list{gap:34px}#equipes .org-v7-node{width:52px !important;height:52px !important;min-width:52px !important;min-height:52px !important;max-width:52px !important;max-height:52px !important}#equipes .org-v7-node .free-org-photo{width:44px !important;height:44px !important;min-width:44px !important;min-height:44px !important;max-width:44px !important;max-height:44px !important}#equipes .org-v7-children{margin-top:58px}}
    `;
    document.head.appendChild(s);
  }
  function byIdMap(){return new Map((state.collaborators||[]).map(p=>[String(p.id),p]));}
  function childrenOf(id){const m=freeOrgData(),parent=String(id||'');return m.order.filter(x=>m.selected.includes(String(x))&&String(m.parents[String(x)]||'')===parent);}
  function avatar(p){return p?.photo?`<img class="free-org-photo" src="${p.photo}" alt="">`:`<div class="free-org-photo initials">${esc((p?.name||'?')[0])}</div>`;}
  function nodeHtml(id,map){const sid=String(id),p=map.get(sid);if(!p)return '';const kids=childrenOf(sid),anchor=String(freeOrgAnchorId||'')===sid;return `<div class="org-v7-node-wrap" data-org-id="${esc(sid)}"><div class="org-v7-node ${anchor?'selected-anchor':''}" draggable="true" data-org-node-id="${esc(sid)}" title="${esc(p.name||'Colaborador')}">${avatar(p)}</div>${kids.length?`<div class="org-v7-children">${kids.map(k=>nodeHtml(k,map)).join('')}</div>`:''}</div>`;}
  function render(){const area=document.getElementById('freeOrgArea');if(!area)return;const map=byIdMap(),roots=childrenOf('');area.innerHTML=`<div class="org-v7-canvas"><svg class="org-v7-svg" aria-hidden="true"></svg><div class="org-v7-tree">${roots.length?`<div class="org-v7-root-list">${roots.map(id=>nodeHtml(id,map)).join('')}</div>`:`<div class="org-v7-empty">Clique em uma foto dos colaboradores para adicioná-la ao organograma.</div>`}</div><div class="org-v7-root-drop" data-org-root-drop="1"></div></div>`;bindDragDrop();requestAnimationFrame(drawConnections);setTimeout(drawConnections,80);}
  function bindDragDrop(){const area=document.getElementById('freeOrgArea');if(!area)return;area.querySelectorAll('[data-org-node-id]').forEach(node=>{node.addEventListener('dragstart',e=>{const id=String(node.dataset.orgNodeId||'');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',id);node.classList.add('dragging');});node.addEventListener('dragend',()=>node.classList.remove('dragging'));node.addEventListener('dragover',e=>{e.preventDefault();e.dataTransfer.dropEffect='move';});node.addEventListener('drop',e=>{e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||''),target=String(node.dataset.orgNodeId||'');if(!child||!target||child===target)return;if(wouldCreateFreeOrgCycle(child,target)){alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');return;}setFreeOrgParent(child,target);});});const root=area.querySelector('[data-org-root-drop]');if(root){root.addEventListener('dragover',e=>{e.preventDefault();e.dataTransfer.dropEffect='move';});root.addEventListener('drop',e=>{e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||'');if(!child)return;setFreeOrgParent(child,'');});}}
  function drawConnections(){const area=document.getElementById('freeOrgArea'),canvas=area?.querySelector('.org-v7-canvas'),svg=canvas?.querySelector('.org-v7-svg');if(!area||!canvas||!svg)return;const rect=canvas.getBoundingClientRect(),width=Math.max(canvas.scrollWidth,rect.width),height=Math.max(canvas.scrollHeight,rect.height);svg.setAttribute('width',width);svg.setAttribute('height',height);svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.innerHTML='';canvas.querySelectorAll('.org-v7-node-wrap').forEach(parentWrap=>{const parentNode=parentWrap.querySelector(':scope > .org-v7-node'),children=parentWrap.querySelector(':scope > .org-v7-children');if(!parentNode||!children)return;const childNodes=[...children.querySelectorAll(':scope > .org-v7-node-wrap > .org-v7-node')];if(!childNodes.length)return;const pr=parentNode.getBoundingClientRect(),pcx=pr.left+pr.width/2-rect.left,pbottom=pr.bottom-rect.top,childRects=childNodes.map(n=>n.getBoundingClientRect()),cxs=childRects.map(r=>r.left+r.width/2-rect.left),ctop=Math.min(...childRects.map(r=>r.top-rect.top)),midY=pbottom+(ctop-pbottom)/2;addLine(svg,pcx,pbottom,pcx,midY);if(cxs.length>1)addLine(svg,Math.min(...cxs),midY,Math.max(...cxs),midY);cxs.forEach(cx=>addLine(svg,cx,midY,cx,ctop));});}
  function addLine(svg,x1,y1,x2,y2){const line=document.createElementNS('http://www.w3.org/2000/svg','line');line.setAttribute('x1',x1);line.setAttribute('y1',y1);line.setAttribute('x2',x2);line.setAttribute('y2',y2);line.setAttribute('stroke','#56615b');line.setAttribute('stroke-width','2');line.setAttribute('stroke-linecap','round');svg.appendChild(line);}
  window.renderFreeOrg=render;
  window.freeOrgDrop=function(e,targetId){e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||''),target=String(targetId||'');if(!child)return;const m=freeOrgData();if(!m.selected.includes(child))return;if(!target){setFreeOrgParent(child,'');return;}if(child===target)return;if(wouldCreateFreeOrgCycle(child,target)){alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');return;}setFreeOrgParent(child,target);};
  window.addEventListener('resize',()=>{clearTimeout(window.__orgV7ResizeTimer);window.__orgV7ResizeTimer=setTimeout(drawConnections,100);});
  if(window.ResizeObserver){const ro=new ResizeObserver(()=>drawConnections());const area=document.getElementById('freeOrgArea');if(area)ro.observe(area);}
  const originalShowView=window.showView;if(typeof originalShowView==='function'&&!window.__orgV7ShowViewPatched){window.__orgV7ShowViewPatched=true;window.showView=function(id,btn){const r=originalShowView.apply(this,arguments);if(id==='equipes')setTimeout(render,50);return r;};}
  render();
})();
