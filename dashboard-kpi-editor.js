/* EDITOR DOS CARDS DO DASHBOARD — módulo isolado.
   Não altera menu, Gestão de Equipes ou Plano de Carreira. */
(function(){
  'use strict';
  var PANEL_ID='dashboard-kpi-editor';

  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]});}
  function num(id,fallback){var e=document.getElementById(id),n=Number(e&&e.value);return Number.isFinite(n)?n:fallback;}

  function style(){
    if(document.getElementById('dashboard-kpi-editor-style'))return;
    var s=document.createElement('style');s.id='dashboard-kpi-editor-style';
    s.textContent='#'+PANEL_ID+' .kpi-editor-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}'+
      '#'+PANEL_ID+' .kpi-editor-group{padding:15px;border:1px solid #29332f;border-radius:10px;background:#0d1210}'+
      '#'+PANEL_ID+' .kpi-editor-group h4{margin:0 0 12px;font-size:11px;color:#fff;letter-spacing:.3px}'+
      '#'+PANEL_ID+' .kpi-editor-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:14px}'+
      '@media(max-width:700px){#'+PANEL_ID+' .kpi-editor-grid{grid-template-columns:1fr}}';
    document.head.appendChild(s);
  }

  function field(id,label,value,step){
    return '<div class="field"><label>'+esc(label)+'</label><input id="'+id+'" type="number" step="'+(step||'1')+'" value="'+esc(value==null?0:value)+'"></div>';
  }

  function currentAccuracy(){
    var ind=window.state&&state.indicators&&state.indicators.find(function(i){return String(i.id)==='acc'});
    if(!ind)return null;
    if(typeof window.current==='function')return current(ind);
    return (ind.records||[]).slice().sort(function(a,b){return String(a.date).localeCompare(String(b.date))}).slice(-1)[0]||null;
  }

  function ensurePanel(){
    var config=document.getElementById('config');
    if(!config||!window.state)return;
    var panel=document.getElementById(PANEL_ID);
    if(!panel){
      panel=document.createElement('div');
      panel.id=PANEL_ID;
      panel.className='panel';
      config.insertBefore(panel,config.firstElementChild||null);
    }
    var c=state.current||{};
    var r=currentAccuracy()||{value:c.acc||0,target:c.meta||0};
    panel.innerHTML='<div class="panel-head"><div><div class="panel-title">DADOS DOS CARDS DO DASHBOARD</div><div class="small-note">Edite os números exibidos no cabeçalho. O restante do aplicativo permanece intacto.</div></div></div>'+
      '<div class="kpi-editor-grid" style="margin-top:14px">'+
      '<div class="kpi-editor-group"><h4>01 · ACURÁCIA DE ESTOQUE</h4>'+field('kpiAccAjustes','AJUSTES REALIZADOS',c.ajustes,'1')+field('kpiAccItens','ITENS EM ESTOQUE',c.itens,'1')+field('kpiAccResultado','RESULTADO (%)',r.value,'.01')+field('kpiAccMeta','META (%)',r.target,'.01')+'</div>'+
      '<div class="kpi-editor-group"><h4>02 · ENTREGAS NO PRAZO</h4>'+field('kpiDelProgramados','PROGRAMADOS',c.prog,'1')+field('kpiDelAtendidos','ATENDIDOS 100%',c.atend,'1')+field('kpiDelSolicitacoes','SOLICITAÇÕES',c.solic,'1')+field('kpiDelDia','ENTREGUES EM DIA',c.dia,'1')+field('kpiDelProjetos','PROJETOS ATENDIDOS (%)',c.proj,'.01')+field('kpiDelDiaPct','ENTREGAS EM DIA (%)',c.diaPct,'.01')+'</div>'+
      '</div><div class="kpi-editor-actions"><button class="btn btn-primary" type="button" id="kpiEditorSave">SALVAR DADOS DO DASHBOARD</button></div>';
    document.getElementById('kpiEditorSave').onclick=save;
  }

  function save(){
    if(!window.state)return;
    state.current=state.current||{};
    state.current.ajustes=num('kpiAccAjustes',state.current.ajustes||0);
    state.current.itens=num('kpiAccItens',state.current.itens||0);
    state.current.prog=num('kpiDelProgramados',state.current.prog||0);
    state.current.atend=num('kpiDelAtendidos',state.current.atend||0);
    state.current.solic=num('kpiDelSolicitacoes',state.current.solic||0);
    state.current.dia=num('kpiDelDia',state.current.dia||0);
    state.current.proj=num('kpiDelProjetos',state.current.proj||0);
    state.current.diaPct=num('kpiDelDiaPct',state.current.diaPct||0);

    var ind=state.indicators&&state.indicators.find(function(i){return String(i.id)==='acc'});
    if(ind){
      ind.records=Array.isArray(ind.records)?ind.records:[];
      var r=currentAccuracy();
      if(!r){
        r={date:new Date().toISOString().slice(0,10),value:0,target:0};
        ind.records.push(r);
      }
      r.value=num('kpiAccResultado',r.value||0);
      r.target=num('kpiAccMeta',r.target||0);
      ind.target=r.target;
    }

    if(typeof window.save==='function'&&!window.save()){
      alert('Não foi possível salvar os dados do Dashboard.');
      return;
    }
    if(typeof window.render==='function')window.render();
    ensurePanel();
    var b=document.getElementById('kpiEditorSave');
    if(b){b.textContent='DADOS SALVOS';setTimeout(function(){var x=document.getElementById('kpiEditorSave');if(x)x.textContent='SALVAR DADOS DO DASHBOARD'},1400)}
  }

  function boot(){style();ensurePanel();}
  var oldShow=window.showView;
  if(typeof oldShow==='function'&&!window.__dashboardKpiEditorShowPatched){
    window.__dashboardKpiEditorShowPatched=true;
    window.showView=function(id,btn){var result=oldShow.apply(this,arguments);if(id==='config')setTimeout(ensurePanel,0);return result};
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
