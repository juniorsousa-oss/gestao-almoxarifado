/* UI V2 — somente visual do menu e organograma */
(function(){
'use strict';
var STYLE='ui-v2-style';
function installCss(){
 if(document.getElementById(STYLE))return;
 var s=document.createElement('style');s.id=STYLE;s.textContent=`
/* MENU */
.sidebar .nav{gap:6px!important;align-items:stretch!important}
.sidebar .nav button{position:relative!important;width:100%!important;height:46px!important;min-height:46px!important;margin:0!important;padding:0 12px 0 44px!important;border:1px solid transparent!important;border-radius:10px!important;display:flex!important;align-items:center!important;justify-content:flex-start!important;text-align:left!important;line-height:1.1!important;box-sizing:border-box!important;font-size:13px!important;white-space:nowrap!important}
.sidebar .nav button .ui-v2-icon{position:absolute!important;left:12px!important;top:50%!important;transform:translateY(-50%)!important;width:20px!important;height:20px!important;display:grid!important;place-items:center!important;font-size:15px!important;line-height:20px!important;font-weight:900!important}
.sidebar .nav button .ui-v2-label{display:block!important;min-width:0!important;line-height:1.15!important}
.sidebar .nav button:hover{background:#181e1b!important;border-color:#2d3732!important}
.sidebar .nav button.active{background:var(--yellow)!important;border-color:var(--yellow)!important;color:#111!important}

/* ORGANOGRAMA: somente fotos pequenas; SVG desenha os conectores com base na posição real */
#equipes .free-org-area{position:relative!important;min-height:470px!important;max-height:760px!important;overflow:auto!important;padding:30px 20px 44px!important;background:#0b100e!important;border:1px solid #303b35!important;border-radius:14px!important;box-sizing:border-box!important}
#equipes .ui-v2-stage{position:relative!important;width:max-content!important;min-width:100%!important;min-height:420px!important;padding:8px 80px 50px!important;box-sizing:border-box!important}
#equipes .ui-v2-svg{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;pointer-events:none!important;overflow:visible!important;z-index:0!important}
#equipes .ui-v2-line{fill:none!important;stroke:#56615b!important;stroke-width:1.7!important;vector-effect:non-scaling-stroke!important}
#equipes .ui-v2-tree{position:relative!important;z-index:1!important;width:max-content!important;min-width:100%!important;display:flex!important;flex-direction:column!important;align-items:center!important}
#equipes .ui-v2-row{display:flex!important;justify-content:center!important;align-items:flex-start!important;gap:82px!important;width:max-content!important}
#equipes .ui-v2-wrap{position:relative!important;width:60px!important;min-width:60px!important;display:flex!important;flex-direction:column!important;align-items:center!important;flex:0 0 60px!important}
#equipes .ui-v2-photo{width:56px!important;height:56px!important;min-width:56px!important;min-height:56px!important;padding:0!important;margin:0!important;border:2px solid var(--yellow)!important;border-radius:50%!important;object-fit:cover!important;background:#151b18!important;display:grid!important;place-items:center!important;box-shadow:0 0 0 3px rgba(255,210,10,.05),0 5px 14px rgba(0,0,0,.28)!important;cursor:grab!important;user-select:none!important;transition:transform .14s ease,box-shadow .14s ease!important}
#equipes .ui-v2-photo:hover{transform:scale(1.05)!important;box-shadow:0 0 0 4px rgba(255,210,10,.14)!important}
#equipes .ui-v2-photo.initials{color:#fff!important;font-weight:900!important;font-size:17px!important}
#equipes .ui-v2-subtree{display:flex!important;flex-direction:column!important;align-items:center!important;margin-top:48px!important;width:max-content!important}
#equipes .ui-v2-subrow{display:flex!important;align-items:flex-start!important;justify-content:center!important;gap:82px!important;width:max-content!important}
#equipes .ui-v2-name{display:none!important}
#equipes .ui-v2-empty{padding:90px 20px!important;color:#66716c!important;text-align:center!important;font-size:11px!important}
@media(max-width:900px){#equipes .ui-v2-row,#equipes .ui-v2-subrow{gap:54px!important}#equipes .ui-v2-stage{padding-left:44px!important;padding-right:44px!important}}
@media(max-width:700px){.sidebar .nav button{height:44px!important;min-height:44px!important;padding-left:40px!important}.sidebar .nav button .ui-v2-icon{left:10px!important}#equipes .free-org-area{padding:24px 10px 36px!important}#equipes .ui-v2-row,#equipes .ui-v2-subrow{gap:38px!important}#equipes .ui-v2-stage{padding-left:24px!important;padding-right:24px!important}#equipes .ui-v2-wrap{width:54px!important;min-width:54px!important}#equipes .ui-v2-photo{width:50px!important;height:50px!important;min-width:50px!important;min-height:50px!important}}
`;
 document.head.appendChild(s);
}
function fixMenu(){
 var map={navDashboard:'▦',navFeed:'✎',navHistory:'◷',navTeams:'♙',navCarreira:'⇧',navConfig:'⚙'};
 Object.keys(map).forEach(function(id){var b=document.getElementById(id);if(!b)return;var i=b.querySelector('.ui-v2-icon');if(!i){i=document.createElement('span');i.className='ui-v2-icon';i.setAttribute('aria-hidden','true');b.insertBefore(i,b.firstChild)}i.textContent=map[id];var l=b.querySelector('.ui-v2-label');if(!l){l=document.createElement('span');l.className='ui-v2-label';var txt='';Array.prototype.forEach.call(b.childNodes,function(n){if(n.nodeType===3)txt+=' '+n.nodeValue});txt=txt.replace(/[\s▦✎◷♙⇧⚙☷›>]+/g,' ').trim();l.textContent=txt||'MENU';b.appendChild(l)}});
}
function getData(){if(typeof freeOrgData!=='function'||typeof state==='undefined')return null;var m=freeOrgData(),by=new Map((state.collaborators||[]).map(function(p){return[String(p.id),p]}));return{m:m,by:by}}
function children(m,id){return m.order.filter(function(x){return m.selected.includes(String(x))&&String(m.parents[String(x)]||'')===String(id||'')})}
function avatar(p){return p&&p.photo?'<img class="ui-v2-photo" src="'+esc(p.photo)+'" alt="">':'<div class="ui-v2-photo initials">'+esc((p&&p.name||'?')[0])+'</div>'}
function build(id,d,seen){var sid=String(id),p=d.by.get(sid);if(!p||seen.has(sid))return '';var n=new Set(seen);n.add(sid);var ch=children(d.m,sid);return '<div class="ui-v2-wrap" data-ui-v2-id="'+esc(sid)+'" title="'+esc(p.name||'Colaborador')+'">'+avatar(p)+(ch.length?'<div class="ui-v2-subtree"><div class="ui-v2-subrow">'+ch.map(function(x){return build(x,d,n)}).join('')+'</div></div>':'')+'</div>'}
function render(){var area=document.getElementById('freeOrgArea'),d=getData();if(!area||!d)return;var roots=children(d.m,'');if(!roots.length){area.innerHTML='<div class="ui-v2-stage"><div class="ui-v2-empty">Clique em uma foto acima para adicionar o primeiro gestor.</div></div>';return}area.innerHTML='<div class="ui-v2-stage"><svg class="ui-v2-svg" aria-hidden="true"></svg><div class="ui-v2-tree"><div class="ui-v2-row">'+roots.map(function(x){return build(x,d,new Set())}).join('')+'</div></div></div>';requestAnimationFrame(drawLines)}
function drawLines(){var area=document.getElementById('freeOrgArea'),stage=area&&area.querySelector('.ui-v2-stage'),svg=stage&&stage.querySelector('.ui-v2-svg');if(!stage||!svg)return;var rect=stage.getBoundingClientRect(),w=Math.max(stage.scrollWidth,stage.clientWidth),h=Math.max(stage.scrollHeight,stage.clientHeight);svg.setAttribute('width',w);svg.setAttribute('height',h);svg.setAttribute('viewBox','0 0 '+w+' '+h);svg.innerHTML='';var d=getData(),nodes=Array.prototype.slice.call(stage.querySelectorAll('.ui-v2-wrap[data-ui-v2-id]')),by=new Map(nodes.map(function(n){return[String(n.dataset.uiV2Id),n]}));if(!d)return;function c(n){var r=n.getBoundingClientRect();return{x:r.left-rect.left+r.width/2,top:r.top-rect.top,bottom:r.bottom-rect.top}}function line(v){var p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('class','ui-v2-line');p.setAttribute('d',v);svg.appendChild(p)}nodes.forEach(function(n){var pid=String(d.m.parents[String(n.dataset.uiV2Id)]||'');if(!pid)return;var pn=by.get(pid);if(!pn)return;var a=c(pn),b=c(n),mid=a.bottom+(b.top-a.bottom)/2;line('M '+a.x+' '+a.bottom+' V '+mid+' H '+b.x+' V '+b.top)})}
function bindDrag(){var area=document.getElementById('freeOrgArea');if(!area||area.dataset.uiV2Drag==='1')return;area.dataset.uiV2Drag='1';area.addEventListener('dragstart',function(e){var p=e.target.closest('.ui-v2-photo');if(!p)return;var w=p.closest('.ui-v2-wrap');if(!w)return;e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',w.dataset.uiV2Id);p.style.opacity='.4'});area.addEventListener('dragend',function(e){var p=e.target.closest('.ui-v2-photo');if(p)p.style.opacity='1'});area.addEventListener('dragover',function(e){if(e.target.closest('.ui-v2-photo'))e.preventDefault()});area.addEventListener('drop',function(e){var p=e.target.closest('.ui-v2-photo');if(!p)return;e.preventDefault();var w=p.closest('.ui-v2-wrap'),child=e.dataTransfer.getData('text/plain'),parent=w&&w.dataset.uiV2Id;if(!child||!parent||child===parent)return;if(typeof wouldCreateFreeOrgCycle==='function'&&wouldCreateFreeOrgCycle(child,parent))return;if(typeof setFreeOrgParent==='function')setFreeOrgParent(child,parent)})}
function refresh(){installCss();fixMenu();render();bindDrag()}
var oldRender=window.renderFreeOrg;if(typeof oldRender==='function'&&!window.__uiV2Render){window.__uiV2Render=true;window.renderFreeOrg=function(){refresh()}}
var oldShow=window.showView;if(typeof oldShow==='function'&&!window.__uiV2Show){window.__uiV2Show=true;window.showView=function(){var r=oldShow.apply(this,arguments);setTimeout(refresh,80);return r}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(refresh,150)});else setTimeout(refresh,150);
window.addEventListener('resize',function(){clearTimeout(window.__uiV2Resize);window.__uiV2Resize=setTimeout(drawLines,100)});
})();
