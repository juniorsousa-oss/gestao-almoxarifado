/* ORGANOGRAMA V9 — visual profissional, fotos pequenas e hierarquia limpa. Mantém os dados e o arrastar/soltar. */
(function(){'use strict';
const STYLE_ID='organograma-layout-v9-style';
function installStyle(){if(document.getElementById(STYLE_ID))return;const s=document.createElement('style');s.id=STYLE_ID;s.textContent=`
/* MENU LATERAL — ícone e texto sempre no mesmo eixo */
.sidebar .nav{gap:6px!important;align-items:stretch!important}
.sidebar .nav button{width:100%!important;height:46px!important;min-height:46px!important;margin:0!important;padding:0 14px!important;border:1px solid transparent!important;border-radius:10px!important;display:flex!important;align-items:center!important;justify-content:flex-start!important;text-align:left!important;line-height:1!important;white-space:nowrap!important;overflow:hidden!important;font-size:0!important;gap:10px!important}
.sidebar .nav button::before{width:18px!important;min-width:18px!important;text-align:center!important;font-size:16px!important;line-height:1!important;display:block!important}
.sidebar .nav button::after{font-size:13px!important;font-weight:800!important;line-height:1!important;letter-spacing:.1px!important;display:block!important}
.sidebar .nav button:nth-child(1)::before{content:'▦'}.sidebar .nav button:nth-child(1)::after{content:'DASHBOARD'}
.sidebar .nav button:nth-child(2)::before{content:'✎'}.sidebar .nav button:nth-child(2)::after{content:'ALIMENTAR INDICADORES'}
.sidebar .nav button:nth-child(3)::before{content:'◷'}.sidebar .nav button:nth-child(3)::after{content:'HISTÓRICO'}
.sidebar .nav button:nth-child(4)::before{content:'♙'}.sidebar .nav button:nth-child(4)::after{content:'GESTÃO DE EQUIPES'}
.sidebar .nav button:nth-child(5)::before{content:'⇧'}.sidebar .nav button:nth-child(5)::after{content:'PLANO DE CARREIRA'}
.sidebar .nav button:nth-child(6)::before{content:'⚙'}.sidebar .nav button:nth-child(6)::after{content:'CONFIGURAÇÕES'}
.sidebar .nav button:hover{background:#181e1b!important;border-color:#2d3732!important;color:#fff!important}.sidebar .nav button.active{background:var(--yellow)!important;border-color:var(--yellow)!important;color:#111!important}

/* ORGANOGRAMA — árvore central, limpa, compacta */
#equipes .free-org-area{position:relative!important;min-height:520px!important;max-height:680px!important;overflow:auto!important;padding:36px 28px 44px!important;background:linear-gradient(180deg,#0b100e,#0d1210)!important;border:1px solid #29332f!important;border-radius:12px!important;display:block!important}
#equipes .org-v9-canvas{position:relative;width:max-content;min-width:100%;min-height:400px;margin:0 auto;padding:0 18px 28px}
#equipes .org-v9-tree{display:flex;justify-content:center;align-items:flex-start;width:100%}
#equipes .org-v9-node-wrap{position:relative;display:flex;flex-direction:column;align-items:center;flex:0 0 auto}
#equipes .org-v9-root-list{display:flex;justify-content:center;align-items:flex-start;gap:72px;width:max-content;margin:0 auto}
#equipes .org-v9-node{position:relative;z-index:2;width:54px!important;height:54px!important;min-width:54px!important;min-height:54px!important;padding:0!important;border:2px solid #68736d!important;border-radius:50%!important;background:#151b18!important;display:grid!important;place-items:center!important;box-shadow:0 5px 16px rgba(0,0,0,.30)!important;cursor:grab!important;transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease!important}
#equipes .org-v9-node:hover{transform:translateY(-2px) scale(1.04)!important;border-color:var(--yellow)!important;box-shadow:0 8px 22px rgba(0,0,0,.35)!important}
#equipes .org-v9-node.selected-anchor{border-color:var(--yellow)!important;box-shadow:0 0 0 3px rgba(255,210,10,.12),0 7px 20px rgba(0,0,0,.3)!important}
#equipes .org-v9-node.dragging{opacity:.35!important}
#equipes .org-v9-photo{width:48px!important;height:48px!important;min-width:48px!important;min-height:48px!important;border-radius:50%!important;object-fit:cover!important;display:block!important;border:0!important;margin:0!important;background:#252d29!important}
#equipes .org-v9-photo.initials{display:grid!important;place-items:center!important;color:#fff!important;font-size:16px!important;font-weight:900!important}
/* nomes/cargos não ocupam espaço: organograma é visual */
#equipes .org-v9-children{position:relative;display:flex;justify-content:center;align-items:flex-start;gap:42px;width:max-content;margin-top:42px;padding-top:28px}
#equipes .org-v9-children:before{content:'';position:absolute;top:0;left:50%;width:2px;height:28px;transform:translateX(-50%);background:#58645e}
#equipes .org-v9-children:after{content:'';position:absolute;top:28px;left:var(--first-center,0px);width:var(--children-span,0px);height:2px;background:#58645e}
#equipes .org-v9-children>.org-v9-node-wrap:before{content:'';position:absolute;top:-28px;left:50%;width:2px;height:28px;transform:translateX(-50%);background:#58645e;z-index:1}
#equipes .org-v9-empty{padding:110px 20px;color:#66716c;text-align:center;font-size:12px}
#equipes .org-v9-root-drop{height:30px;width:100%;margin-top:18px}
@media(max-width:900px){#equipes .free-org-area{min-height:480px;padding:30px 18px 38px!important}#equipes .org-v9-root-list{gap:52px}#equipes .org-v9-children{gap:30px}}
@media(max-width:700px){.sidebar .nav button{height:44px!important;min-height:44px!important}.sidebar .nav button::after{font-size:12px!important}#equipes .free-org-area{min-height:430px;padding:28px 12px 34px!important}#equipes .org-v9-root-list{gap:38px}#equipes .org-v9-children{gap:24px;margin-top:34px;padding-top:24px}#equipes .org-v9-children:before{height:24px}#equipes .org-v9-children:after{top:24px}#equipes .org-v9-children>.org-v9-node-wrap:before{top:-24px;height:24px}}
` ;document.head.appendChild(s)}
function mapPeople(){return new Map((state.collaborators||[]).map(p=>[String(p.id),p]))}
function data(){return freeOrgData()}
function childrenOf(id){const m=data(),p=String(id||'');return m.order.filter(x=>m.selected.includes(String(x))&&String(m.parents[String(x)]||'')===p)}
function avatar(p){return p?.photo?`<img class="org-v9-photo" src="${p.photo}" alt="">`:`<div class="org-v9-photo initials">${esc((p?.name||'?')[0])}</div>`}
function nodeHtml(id,map){const sid=String(id),p=map.get(sid);if(!p)return '';const kids=childrenOf(sid);const anchor=String(freeOrgAnchorId||'')===sid;return `<div class="org-v9-node-wrap" data-org-id="${esc(sid)}"><div class="org-v9-node ${anchor?'selected-anchor':''}" draggable="true" data-org-node-id="${esc(sid)}" title="Arraste para reorganizar — ${esc(p.name||'Colaborador')}">${avatar(p)}</div>${kids.length?`<div class="org-v9-children">${kids.map(k=>nodeHtml(k,map)).join('')}</div>`:''}</div>`}
function connector(el){el.querySelectorAll(':scope > .org-v9-children').forEach(c=>{const ns=[...c.querySelectorAll(':scope > .org-v9-node-wrap')];if(!ns.length)return;const centers=ns.map(n=>n.offsetLeft+n.offsetWidth/2);c.style.setProperty('--first-center',centers[0]+'px');c.style.setProperty('--children-span',Math.max(0,centers[centers.length-1]-centers[0])+'px')})}
function render(){const area=document.getElementById('freeOrgArea');if(!area)return;const map=mapPeople(),roots=childrenOf('');area.innerHTML=`<div class="org-v9-canvas"><div class="org-v9-tree">${roots.length?`<div class="org-v9-root-list">${roots.map(id=>nodeHtml(id,map)).join('')}</div>`:`<div class="org-v9-empty">Selecione os colaboradores para montar o organograma.</div>`}</div><div class="org-v9-root-drop" data-org-root-drop="1"></div></div>`;bind();requestAnimationFrame(()=>area.querySelectorAll('.org-v9-node-wrap').forEach(connector))}
function bind(){const area=document.getElementById('freeOrgArea');if(!area)return;area.querySelectorAll('[data-org-node-id]').forEach(node=>{node.addEventListener('dragstart',e=>{const id=String(node.dataset.orgNodeId||'');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',id);node.classList.add('dragging')});node.addEventListener('dragend',()=>node.classList.remove('dragging'));node.addEventListener('dragover',e=>{e.preventDefault();e.dataTransfer.dropEffect='move'});node.addEventListener('drop',e=>{e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||''),target=String(node.dataset.orgNodeId||'');if(!child||!target||child===target)return;if(wouldCreateFreeOrgCycle(child,target)){alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');return}setFreeOrgParent(child,target)})});const root=area.querySelector('[data-org-root-drop]');if(root){root.addEventListener('dragover',e=>{e.preventDefault()});root.addEventListener('drop',e=>{e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||'');if(child)setFreeOrgParent(child,'')})}}
window.renderFreeOrg=render;window.freeOrgDrop=function(e,targetId){e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||''),target=String(targetId||'');if(!child)return;if(!target){setFreeOrgParent(child,'');return}if(child===target)return;if(wouldCreateFreeOrgCycle(child,target)){alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');return}setFreeOrgParent(child,target)};
window.addEventListener('resize',()=>{clearTimeout(window.__orgV9Resize);window.__orgV9Resize=setTimeout(()=>{const a=document.getElementById('freeOrgArea');a?.querySelectorAll('.org-v9-node-wrap').forEach(connector)},100)});
const original=window.showView;if(typeof original==='function'&&!window.__orgV9Patched){window.__orgV9Patched=true;window.showView=function(id,btn){const r=original.apply(this,arguments);if(id==='equipes')setTimeout(render,60);return r}}
installStyle();render();
})();
