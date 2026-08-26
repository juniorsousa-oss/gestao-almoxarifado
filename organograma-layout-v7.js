/* ORGANOGRAMA — layout corporativo compacto e menu lateral alinhado. */
(function(){
'use strict';

const STYLE_ID='org-corporate-v1-style';

function installStyle(){
  if(document.getElementById(STYLE_ID)) return;
  const s=document.createElement('style');
  s.id=STYLE_ID;
  s.textContent=`
/* ================= MENU LATERAL ================= */
.sidebar{width:245px!important;padding:25px 14px!important}
.sidebar .nav{display:flex!important;flex-direction:column!important;gap:5px!important;width:100%!important;padding:0!important}
.sidebar .nav button{
  position:relative!important;width:100%!important;height:46px!important;min-height:46px!important;
  margin:0!important;padding:0 12px 0 43px!important;border:1px solid transparent!important;
  border-radius:10px!important;background:transparent!important;text-align:left!important;
  display:flex!important;align-items:center!important;justify-content:flex-start!important;
  color:#dfe4e1!important;font-size:12px!important;font-weight:800!important;
  line-height:1!important;letter-spacing:.15px!important;white-space:nowrap!important;
}
.sidebar .nav button::before{
  content:'';position:absolute!important;left:13px!important;top:50%!important;
  transform:translateY(-50%)!important;width:20px!important;height:20px!important;
  display:flex!important;align-items:center!important;justify-content:center!important;
  font-family:Arial,sans-serif!important;font-size:14px!important;font-weight:700!important;
  line-height:20px!important;text-align:center!important;color:#aeb8b3!important;
}
.sidebar .nav button:nth-child(1)::before{content:'▦'}
.sidebar .nav button:nth-child(2)::before{content:'✎'}
.sidebar .nav button:nth-child(3)::before{content:'◷'}
.sidebar .nav button:nth-child(4)::before{content:'♙'}
.sidebar .nav button:nth-child(5)::before{content:'⇧'}
.sidebar .nav button:nth-child(6)::before{content:'⚙'}
.sidebar .nav button:hover{background:#171d1a!important;border-color:#29332f!important;color:#fff!important}
.sidebar .nav button.active{background:var(--yellow)!important;border-color:var(--yellow)!important;color:#111!important}
.sidebar .nav button.active::before{color:#111!important}

/* ================= ORGANOGRAMA ================= */
#equipes .free-org-area{
  position:relative!important;min-height:560px!important;max-height:650px!important;
  overflow:auto!important;padding:30px 24px 44px!important;
  background:linear-gradient(180deg,#0b100e 0%,#0e1411 100%)!important;
  border:1px solid #2d3833!important;border-radius:14px!important;
  scrollbar-color:#4b554f #101512!important;
}
#equipes .org-canvas{
  position:relative!important;width:max-content!important;min-width:100%!important;
  min-height:470px!important;padding:8px 18px 34px!important;box-sizing:border-box!important;
}
#equipes .org-svg{
  position:absolute!important;inset:0!important;width:100%!important;height:100%!important;
  pointer-events:none!important;z-index:1!important;overflow:visible!important;
}
#equipes .org-svg path{
  fill:none!important;stroke:#56625b!important;stroke-width:1.5!important;
  stroke-linecap:round!important;stroke-linejoin:round!important;vector-effect:non-scaling-stroke!important;
}
#equipes .org-tree{position:relative!important;z-index:2!important;width:max-content!important;margin:0 auto!important;display:flex!important;justify-content:center!important}
#equipes .org-level{display:flex!important;justify-content:center!important;align-items:flex-start!important;gap:18px!important;width:max-content!important}
#equipes .org-wrap{position:relative!important;display:flex!important;flex-direction:column!important;align-items:center!important;flex:0 0 auto!important}
#equipes .org-node{
  width:156px!important;min-width:156px!important;height:62px!important;min-height:62px!important;
  padding:8px 10px!important;box-sizing:border-box!important;
  display:flex!important;align-items:center!important;gap:9px!important;
  border:1px solid #344039!important;border-radius:10px!important;
  background:linear-gradient(145deg,#171e1b,#111714)!important;
  box-shadow:0 5px 15px rgba(0,0,0,.25)!important;cursor:grab!important;
  transition:transform .15s ease,border-color .15s ease,background .15s ease!important;
}
#equipes .org-node:hover{transform:translateY(-2px)!important;border-color:#737e77!important;background:#19211d!important}
#equipes .org-node.anchor{border-color:var(--yellow)!important;box-shadow:0 0 0 2px rgba(255,210,10,.10),0 7px 18px rgba(0,0,0,.30)!important}
#equipes .org-node.dragging{opacity:.35!important}
#equipes .org-photo{
  width:38px!important;height:38px!important;min-width:38px!important;min-height:38px!important;
  flex:0 0 38px!important;border-radius:50%!important;object-fit:cover!important;
  display:block!important;margin:0!important;border:1.5px solid var(--yellow)!important;background:#252d29!important;
}
#equipes .org-initials{display:grid!important;place-items:center!important;color:#fff!important;font-size:13px!important;font-weight:900!important}
#equipes .org-info{min-width:0!important;overflow:hidden!important;display:flex!important;flex-direction:column!important;justify-content:center!important;text-align:left!important}
#equipes .org-name{font-size:11px!important;line-height:1.15!important;font-weight:900!important;color:#f1f4f2!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}
#equipes .org-role{margin-top:4px!important;font-size:8px!important;line-height:1.15!important;font-weight:700!important;color:#89958e!important;text-transform:uppercase!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}
#equipes .org-children{display:flex!important;justify-content:center!important;align-items:flex-start!important;gap:18px!important;width:max-content!important;margin-top:46px!important}
#equipes .org-root-drop{height:20px!important;width:100%!important;margin-top:20px!important}
#equipes .org-empty{padding:150px 25px!important;color:#69746e!important;text-align:center!important;font-size:12px!important}
#equipes .org-caption{font-size:9px!important;color:#68736d!important;text-align:center!important;margin-top:18px!important;letter-spacing:.3px!important}
@media(max-width:900px){
 .sidebar{width:230px!important}.main{margin-left:230px!important;width:calc(100% - 230px)!important}
 #equipes .free-org-area{padding:25px 18px 40px!important}
 #equipes .org-level{gap:14px!important}#equipes .org-children{gap:14px!important}
}
@media(max-width:700px){
 .sidebar{width:100%!important;padding:18px!important}.main{margin-left:0!important;width:100%!important}
 .sidebar .nav{flex-direction:row!important;overflow-x:auto!important}.sidebar .nav button{min-width:165px!important}
 #equipes .org-node{width:145px!important;min-width:145px!important;height:58px!important;min-height:58px!important}
 #equipes .org-photo{width:34px!important;height:34px!important;min-width:34px!important;min-height:34px!important;flex-basis:34px!important}
}
`;
  document.head.appendChild(s);
}

function peopleMap(){
  return new Map((state.collaborators||[]).map(p=>[String(p.id),p]));
}
function orgData(){return freeOrgData();}
function childrenOf(id){
  const d=orgData(), parent=String(id||'');
  return d.order.filter(x=>d.selected.includes(String(x)) && String(d.parents[String(x)]||'')===parent);
}
function esc(v){return String(v??'').replace(/[&<>\'\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c]));}
function avatar(p){
  if(p?.photo) return `<img class="org-photo" src="${esc(p.photo)}" alt="">`;
  return `<div class="org-photo org-initials">${esc((p?.name||'?')[0])}</div>`;
}
function nodeHtml(id,map){
  const sid=String(id), p=map.get(sid); if(!p)return '';
  const kids=childrenOf(sid);
  const anchor=String(freeOrgAnchorId||'')===sid;
  const name=esc(p.name||'Colaborador');
  const role=esc(p.role||p.position||p.cargo||'');
  return `<div class="org-wrap" data-org-wrap="${esc(sid)}">
    <div class="org-node ${anchor?'anchor':''}" draggable="true" data-org-node-id="${esc(sid)}" title="Arraste para reorganizar — ${name}">
      ${avatar(p)}<div class="org-info"><div class="org-name">${name}</div>${role?`<div class="org-role">${role}</div>`:''}</div>
    </div>
    ${kids.length?`<div class="org-children">${kids.map(k=>nodeHtml(k,map)).join('')}</div>`:''}
  </div>`;
}
function drawConnectors(area){
  const canvas=area.querySelector('.org-canvas'), svg=area.querySelector('.org-svg');
  if(!canvas||!svg)return;
  const rect=canvas.getBoundingClientRect();
  const w=Math.max(canvas.scrollWidth,canvas.clientWidth),h=Math.max(canvas.scrollHeight,canvas.clientHeight);
  svg.setAttribute('width',w);svg.setAttribute('height',h);svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.innerHTML='';
  area.querySelectorAll('.org-wrap').forEach(wrap=>{
    const children=wrap.querySelector(':scope > .org-children');
    const parent=wrap.querySelector(':scope > .org-node');
    if(!children||!parent)return;
    const childNodes=[...children.querySelectorAll(':scope > .org-wrap > .org-node')];
    if(!childNodes.length)return;
    const pr=parent.getBoundingClientRect();
    const px=pr.left+pr.width/2-rect.left, py=pr.bottom-rect.top;
    const pts=childNodes.map(n=>{const r=n.getBoundingClientRect();return{x:r.left+r.width/2-rect.left,y:r.top-rect.top};});
    const rail=py+22;
    const path=document.createElementNS('http://www.w3.org/2000/svg','path');
    let d=`M ${px} ${py} V ${rail}`;
    if(pts.length===1)d+=` M ${px} ${rail} V ${pts[0].y}`;
    else{
      d+=` M ${pts[0].x} ${rail} H ${pts[pts.length-1].x}`;
      pts.forEach(p=>{d+=` M ${p.x} ${rail} V ${p.y}`;});
    }
    path.setAttribute('d',d);svg.appendChild(path);
  });
}
function render(){
  const area=document.getElementById('freeOrgArea'); if(!area)return;
  const map=peopleMap(),roots=childrenOf('');
  area.innerHTML=`<div class="org-canvas"><svg class="org-svg" aria-hidden="true"></svg><div class="org-tree">${roots.length?`<div class="org-level">${roots.map(id=>nodeHtml(id,map)).join('')}</div>`:`<div class="org-empty">Selecione os colaboradores para montar o organograma.</div>`}</div><div class="org-root-drop" data-org-root-drop="1"></div></div>`;
  bind();
  requestAnimationFrame(()=>requestAnimationFrame(()=>drawConnectors(area)));
}
function bind(){
  const area=document.getElementById('freeOrgArea');if(!area)return;
  area.querySelectorAll('[data-org-node-id]').forEach(node=>{
    node.addEventListener('dragstart',e=>{const id=String(node.dataset.orgNodeId||'');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',id);node.classList.add('dragging');});
    node.addEventListener('dragend',()=>node.classList.remove('dragging'));
    node.addEventListener('dragover',e=>{e.preventDefault();e.dataTransfer.dropEffect='move';});
    node.addEventListener('drop',e=>{
      e.preventDefault();
      const child=String(e.dataTransfer.getData('text/plain')||''),target=String(node.dataset.orgNodeId||'');
      if(!child||!target||child===target)return;
      if(wouldCreateFreeOrgCycle(child,target)){alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');return;}
      setFreeOrgParent(child,target);
    });
  });
  const root=area.querySelector('[data-org-root-drop="1"]');
  if(root){root.addEventListener('dragover',e=>e.preventDefault());root.addEventListener('drop',e=>{e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||'');if(child)setFreeOrgParent(child,'');});}
}

window.renderFreeOrg=render;
window.freeOrgDrop=function(e,targetId){
  e.preventDefault();const child=String(e.dataTransfer.getData('text/plain')||''),target=String(targetId||'');
  if(!child)return;if(!target){setFreeOrgParent(child,'');return}if(child===target)return;
  if(wouldCreateFreeOrgCycle(child,target)){alert('Essa relação criaria um ciclo na hierarquia. Escolha outro superior.');return}
  setFreeOrgParent(child,target);
};
window.addEventListener('resize',()=>{clearTimeout(window.__orgCorporateResize);window.__orgCorporateResize=setTimeout(()=>drawConnectors(document.getElementById('freeOrgArea')),120);});

const original=window.showView;
if(typeof original==='function'&&!window.__orgCorporatePatched){
  window.__orgCorporatePatched=true;
  window.showView=function(id,btn){const r=original.apply(this,arguments);if(id==='equipes')setTimeout(render,80);return r;};
}

installStyle();
render();
})();