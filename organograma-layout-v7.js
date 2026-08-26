/* ORGANOGRAMA V10 — layout corporativo, hierarquia limpa e menu sem ícones duplicados. */
(function(){'use strict';
const STYLE_ID='organograma-layout-v10-style';
function installStyle(){
 if(document.getElementById(STYLE_ID)) return;
 const s=document.createElement('style'); s.id=STYLE_ID; s.textContent=`
/* MENU — uma única camada de ícone */
.sidebar .nav{gap:6px!important;align-items:stretch!important}
.sidebar .nav button{width:100%!important;height:46px!important;min-height:46px!important;margin:0!important;padding:0 14px!important;border:1px solid transparent!important;border-radius:10px!important;display:flex!important;align-items:center!important;justify-content:flex-start!important;text-align:left!important;line-height:1!important;white-space:nowrap!important;overflow:hidden!important;font-size:0!important;gap:10px!important;position:relative!important}
.sidebar .nav button > *{font-size:0!important}
.sidebar .nav button::before{width:18px!important;min-width:18px!important;text-align:center!important;font-size:16px!important;line-height:1!important;display:block!important}
.sidebar .nav button::after{font-size:13px!important;font-weight:800!important;line-height:1!important;letter-spacing:.1px!important;display:block!important}
.sidebar .nav button:nth-child(1)::before{content:'▦'}.sidebar .nav button:nth-child(1)::after{content:'DASHBOARD'}
.sidebar .nav button:nth-child(2)::before{content:'✎'}.sidebar .nav button:nth-child(2)::after{content:'ALIMENTAR INDICADORES'}
.sidebar .nav button:nth-child(3)::before{content:'◷'}.sidebar .nav button:nth-child(3)::after{content:'HISTÓRICO'}
.sidebar .nav button:nth-child(4)::before{content:'♙'}.sidebar .nav button:nth-child(4)::after{content:'GESTÃO DE EQUIPES'}
.sidebar .nav button:nth-child(5)::before{content:'⇧'}.sidebar .nav button:nth-child(5)::after{content:'PLANO DE CARREIRA'}
.sidebar .nav button:nth-child(6)::before{content:'⚙'}.sidebar .nav button:nth-child(6)::after{content:'CONFIGURAÇÕES'}
.sidebar .nav button:hover{background:#181e1b!important;border-color:#2d3732!important;color:#fff!important}.sidebar .nav button.active{background:var(--yellow)!important;border-color:var(--yellow)!important;color:#111!important}

/* ORGANOGRAMA — estrutura corporativa */
#equipes .free-org-area{position:relative!important;min-height:560px!important;max-height:720px!important;overflow:auto!important;padding:38px 34px 54px!important;background:linear-gradient(180deg,#0a0f0d 0%,#0d1310 100%)!important;border:1px solid #2b3530!important;border-radius:14px!important;display:block!important}
#equipes .org-v10-canvas{position:relative;width:max-content;min-width:100%;min-height:460px;margin:0 auto;padding:4px 24px 36px;box-sizing:border-box}
#equipes .org-v10-tree{display:flex;justify-content:center;align-items:flex-start;width:100%}
#equipes .org-v10-root-list{display:flex;justify-content:center;align-items:flex-start;gap:54px;width:max-content;margin:0 auto}
#equipes .org-v10-node-wrap{position:relative;display:flex;flex-direction:column;align-items:center;flex:0 0 auto}
#equipes .org-v10-node{position:relative;z-index:3;width:190px!important;min-width:190px!important;height:76px!important;min-height:76px!important;padding:10px 12px!important;box-sizing:border-box!important;border:1px solid #35413b!important;border-radius:12px!important;background:#141a17!important;display:flex!important;align-items:center!important;gap:11px!important;box-shadow:0 7px 18px rgba(0,0,0,.28)!important;cursor:grab!important;transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease!important}
#equipes .org-v10-node:hover{transform:translateY(-2px)!important;border-color:#77847c!important;box-shadow:0 10px 24px rgba(0,0,0,.36)!important}
#equipes .org-v10-node.selected-anchor{border-color:var(--yellow)!important;box-shadow:0 0 0 3px rgba(255,210,10,.10),0 9px 24px rgba(0,0,0,.34)!important}
#equipes .org-v10-node.dragging{opacity:.38!important}
#equipes .org-v10-photo{width:50px!important;height:50px!important;min-width:50px!important;min-height:50px!important;border-radius:50%!important;object-fit:cover!important;display:block!important;border:2px solid #5f6b64!important;margin:0!important;background:#252d29!important;flex:0 0 50px!important}
#equipes .org-v10-photo.initials{display:grid!important;place-items:center!important;color:#fff!important;font-size:17px!important;font-weight:900!important}
#equipes .org-v10-info{min-width:0!important;display:flex!important;flex-direction:column!important;justify-content:center!important;align-items:flex-start!important;text-align:left!important;overflow:hidden!important}
#equipes .org-v10-name{font-size:13px!important;font-weight:850!important;line-height:1.2!important;color:#f2f5f3!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;max-width:105px!important}
#equipes .org-v10-role{margin-top:5px!important;font-size:10px!important;font-weight:650!important;line-height:1.2!important;color:#89958e!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;max-width:105px!important}
/* ligação pai -> nível */
#equipes .org-v10-children{position:relative;display:flex;justify-content:center;align-items:flex-start;gap:30px;width:max-content;margin-top:54px;padding-top:34px}
#equipes .org-v10-children:before{content:'';position:absolute;top:0;left:50%;width:2px;height:34px;transform:translateX(-50%);background:#59655e;z-index:1}
#equipes .org-v10-children:after{content:'';position:absolute;top:34px;left:var(--first-center,0px);width:var(--children-span,0px);height:2px;background:#59655e;z-index:1}
#equipes .org-v10-children>.org-v10-node-wrap:before{content:'';position:absolute;top:-34px;left:50%;width:2px;height:34px;transform:translateX(-50%);background:#59655e;z-index:1}
#equipes .org-v10-root-drop{height:26px;width:100%;margin-top:22px}
#equipes .org-v10-empty{padding:150px 20px;color:#68736d;text-align:center;font-size:12px}
@media(max-width:900px){#equipes .free-org-area{min-height:520px;padding:30px 22px 44px!important}#equipes .org-v10-root-list{gap:34px}#equipes .org-v10-children{gap:22px}}
@media(max-width:700px){.sidebar .nav button{height:44px!important;min-height:44px!important}#equipes .free-org-area{min-height:470px;padding:26px 14px 36px!important}#equipes .org-v10-node{width:170px!important;min-width:170px!important;height:70px!important;min-height:70px!important}#equipes .org-v10-photo{width:46px!important;height:46px!important;min-width:46px!important;min-height:46px!important;flex-basis:46px!important}#equipes .org-v10-root-list{gap:24px}#equipes .org-v10-children{gap:18px;margin-top:44px;padding-top:28px}#equipes .org-v10-children:before{height:28px}#equipes .org-v10-children:after{top:28px}#equipes .org-v10-children>.org-v10-node-wrap:before{top:-28px;height:28px}}
`; document.head.appendChild(s);
}
function mapPeople(){return new Map((state.collaborators||[]).map(p=>[String(p.id),p]))}
function data(){return freeOrgData()}
function childrenOf(id){const m=data(),p=String(id||'');return m.order.filter(x=>m.selected.includes(String(x))&&String(m.parents[String(x)]||'')===p)}
function esc(v){return String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]) )}
function avatar(p){return p?.photo?`<img class="org-v10-photo" src="${esc(p.photo)}" alt="">`:`<div class="org-v10-photo initials">${esc((p?.name||'?')[0])}</div>`}
function nodeHtml(id,map){const sid=String(id),p=map.get(sid);if(!p)return '';const kids=childrenOf(sid);const anchor=String(freeOrgAnchorId||'')===sid;const name=esc(p.name||'Colaborador');const role=esc(p.role||p.position||p.cargo||'');return `<div class="org-v10-node-wrap" data-org-id="${esc(sid)}"><div class="org-v10-node ${anchor?'selected-anchor':''}" draggable="true" data-org-node-id="${esc(sid)}" title="Arraste para reorganizar — ${name}">${avatar(p)}<div class="org-v10-info"><div class="org-v10-name">${name}</div>${role?`<div class="org-v10-role">${role}</div>`:''}</div></div>${kids.length?`<div class="org-v10-children">${kids.map(k=>nodeHtml(k,map)).join('')}</div>`:''}</div>`}
function connector(el){el.querySelectorAll(':scope > .org-v10-children').forEach(c=>{const ns=[...c.querySelectorAll(':scope > .org-v10-node-wrap')];if(!ns.length)return;const centers=ns.map(n=>n.offsetLeft+n.offsetWidth/2);c.style.setProperty('--first-center',centers[0]+'px');c.style.setProperty('--children-span',Math.max(0,centers[centers.length-1]-centers[0])+'px')})}
function render(){const area=document.getElementById('freeOrgArea');if(!area)return;const map=mapPeople(),roots=childrenOf('');area.innerHTML=`<div class="org-v10-canvas"><div class="org-v10-tree">${roots.length?`<div class="org-v10-root-list">${roots.map(id=>nodeHtml(id,map)).join('')}</div>`:`<div class="org-v10-empty">Selecione os colaboradores para montar o organograma.</div>`}</div><div class="org-v10-root-drop" data-org-root-drop="1"></div></div>`;bind();requestAnimationFrame(()=>area.querySelectorAll('.org-v10-node-wrap').forEach(connector))}
function bind(){const area=document.getElementById('freeOrgArea');if(!area)return;area.querySelectorAll('[data-org-node-id]').forEach(node=>{node.addEventListener('dragstart',e=>{const id=String(node.dataset.orgNodeId||'');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',id);node.classList.add('dragging')});node.addEventListener('dragend',()=>node.classList.remove('dragging'));node.addEventListener('dragover',e=>{e.preventDefault();e.dataTransfer.dropEffect='move'});node.addEventListener('drop',e=>{e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||''),target=String(node.dataset.orgNodeId||'');if(!child||!target||child===target)return;if(wouldCreateFreeOrgCycle(child,target)){alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');return}setFreeOrgParent(child,target)})});const root=area.querySelector('[data-org-root-drop]');if(root){root.addEventListener('dragover',e=>{e.preventDefault()});root.addEventListener('drop',e=>{e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||'');if(child)setFreeOrgParent(child,'')})}}
window.renderFreeOrg=render;window.freeOrgDrop=function(e,targetId){e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||''),target=String(targetId||'');if(!child)return;if(!target){setFreeOrgParent(child,'');return}if(child===target)return;if(wouldCreateFreeOrgCycle(child,target)){alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');return}setFreeOrgParent(child,target)};
window.addEventListener('resize',()=>{clearTimeout(window.__orgV10Resize);window.__orgV10Resize=setTimeout(()=>{const a=document.getElementById('freeOrgArea');a?.querySelectorAll('.org-v10-node-wrap').forEach(connector)},100)});
const original=window.showView;if(typeof original==='function'&&!window.__orgV10Patched){window.__orgV10Patched=true;window.showView=function(id,btn){const r=original.apply(this,arguments);if(id==='equipes')setTimeout(render,60);return r}}
installStyle();render();
})();
