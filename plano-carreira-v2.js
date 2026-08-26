/* Plano de Carreira — carregador isolado + correção definitiva do menu */
(function(){
'use strict';
var CORE='https://raw.githubusercontent.com/juniorsousa-oss/gestao-almoxarifado/7896dc3e9a527219e3be31ac5c0b1b1a6e20cb01/plano-carreira-v2.js';
var STYLE_ID='cleanMainMenuOverride';
var CSS=`
/* MENU PRINCIPAL — uma única camada visual, sem duplicação de ícones */
.sidebar{width:245px!important;padding:25px 17px!important;background:#0a0d0c!important;border-right:1px solid #252c29!important}
.sidebar .brand{height:72px!important;margin:0 0 20px!important;display:flex!important;align-items:center!important;justify-content:center!important}
.sidebar .brand img{max-width:165px!important;max-height:58px!important;object-fit:contain!important;display:block!important}
.sidebar .nav{display:flex!important;flex-direction:column!important;gap:7px!important;padding:0!important}
.sidebar .nav button{box-sizing:border-box!important;width:100%!important;height:46px!important;min-height:46px!important;margin:0!important;padding:0 15px!important;border:0!important;border-radius:10px!important;background:transparent!important;color:#b9c0bd!important;text-align:left!important;font-size:13px!important;font-weight:800!important;line-height:1!important;display:flex!important;align-items:center!important;gap:11px!important;overflow:hidden!important;white-space:nowrap!important;box-shadow:none!important}
.sidebar .nav button:hover{background:#181e1b!important;color:#fff!important}
.sidebar .nav button.active{background:var(--yellow)!important;color:#111!important}
.sidebar .nav button:focus,.sidebar .nav button:focus-visible{outline:none!important;box-shadow:none!important}
.sidebar .nav button>span:first-child{display:none!important}
.sidebar .nav button>span:last-child{display:inline!important;min-width:0!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
.sidebar .nav button::before{display:inline-flex!important;flex:0 0 22px!important;width:22px!important;height:22px!important;align-items:center!important;justify-content:center!important;font-family:"Segoe UI Symbol","Segoe UI",Arial,sans-serif!important;font-size:17px!important;font-weight:400!important;line-height:1!important;color:currentColor!important}
.sidebar .nav button:nth-child(1)::before{content:'▦'}
.sidebar .nav button:nth-child(2)::before{content:'✎'}
.sidebar .nav button:nth-child(3)::before{content:'◷'}
.sidebar .nav button:nth-child(4)::before{content:'♧'}
.sidebar .nav button:nth-child(5)::before{content:'⚙'}
#navCarreira::before{content:'⇧'}
#navCarreira{font-size:13px!important;font-weight:800!important}
@media(max-width:1050px){.sidebar{width:210px!important}.main{margin-left:210px!important;width:calc(100% - 210px)!important}}
@media(max-width:700px){.sidebar{position:static!important;width:100%!important;height:auto!important}.main{margin:0!important;width:100%!important}.sidebar .nav{flex-direction:row!important;overflow:auto!important}.sidebar .nav button{flex:0 0 auto!important;width:auto!important;min-width:150px!important}}
`;
function apply(){
  var old=document.getElementById(STYLE_ID);if(old)old.remove();
  var s=document.createElement('style');s.id=STYLE_ID;s.textContent=CSS;document.head.appendChild(s);
}
function loadCore(){
  var s=document.createElement('script');
  s.src=CORE;s.async=false;
  s.onload=function(){apply();setTimeout(apply,100);setTimeout(apply,500)};
  s.onerror=function(){console.error('[Plano de Carreira] falha ao carregar modulo principal')};
  document.head.appendChild(s);
}
loadCore();
})();
