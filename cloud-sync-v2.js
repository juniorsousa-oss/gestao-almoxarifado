/* CLOUD SYNC V2 — persistência compartilhada do Gestão Almoxarifado
   Fonte oficial: Supabase / almox_app_state / id=main
   Estratégia: nuvem > local somente quando houver estado remoto válido;
   estado local não vazio é preservado quando a nuvem estiver vazia.
*/
(function(){
  'use strict';

  const SUPABASE_URL='https://cuixazpxkvniqldmmnth.supabase.co';
  const SUPABASE_KEY='sb_publishable_ZTqIgmA9Ez6AVQsoXa0P8Q_6CYHDFye';
  const STATE_ID='main';
  const POLL_MS=3500;
  const DEBOUNCE_MS=700;

  let client=null;
  let remoteUpdatedAt='';
  let applyingRemote=false;
  let writeTimer=null;
  let dirtyUntil=0;
  let bootFinished=false;
  let lastLocalFingerprint='';

  function status(text,error){
    let el=document.getElementById('cloudSyncStatus');
    if(!el){
      el=document.createElement('div');
      el.id='cloudSyncStatus';
      el.style.cssText='position:fixed;right:14px;bottom:14px;z-index:99999;padding:7px 10px;border:1px solid #35403b;border-radius:8px;background:#111715;color:#72e6a0;font:700 9px Inter,Segoe UI,Arial,sans-serif;opacity:.9;pointer-events:none;';
      document.body.appendChild(el);
    }
    el.textContent='● '+text;
    el.style.color=error?'#ff9c9c':'#72e6a0';
    el.style.opacity='.9';
    clearTimeout(el.__t);
    el.__t=setTimeout(()=>el.style.opacity='0',2200);
  }

  function normalize(){
    if(typeof state!=='object' || !state)return null;
    state.collaborators=Array.isArray(state.collaborators)?state.collaborators:[];
    state.teams=Array.isArray(state.teams)?state.teams:[];
    state.orphanPeople=Array.isArray(state.orphanPeople)?state.orphanPeople:[];
    state.freeOrg=Object.assign({selected:[],parents:{},order:[],sizes:{}},state.freeOrg||{});
    state.freeOrg.selected=Array.isArray(state.freeOrg.selected)?state.freeOrg.selected:[];
    state.freeOrg.order=Array.isArray(state.freeOrg.order)?state.freeOrg.order:[];
    state.freeOrg.parents=state.freeOrg.parents||{};
    state.freeOrg.sizes=state.freeOrg.sizes||{};
    state.texts=Object.assign({},state.texts||{});
    state.macroOrg=Object.assign({title:'ORGANOGRAMA MACRO',root:'ALMOXARIFADO',teamOrder:[]},state.macroOrg||{});
    return state;
  }

  function snapshot(){
    try{
      const s=normalize();
      return s?JSON.parse(JSON.stringify(s)):null;
    }catch(e){
      console.error('[CLOUD V2] snapshot:',e);
      return null;
    }
  }

  function fingerprint(s){
    try{return JSON.stringify(s||{});}catch(e){return '';}
  }

  function hasMeaningfulData(s){
    if(!s)return false;
    return Boolean(
      (s.collaborators&&s.collaborators.length) ||
      (s.teams&&s.teams.length) ||
      (s.orphanPeople&&s.orphanPeople.length) ||
      (s.freeOrg&&s.freeOrg.selected&&s.freeOrg.selected.length)
    );
  }

  async function readRemote(){
    const {data,error}=await client.from('almox_app_state')
      .select('id,estado,atualizado_em')
      .eq('id',STATE_ID)
      .maybeSingle();
    if(error)throw error;
    return data||null;
  }

  function redraw(){
    try{ if(typeof render==='function')render(); }catch(e){}
    try{ if(typeof renderBrand==='function')renderBrand(); }catch(e){}
    try{ if(typeof renderTeams==='function')renderTeams(); }catch(e){}
    try{ if(typeof renderCollaborators==='function')renderCollaborators(); }catch(e){}
    try{ if(typeof renderFreeOrg==='function')renderFreeOrg(); }catch(e){}
    try{ if(document.getElementById('config')?.classList.contains('active') && typeof loadConfigForm==='function')loadConfigForm(); }catch(e){}
  }

  async function writeRemote(reason){
    if(!client || applyingRemote)return;
    const s=snapshot();
    if(!s)return;
    const fp=fingerprint(s);
    if(fp===lastLocalFingerprint && reason!=='force')return;

    try{
      const now=new Date().toISOString();
      const {data,error}=await client.from('almox_app_state').upsert({
        id:STATE_ID,
        estado:s,
        atualizado_em:now
      },{onConflict:'id'}).select('atualizado_em').single();
      if(error)throw error;
      lastLocalFingerprint=fp;
      remoteUpdatedAt=data?.atualizado_em||now;
      status('SINCRONIZADO',false);
    }catch(e){
      console.error('[CLOUD V2] write:',e);
      status('ERRO AO SALVAR NA NUVEM',true);
    }
  }

  function markDirty(reason){
    if(applyingRemote || !bootFinished)return;
    dirtyUntil=Date.now()+2500;
    clearTimeout(writeTimer);
    writeTimer=setTimeout(()=>writeRemote(reason||'event'),DEBOUNCE_MS);
  }

  async function applyRemote(remote){
    if(!remote?.estado || typeof remote.estado!=='object')return;
    applyingRemote=true;
    try{
      state=remote.estado;
      normalize();
      remoteUpdatedAt=remote.atualizado_em||'';
      lastLocalFingerprint=fingerprint(state);
      redraw();
    }finally{
      applyingRemote=false;
    }
  }

  async function bootstrap(){
    try{
      if(!window.supabase?.createClient){
        status('SUPABASE NÃO CARREGADO',true);
        return;
      }
      client=window.supabase.createClient(SUPABASE_URL,SUPABASE_KEY);
      status('VERIFICANDO NUVEM...',false);

      /* Espera a sincronização antiga terminar para evitar corrida de estado. */
      await new Promise(r=>setTimeout(r,1800));
      const remote=await readRemote();
      const local=snapshot();
      const remoteValid=hasMeaningfulData(remote?.estado);
      const localValid=hasMeaningfulData(local);

      if(remoteValid){
        await applyRemote(remote);
      }else if(localValid){
        /* Primeiro navegador ainda possui os dados: migra-os para a nuvem. */
        lastLocalFingerprint='';
        await writeRemote('bootstrap-local');
      }else if(remote?.estado){
        await applyRemote(remote);
      }else if(local){
        await writeRemote('bootstrap-empty');
      }

      bootFinished=true;
      status('CLOUD ATIVO',false);
    }catch(e){
      console.error('[CLOUD V2] bootstrap:',e);
      bootFinished=true;
      status('MODO LOCAL — CLOUD INDISPONÍVEL',true);
    }
  }

  async function poll(){
    if(!client || !bootFinished || applyingRemote)return;
    try{
      const remote=await readRemote();
      if(!remote?.estado || !remote.atualizado_em)return;
      const rt=new Date(remote.atualizado_em).getTime();
      const kt=remoteUpdatedAt?new Date(remoteUpdatedAt).getTime():0;
      if(rt<=kt || Date.now()<dirtyUntil)return;

      const current=snapshot();
      const remoteFp=fingerprint(remote.estado);
      const currentFp=fingerprint(current);
      if(remoteFp===currentFp){
        remoteUpdatedAt=remote.atualizado_em;
        lastLocalFingerprint=currentFp;
        return;
      }
      await applyRemote(remote);
      status('ATUALIZADO DA NUVEM',false);
    }catch(e){
      console.warn('[CLOUD V2] poll:',e);
    }
  }

  window.syncCloudNowV2=function(){
    if(!bootFinished)return;
    dirtyUntil=Date.now()+3000;
    clearTimeout(writeTimer);
    writeTimer=setTimeout(()=>writeRemote('manual'),50);
  };

  /* Captura as alterações feitas pela interface, inclusive quando alguma
     função interna não chama save(). */
  ['click','change','input','drop','dragend'].forEach(type=>{
    document.addEventListener(type,function(e){
      if(e.target?.closest?.('#cloudSyncStatus'))return;
      markDirty(type);
    },true);
  });

  /* Mantém compatibilidade com a função save() existente. */
  const oldSave=window.save;
  if(typeof oldSave==='function'){
    window.save=function(){
      const result=oldSave.apply(this,arguments);
      markDirty('save');
      return result;
    };
  }

  /* Se o aplicativo escrever no localStorage diretamente, também sincroniza. */
  try{
    const oldSetItem=Storage.prototype.setItem;
    Storage.prototype.setItem=function(key,value){
      const result=oldSetItem.apply(this,arguments);
      if(!applyingRemote && bootFinished)markDirty('storage');
      return result;
    };
  }catch(e){console.warn('[CLOUD V2] storage hook:',e)}

  window.addEventListener('beforeunload',function(){
    if(bootFinished && !applyingRemote)window.syncCloudNowV2();
  });

  bootstrap();
  setInterval(poll,POLL_MS);

  /*
     CARREGAMENTO EXPLÍCITO DO LAYOUT DO ORGANOGRAMA.
     O arquivo de layout já existe no projeto, mas não estava sendo incluído
     pelo index.html. Carregamos aqui para não alterar o restante do aplicativo.
  */
  function loadOrgLayout(){
    if(document.getElementById('organograma-layout-v8-loader'))return;
    const s=document.createElement('script');
    s.id='organograma-layout-v8-loader';
    s.src='./organograma-layout-v7.js?v=8';
    s.async=false;
    s.onload=function(){ console.info('[ORGANOGRAMA] layout V8 carregado'); };
    s.onerror=function(){ console.error('[ORGANOGRAMA] não foi possível carregar o layout V8'); };
    document.body.appendChild(s);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',loadOrgLayout,{once:true});
  else loadOrgLayout();

  /* =========================================================
     EDITOR ISOLADO — CABEÇALHOS DO DASHBOARD
     Não altera menu, Gestão de Equipes, organograma ou Plano de Carreira.
     ========================================================= */
  (function dashboardHeaderEditor(){
    const STYLE_ID='dashboard-header-editor-style';
    const MODAL_ID='dashboardHeaderModal';

    function installStyle(){
      if(document.getElementById(STYLE_ID))return;
      const s=document.createElement('style');
      s.id=STYLE_ID;
      s.textContent=`
        #dashboardHeaderEditBtn{margin-left:auto;}
        #dashboardHeaderModal .modal-box{width:min(820px,100%);}
        #dashboardHeaderModal .dashboard-header-section{border:1px solid #29332f;border-radius:10px;background:#0d1210;padding:14px;margin-top:12px;}
        #dashboardHeaderModal .dashboard-header-section:first-child{margin-top:0;}
        #dashboardHeaderModal .dashboard-header-section h4{margin:0 0 11px;color:#fff;font-size:12px;}
        #dashboardHeaderModal .dashboard-header-help{color:var(--muted);font-size:10px;line-height:1.4;margin-bottom:10px;}
        #dashboardHeaderModal .dashboard-header-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:16px;}
      `;
      document.head.appendChild(s);
    }

    function ensureModal(){
      if(document.getElementById(MODAL_ID))return;
      const modal=document.createElement('div');
      modal.className='modal';
      modal.id=MODAL_ID;
      modal.innerHTML=`
        <div class="modal-box">
          <div class="modal-head">
            <h3>Editar cabeçalhos do Dashboard</h3>
            <button class="close" type="button" data-dash-head-close>×</button>
          </div>
          <div class="notice">Edite somente os títulos e rótulos exibidos no Dashboard. Os números dos indicadores não são alterados nesta tela.</div>
          <div class="dashboard-header-section">
            <h4>01 · ACURÁCIA DE ESTOQUE</h4>
            <div class="dashboard-header-help">Título da seção e os três cabeçalhos dos cards.</div>
            <div class="form-grid">
              <div class="field full"><label>TÍTULO DA SEÇÃO</label><input id="dashHeadAccSection"></div>
              <div class="field"><label>CARD 1</label><input id="dashHeadAccKpi1"></div>
              <div class="field"><label>CARD 2</label><input id="dashHeadAccKpi2"></div>
              <div class="field"><label>CARD 3</label><input id="dashHeadAccKpi3"></div>
            </div>
          </div>
          <div class="dashboard-header-section">
            <h4>02 · ENTREGAS NO PRAZO</h4>
            <div class="dashboard-header-help">Título da seção e os quatro cabeçalhos dos cards.</div>
            <div class="form-grid">
              <div class="field full"><label>TÍTULO DA SEÇÃO</label><input id="dashHeadDelSection"></div>
              <div class="field"><label>CARD 1</label><input id="dashHeadDelKpi1"></div>
              <div class="field"><label>CARD 2</label><input id="dashHeadDelKpi2"></div>
              <div class="field"><label>CARD 3</label><input id="dashHeadDelKpi3"></div>
              <div class="field"><label>CARD 4</label><input id="dashHeadDelKpi4"></div>
            </div>
          </div>
          <div class="dashboard-header-section">
            <h4>GRÁFICOS E BARRAS</h4>
            <div class="form-grid">
              <div class="field"><label>GRÁFICO — ACURÁCIA</label><input id="dashHeadAccChart"></div>
              <div class="field"><label>GRÁFICO — ENTREGAS</label><input id="dashHeadDelChart"></div>
              <div class="field"><label>BARRA 1</label><input id="dashHeadProg1"></div>
              <div class="field"><label>BARRA 2</label><input id="dashHeadProg2"></div>
            </div>
          </div>
          <div class="dashboard-header-actions">
            <button class="btn" type="button" data-dash-head-cancel>CANCELAR</button>
            <button class="btn btn-primary" type="button" data-dash-head-save>SALVAR CABEÇALHOS</button>
          </div>
        </div>`;
      document.body.appendChild(modal);
      modal.addEventListener('click',e=>{
        if(e.target===modal)e.target.classList.remove('open');
        if(e.target.closest('[data-dash-head-close],[data-dash-head-cancel]'))modal.classList.remove('open');
        if(e.target.closest('[data-dash-head-save]'))saveHeaders();
      });
    }

    function value(id){return document.getElementById(id)?.value.trim()||'';}
    function setValue(id,v){const e=document.getElementById(id);if(e)e.value=v||'';}

    function openHeaders(){
      ensureStyle();
      ensureModal();
      const t=state?.texts||{};
      setValue('dashHeadAccSection',t.accSection);
      setValue('dashHeadAccKpi1',t.accKpi1);
      setValue('dashHeadAccKpi2',t.accKpi2);
      setValue('dashHeadAccKpi3',t.accKpi3);
      setValue('dashHeadDelSection',t.delSection);
      setValue('dashHeadDelKpi1',t.delKpi1);
      setValue('dashHeadDelKpi2',t.delKpi2);
      setValue('dashHeadDelKpi3',t.delKpi3);
      setValue('dashHeadDelKpi4',t.delKpi4);
      setValue('dashHeadAccChart',t.accChart);
      setValue('dashHeadDelChart',t.delChart);
      setValue('dashHeadProg1',t.prog1);
      setValue('dashHeadProg2',t.prog2);
      document.getElementById(MODAL_ID).classList.add('open');
    }

    function saveHeaders(){
      if(!state)return;
      state.texts=state.texts||{};
      const fields={
        accSection:'dashHeadAccSection',accKpi1:'dashHeadAccKpi1',accKpi2:'dashHeadAccKpi2',accKpi3:'dashHeadAccKpi3',
        delSection:'dashHeadDelSection',delKpi1:'dashHeadDelKpi1',delKpi2:'dashHeadDelKpi2',delKpi3:'dashHeadDelKpi3',delKpi4:'dashHeadDelKpi4',
        accChart:'dashHeadAccChart',delChart:'dashHeadDelChart',prog1:'dashHeadProg1',prog2:'dashHeadProg2'
      };
      Object.entries(fields).forEach(([key,id])=>{const v=value(id);if(v)state.texts[key]=v;});
      try{
        if(typeof save==='function')save();
        else localStorage.setItem(KEY,JSON.stringify(state));
      }catch(e){
        alert('Não foi possível salvar os cabeçalhos.');
        return;
      }
      try{if(typeof render==='function')render();}catch(e){}
      document.getElementById(MODAL_ID)?.classList.remove('open');
      status('CABEÇALHOS SALVOS',false);
    }

    function ensureButton(){
      const dashboard=document.getElementById('dashboard');
      if(!dashboard || document.getElementById('dashboardHeaderEditBtn'))return;
      const firstTitle=document.getElementById('accSectionTitle');
      if(!firstTitle)return;
      const wrap=document.createElement('div');
      wrap.style.cssText='display:flex;align-items:center;gap:10px;margin-bottom:12px;';
      firstTitle.style.marginBottom='0';
      firstTitle.parentNode.insertBefore(wrap,firstTitle);
      wrap.appendChild(firstTitle);
      const btn=document.createElement('button');
      btn.id='dashboardHeaderEditBtn';
      btn.className='btn btn-small';
      btn.type='button';
      btn.textContent='EDITAR CABEÇALHOS';
      btn.title='Editar títulos e rótulos do Dashboard';
      btn.addEventListener('click',openHeaders);
      wrap.appendChild(btn);
    }

    function init(){
      ensureStyle();
      ensureModal();
      ensureButton();
    }

    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
    else init();

    const oldShowView=window.showView;
    if(typeof oldShowView==='function'&&!window.__dashboardHeaderEditorPatched){
      window.__dashboardHeaderEditorPatched=true;
      window.showView=function(id,b){
        const result=oldShowView.apply(this,arguments);
        if(id==='dashboard')setTimeout(ensureButton,0);
        return result;
      };
    }
  })();
})();