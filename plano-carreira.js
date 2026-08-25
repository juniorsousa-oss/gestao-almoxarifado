/* PLANO DE CARREIRA — módulo integrado ao estado global */
(function(){
  'use strict';

  const STYLE_ID='career-module-style';
  const VIEW_ID='carreira';
  const NAV_ID='navCarreira';

  const css = `
  #carreira{display:none}
  #carreira.active{display:block}
  #carreira .career-grid{display:grid;grid-template-columns:1.1fr 1.9fr;gap:14px}
  #carreira .career-card{background:linear-gradient(145deg,#141a17,#101513);border:1px solid #35403b;border-radius:15px;padding:16px}
  #carreira .career-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
  #carreira .career-kpi{background:#111715;border:1px solid #29332f;border-radius:12px;padding:14px}
  #carreira .career-kpi span{display:block;color:#9aa39f;font-size:10px;font-weight:800;text-transform:uppercase}
  #carreira .career-kpi strong{display:block;font-size:25px;margin-top:8px}
  #carreira .career-kpi.good strong{color:#72e6a0}
  #carreira .career-kpi.warn strong{color:#ffd20a}
  #carreira .career-head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px}
  #carreira .career-head h2{margin:0;font-size:15px}
  #carreira .career-muted{color:#9aa39f;font-size:11px;line-height:1.45}
  #carreira .career-plan-list{display:flex;flex-direction:column;gap:8px}
  #carreira .career-plan{padding:11px;border:1px solid #29332f;border-radius:10px;background:#0d1210;cursor:pointer}
  #carreira .career-plan.active{border-color:#ffd20a;background:#151b18}
  #carreira .career-plan-title{font-weight:900;font-size:12px}
  #carreira .career-plan-meta{font-size:10px;color:#9aa39f;margin-top:4px}
  #carreira .career-req{display:grid;grid-template-columns:28px 1fr auto;gap:9px;align-items:center;padding:9px;border:1px solid #29332f;border-radius:9px;background:#0d1210;margin-bottom:7px}
  #carreira .career-req-num{width:25px;height:25px;border-radius:50%;display:grid;place-items:center;background:#202824;color:#ffd20a;font-size:10px;font-weight:900}
  #carreira .career-req-title{font-size:11px;font-weight:800}
  #carreira .career-req-type{font-size:9px;color:#7f8984;margin-top:2px}
  #carreira .career-row{display:grid;grid-template-columns:40px minmax(170px,1fr) 130px 90px;gap:9px;align-items:center;padding:9px;border:1px solid #29332f;border-radius:9px;background:#0d1210;margin-bottom:7px}
  #carreira .career-row .avatar{width:36px;height:36px}
  #carreira .career-person{font-size:11px;font-weight:900}
  #carreira .career-person small{display:block;color:#9aa39f;font-weight:500;margin-top:2px}
  #carreira .career-progress{height:7px;background:#252d29;border-radius:99px;overflow:hidden}
  #carreira .career-progress div{height:100%;background:#ffd20a;border-radius:99px}
  #carreira .career-status{padding:5px 7px;border-radius:6px;font-size:9px;font-weight:900;text-align:center}
  #carreira .career-status.ok{background:rgba(85,214,138,.12);color:#72e6a0}
  #carreira .career-status.warn{background:rgba(255,210,10,.1);color:#ffd20a}
  #carreira .career-status.bad{background:rgba(255,107,107,.1);color:#ff9999}
  #carreira .career-toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  #carreira .career-select,#carreira .career-input{background:#0c110f;color:#f5f5f5;border:1px solid #3a4540;border-radius:8px;padding:9px;font-size:11px;outline:none}
  #carreira .career-select{min-width:220px}
  #carreira .career-empty{padding:35px;text-align:center;color:#69736e;font-size:11px}
  #careerAssessmentModal .career-assessment-grid{display:grid;grid-template-columns:1fr;gap:8px}
  #careerAssessmentModal .assessment-item{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:10px;border:1px solid #29332f;border-radius:9px;background:#0d1210}
  #careerAssessmentModal .assessment-label{font-size:11px;font-weight:800}
  #careerAssessmentModal .assessment-label small{display:block;color:#89938e;margin-top:3px;font-weight:500}
  #careerAssessmentModal .assessment-btn{border:1px solid #424b46;background:#171d1a;color:#bbb;border-radius:7px;padding:7px 10px;font-size:10px;font-weight:800}
  #careerAssessmentModal .assessment-btn.ok{background:rgba(85,214,138,.12);border-color:#55d68a;color:#72e6a0}
  @media(max-width:1050px){#carreira .career-grid{grid-template-columns:1fr}#carreira .career-kpis{grid-template-columns:repeat(2,1fr)}}
  @media(max-width:700px){#carreira .career-kpis{grid-template-columns:1fr 1fr}#carreira .career-row{grid-template-columns:40px 1fr}.career-row .career-progress,.career-row .career-status{grid-column:2}}
  `;

  function ensureStyle(){
    if(document.getElementById(STYLE_ID))return;
    const s=document.createElement('style');s.id=STYLE_ID;s.textContent=css;document.head.appendChild(s);
  }

  function esc(v){
    return String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  }
  function uid(prefix='cr'){return prefix+'_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8)}

  function data(){
    state.career=state.career||{};
    state.career.plans=Array.isArray(state.career.plans)?state.career.plans:[];
    state.career.assessments=state.career.assessments||{};
    return state.career;
  }
  function people(){return Array.isArray(state.collaborators)?state.collaborators:[]}
  function getPerson(id){return people().find(p=>String(p.id)===String(id))}
  function activePlan(){
    const d=data();
    return d.plans.find(p=>String(p.id)===String(window.__careerPlanId))||d.plans[0]||null;
  }
  function statusFor(person,plan){
    if(!plan||!plan.requirements?.length)return {pct:0,ok:false,done:0,total:0};
    const a=data().assessments[String(person.id)]?.[String(plan.id)]||{};
    const total=plan.requirements.length;
    const done=plan.requirements.filter(r=>a[String(r.id)]===true).length;
    return {pct:Math.round(done/total*100),ok:done===total,done,total};
  }
  function persist(){
    if(typeof save==='function') save();
    else if(typeof window.syncCloudNow==='function') window.syncCloudNow();
  }

  function addNav(){
    const nav=document.querySelector('.nav');
    if(!nav||document.getElementById(NAV_ID))return;
    const b=document.createElement('button');
    b.id=NAV_ID;b.type='button';b.textContent='PLANO DE CARREIRA';
    b.onclick=()=>openModule();
    nav.appendChild(b);
  }

  function addView(){
    const main=document.querySelector('.main');
    if(!main||document.getElementById(VIEW_ID))return;
    const v=document.createElement('section');
    v.id=VIEW_ID;v.className='view';
    main.appendChild(v);
  }

  function openModule(){
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
    const v=document.getElementById(VIEW_ID);
    if(!v)return;
    v.classList.add('active');
    document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));
    document.getElementById(NAV_ID)?.classList.add('active');
    render();
    window.scrollTo({top:0,behavior:'smooth'});
  }

  function render(){
    ensureStyle();addNav();addView();
    const v=document.getElementById(VIEW_ID);
    if(!v)return;
    const d=data(),plan=activePlan();
    const all=people();
    const stats=plan?all.map(p=>statusFor(p,plan)):[];
    const aptos=stats.filter(x=>x.ok).length;
    const andamento=stats.filter(x=>x.done>0&&!x.ok).length;
    const sem=stats.filter(x=>x.done===0).length;
    v.innerHTML=`
      <div class="topbar">
        <div class="title"><h1>PLANO DE CARREIRA</h1><p>Defina os pré-requisitos de promoção e acompanhe a prontidão de cada colaborador.</p></div>
        <div class="actions"><button class="btn btn-primary" onclick="careerNewPlan()">+ NOVO PLANO</button></div>
      </div>
      <div class="career-kpis">
        <div class="career-kpi"><span>PLANOS</span><strong>${d.plans.length}</strong></div>
        <div class="career-kpi good"><span>APTOS</span><strong>${aptos}</strong></div>
        <div class="career-kpi warn"><span>EM DESENVOLVIMENTO</span><strong>${andamento}</strong></div>
        <div class="career-kpi"><span>SEM AVALIAÇÃO</span><strong>${sem}</strong></div>
      </div>
      <div class="career-grid">
        <div class="career-card">
          <div class="career-head"><div><h2>TRILHAS DE PROMOÇÃO</h2><div class="career-muted">Crie uma trilha por cargo ou função.</div></div></div>
          <div class="career-plan-list">
            ${d.plans.length?d.plans.map(p=>`
              <div class="career-plan ${plan&&String(plan.id)===String(p.id)?'active':''}" onclick="careerSelectPlan('${p.id}')">
                <div class="career-plan-title">${esc(p.name)}</div>
                <div class="career-plan-meta">${esc(p.currentRole||'Cargo atual')} → ${esc(p.targetRole||'Cargo destino')} · ${p.requirements.length} requisito(s)</div>
              </div>`).join(''):`<div class="career-empty">Nenhum plano cadastrado.<br>Comece criando o primeiro.</div>`}
          </div>
        </div>
        <div class="career-card">
          ${plan?renderPlan(plan):`<div class="career-empty">Selecione ou crie um plano de carreira.</div>`}
        </div>
      </div>`;
  }

  function renderPlan(plan){
    return `
      <div class="career-head">
        <div><h2>${esc(plan.name)}</h2><div class="career-muted">${esc(plan.currentRole||'')} → <strong>${esc(plan.targetRole||'')}</strong></div></div>
        <div class="career-toolbar"><button class="btn btn-small" onclick="careerEditPlan('${plan.id}')">EDITAR</button><button class="btn btn-small btn-danger" onclick="careerDeletePlan('${plan.id}')">EXCLUIR</button></div>
      </div>
      ${plan.description?`<div class="notice">${esc(plan.description)}</div>`:''}
      <div class="career-head"><div><h2>PRÉ-REQUISITOS</h2><div class="career-muted">Todos os requisitos abaixo são obrigatórios para considerar o colaborador apto.</div></div><button class="btn btn-primary btn-small" onclick="careerAddRequirement('${plan.id}')">+ REQUISITO</button></div>
      ${plan.requirements.length?plan.requirements.map((r,i)=>`
        <div class="career-req"><div class="career-req-num">${i+1}</div><div><div class="career-req-title">${esc(r.label)}</div><div class="career-req-type">${esc(r.type||'Critério')}</div></div><button class="btn btn-small btn-danger" onclick="careerRemoveRequirement('${plan.id}','${r.id}')">REMOVER</button></div>`).join(''):`<div class="career-empty">Adicione os pré-requisitos para esta promoção.</div>`}
      <div class="career-head" style="margin-top:18px"><div><h2>PRONTIDÃO DOS COLABORADORES</h2><div class="career-muted">Use AVALIAR para marcar o que já foi cumprido.</div></div><select class="career-select" onchange="careerFilterPeople(this.value"><option value="all">TODOS OS COLABORADORES</option><option value="apt">APTOS</option><option value="dev">EM DESENVOLVIMENTO</option><option value="none">SEM AVALIAÇÃO</option></select></div>
      <div id="careerPeopleRows">${renderPeopleRows(plan,'all')}</div>`;
  }

  function renderPeopleRows(plan,filter){
    const all=people();
    if(!all.length)return `<div class="career-empty">Nenhum colaborador cadastrado na Gestão de Equipe.</div>`;
    return all.map(p=>{
      const s=statusFor(p,plan);
      if(filter==='apt'&&!s.ok)return '';
      if(filter==='dev'&&!(s.done>0&&!s.ok))return '';
      if(filter==='none'&&s.done!==0)return '';
      const img=p.photo||p.foto||p.image||p.imagem||'';
      const avatar=img?`<div class="avatar"><img src="${esc(img)}"></div>`:`<div class="avatar">${esc((p.name||'?').slice(0,1).toUpperCase())}</div>`;
      return `<div class="career-row">${avatar}<div class="career-person">${esc(p.name||'SEM NOME')}<small>${esc(p.role||p.funcao||'')}</small></div><div><div class="career-progress"><div style="width:${s.pct}%"></div></div><div class="career-muted" style="margin-top:4px">${s.done}/${s.total} requisitos</div></div><div><div class="career-status ${s.ok?'ok':s.done?'warn':'bad'}">${s.ok?'APTO':s.done?'EM DESENV.':'NÃO AVALIADO'}</div><button class="btn btn-small" style="margin-top:5px;width:100%" onclick="careerAssess('${p.id}','${plan.id}')">AVALIAR</button></div></div>`;
    }).join('')||`<div class="career-empty">Nenhum colaborador encontrado.</div>`;
  }

  window.careerSelectPlan=function(id){window.__careerPlanId=id;render()}
  window.careerFilterPeople=function(filter){const p=activePlan(),el=document.getElementById('careerPeopleRows');if(p&&el)el.innerHTML=renderPeopleRows(p,filter)}

  function openModal(id,title,body,actions){
    let m=document.getElementById(id);
    if(!m){m=document.createElement('div');m.className='modal';m.id=id;document.body.appendChild(m)}
    m.innerHTML=`<div class="modal-box"><div class="modal-head"><h3>${title}</h3><button class="close" onclick="document.getElementById('${id}').classList.remove('open')">×</button></div>${body}<div class="modal-actions">${actions}</div></div>`;
    m.classList.add('open');return m;
  }

  window.careerNewPlan=function(){
    openModal('careerPlanModal','NOVO PLANO DE CARREIRA',`<div class="form-grid"><div class="field"><label>NOME DO PLANO</label><input id="cpName" placeholder="Ex.: Almoxarife I → Almoxarife II"></div><div class="field"><label>CARGO ATUAL</label><input id="cpCurrent" placeholder="Ex.: Almoxarife I"></div><div class="field"><label>CARGO DE DESTINO</label><input id="cpTarget" placeholder="Ex.: Almoxarife II"></div><div class="field full"><label>DESCRIÇÃO</label><textarea id="cpDesc" placeholder="Objetivo e escopo da promoção"></textarea></div></div>`,`<button class="btn" onclick="document.getElementById('careerPlanModal').classList.remove('open')">CANCELAR</button><button class="btn btn-primary" onclick="careerSavePlan()">CRIAR PLANO</button>`);
  }
  window.careerSavePlan=function(){const name=document.getElementById('cpName')?.value.trim();if(!name)return alert('Informe o nome do plano.');const d=data();const p={id:uid('plan'),name,currentRole:document.getElementById('cpCurrent').value.trim(),targetRole:document.getElementById('cpTarget').value.trim(),description:document.getElementById('cpDesc').value.trim(),requirements:[]};d.plans.push(p);window.__careerPlanId=p.id;persist();document.getElementById('careerPlanModal').classList.remove('open');render()}
  window.careerEditPlan=function(id){const p=data().plans.find(x=>String(x.id)===String(id));if(!p)return;openModal('careerPlanModal','EDITAR PLANO',`<div class="form-grid"><div class="field"><label>NOME DO PLANO</label><input id="cpName" value="${esc(p.name)}"></div><div class="field"><label>CARGO ATUAL</label><input id="cpCurrent" value="${esc(p.currentRole||'')}"></div><div class="field"><label>CARGO DE DESTINO</label><input id="cpTarget" value="${esc(p.targetRole||'')}"></div><div class="field full"><label>DESCRIÇÃO</label><textarea id="cpDesc">${esc(p.description||'')}</textarea></div></div>`,`<button class="btn" onclick="document.getElementById('careerPlanModal').classList.remove('open')">CANCELAR</button><button class="btn btn-primary" onclick="careerUpdatePlan('${p.id}')">SALVAR</button>`)}
  window.careerUpdatePlan=function(id){const p=data().plans.find(x=>String(x.id)===String(id));if(!p)return;p.name=document.getElementById('cpName').value.trim()||p.name;p.currentRole=document.getElementById('cpCurrent').value.trim();p.targetRole=document.getElementById('cpTarget').value.trim();p.description=document.getElementById('cpDesc').value.trim();persist();document.getElementById('careerPlanModal').classList.remove('open');render()}
  window.careerDeletePlan=function(id){if(!confirm('Excluir este plano e suas avaliações?'))return;const d=data();d.plans=d.plans.filter(p=>String(p.id)!==String(id));Object.keys(d.assessments).forEach(pid=>{if(d.assessments[pid])delete d.assessments[pid][String(id)]});window.__careerPlanId=d.plans[0]?.id||null;persist();render()}
  window.careerAddRequirement=function(planId){openModal('careerReqModal','NOVO PRÉ-REQUISITO',`<div class="form-grid"><div class="field"><label>TIPO</label><select id="crType"><option>EXPERIÊNCIA</option><option>COMPETÊNCIA</option><option>CURSO / CERTIFICAÇÃO</option><option>ESCOLARIDADE</option><option>DESEMPENHO</option><option>TREINAMENTO</option><option>OUTRO</option></select></div><div class="field"><label>DESCRIÇÃO DO REQUISITO</label><input id="crLabel" placeholder="Ex.: Dominar inventário rotativo"></div></div>`,`<button class="btn" onclick="document.getElementById('careerReqModal').classList.remove('open')">CANCELAR</button><button class="btn btn-primary" onclick="careerSaveRequirement('${planId}')">ADICIONAR</button>`)}
  window.careerSaveRequirement=function(planId){const label=document.getElementById('crLabel')?.value.trim();if(!label)return alert('Informe o requisito.');const p=data().plans.find(x=>String(x.id)===String(planId));if(!p)return;p.requirements.push({id:uid('req'),type:document.getElementById('crType').value,label});persist();document.getElementById('careerReqModal').classList.remove('open');render()}
  window.careerRemoveRequirement=function(planId,reqId){const p=data().plans.find(x=>String(x.id)===String(planId));if(!p)return;p.requirements=p.requirements.filter(r=>String(r.id)!==String(reqId));persist();render()}

  window.careerAssess=function(personId,planId){
    const p=getPerson(personId),plan=data().plans.find(x=>String(x.id)===String(planId));if(!p||!plan)return;
    const a=data().assessments[String(personId)]?.[String(planId)]||{};
    const body=plan.requirements.length?`<div class="career-muted" style="margin-bottom:12px">${esc(p.name||'')} · ${esc(plan.name)}</div><div class="career-assessment-grid">${plan.requirements.map((r,i)=>`<div class="assessment-item"><div class="assessment-label">${i+1}. ${esc(r.label)}<small>${esc(r.type||'Critério')}</small></div><button id="ass_${r.id}" class="assessment-btn ${a[String(r.id)]===true?'ok':''}" onclick="careerToggleRequirement('${personId}','${planId}','${r.id}')">${a[String(r.id)]===true?'CUMPRIDO':'PENDENTE'}</button></div>`).join('')}</div>`:`<div class="career-empty">Este plano ainda não possui pré-requisitos.</div>`;
    openModal('careerAssessmentModal','AVALIAÇÃO DE PRONTIDÃO',body,`<button class="btn btn-primary" onclick="document.getElementById('careerAssessmentModal').classList.remove('open');renderCareerModule()">CONCLUIR AVALIAÇÃO</button>`);
  }
  window.careerToggleRequirement=function(personId,planId,reqId){
    const d=data();d.assessments[String(personId)]=d.assessments[String(personId)]||{};d.assessments[String(personId)][String(planId)]=d.assessments[String(personId)][String(planId)]||{};
    const a=d.assessments[String(personId)][String(planId)];a[String(reqId)]=a[String(reqId)]!==true;persist();
    const b=document.getElementById('ass_'+reqId);if(b){b.classList.toggle('ok',a[String(reqId)]===true);b.textContent=a[String(reqId)]===true?'CUMPRIDO':'PENDENTE'}
  }

  function boot(){
    ensureStyle();addNav();addView();
    if(data().plans.length&&!window.__careerPlanId)window.__careerPlanId=data().plans[0].id;
    const obs=new MutationObserver(()=>{addNav();addView()});
    const nav=document.querySelector('.nav');if(nav)obs.observe(nav,{childList:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
  window.renderCareerModule=render;
})();
