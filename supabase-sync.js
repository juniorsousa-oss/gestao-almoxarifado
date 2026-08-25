/* ============================================================
   SINCRONIZAÇÃO CLOUD — GESTÃO ALMOXARIFADO
   Banco: Supabase / almox_app_state
   ============================================================ */
(function(){
  const SUPABASE_URL = 'https://cuixazpxkvniqldmmnth.supabase.co';
  const SUPABASE_KEY = 'sb_publishable_ZTqIgmA9Ez6AVQsoXa0P8Q_6CYHDFye';
  const STATE_ID = 'main';
  const POLL_MS = 5000;

  if(!window.supabase || !window.supabase.createClient){
    console.error('[CLOUD] Supabase JS não carregado.');
    return;
  }

  const client = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
  let lastCloudUpdatedAt = '';
  let applyingRemote = false;
  let lastLocalSaveAt = 0;

  function buildCloudState(){
    try{
      return JSON.parse(JSON.stringify(state));
    }catch(err){
      console.error('[CLOUD] Não foi possível serializar o estado.',err);
      return null;
    }
  }

  async function readCloud(){
    const {data,error} = await client
      .from('almox_app_state')
      .select('id,estado,atualizado_em')
      .eq('id',STATE_ID)
      .maybeSingle();
    if(error) throw error;
    return data || null;
  }

  async function writeCloud(){
    if(applyingRemote) return;
    const snapshot=buildCloudState();
    if(!snapshot) return;

    const {data,error}=await client
      .from('almox_app_state')
      .upsert({
        id:STATE_ID,
        estado:snapshot,
        atualizado_em:new Date().toISOString()
      },{onConflict:'id'})
      .select('atualizado_em')
      .single();

    if(error){
      console.error('[CLOUD] Falha ao sincronizar:',error);
      showCloudStatus('ERRO DE SINCRONIZAÇÃO',true);
      return;
    }

    lastLocalSaveAt=Date.now();
    lastCloudUpdatedAt=data?.atualizado_em||new Date().toISOString();
    showCloudStatus('SINCRONIZADO',false);
  }

  function showCloudStatus(text,isError){
    let el=document.getElementById('cloudSyncStatus');
    if(!el){
      el=document.createElement('div');
      el.id='cloudSyncStatus';
      el.style.cssText='position:fixed;right:14px;bottom:14px;z-index:9999;padding:7px 10px;border:1px solid #35403b;border-radius:8px;background:#111715;color:#b9c0bd;font:700 9px Inter,Segoe UI,Arial,sans-serif;opacity:.86;pointer-events:none;transition:opacity .3s;';
      document.body.appendChild(el);
    }
    el.textContent='● '+text;
    el.style.color=isError?'#ff9c9c':'#72e6a0';
    el.style.opacity='0.86';
    clearTimeout(el.__timer);
    el.__timer=setTimeout(()=>el.style.opacity='0',1800);
  }

  async function bootstrap(){
    try{
      showCloudStatus('CONECTANDO...',false);
      const remote=await readCloud();

      if(remote?.estado && typeof remote.estado==='object' && Object.keys(remote.estado).length){
        applyingRemote=true;
        state=remote.estado;
        state.orphanPeople=state.orphanPeople||[];
        state.collaborators=state.collaborators||[];
        state.teams=state.teams||[];
        state.freeOrg=Object.assign({selected:[],parents:{},order:[]},state.freeOrg||{});
        state.texts=Object.assign({},base?.texts||{},state.texts||{});
        state.macroOrg=Object.assign({title:'ORGANOGRAMA MACRO',root:'ALMOXARIFADO',teamOrder:[]},state.macroOrg||{});
        lastCloudUpdatedAt=remote.atualizado_em||'';
        applyingRemote=false;

        render();
        renderBrand();
        renderTeams();
        renderCollaborators();
        renderFreeOrg();
        if(document.getElementById('config')?.classList.contains('active')) loadConfigForm();
        showCloudStatus('DADOS DA NUVEM CARREGADOS',false);
      }else{
        await writeCloud();
      }
    }catch(err){
      applyingRemote=false;
      console.error('[CLOUD] Falha na inicialização:',err);
      showCloudStatus('MODO LOCAL — SEM CONEXÃO',true);
    }
  }

  async function refreshFromCloud(){
    if(applyingRemote) return;
    try{
      const remote=await readCloud();
      if(!remote?.estado || !remote.atualizado_em) return;

      const remoteTime=new Date(remote.atualizado_em).getTime();
      const knownTime=lastCloudUpdatedAt?new Date(lastCloudUpdatedAt).getTime():0;
      if(remoteTime<=knownTime || remoteTime<=lastLocalSaveAt) return;

      applyingRemote=true;
      state=remote.estado;
      state.orphanPeople=state.orphanPeople||[];
      state.collaborators=state.collaborators||[];
      state.teams=state.teams||[];
      state.freeOrg=Object.assign({selected:[],parents:{},order:[]},state.freeOrg||{});
      state.texts=Object.assign({},base?.texts||{},state.texts||{});
      state.macroOrg=Object.assign({title:'ORGANOGRAMA MACRO',root:'ALMOXARIFADO',teamOrder:[]},state.macroOrg||{});
      lastCloudUpdatedAt=remote.atualizado_em;
      applyingRemote=false;

      render();
      renderBrand();
      renderTeams();
      renderCollaborators();
      renderFreeOrg();
      if(document.getElementById('config')?.classList.contains('active')) loadConfigForm();
      showCloudStatus('ATUALIZADO DA NUVEM',false);
    }catch(err){
      console.warn('[CLOUD] Falha ao atualizar:',err);
    }
  }

  const originalSave=window.save;
  if(typeof originalSave==='function'){
    window.save=function(){
      const result=originalSave.apply(this,arguments);
      if(!applyingRemote){
        lastLocalSaveAt=Date.now();
        setTimeout(()=>writeCloud(),0);
      }
      return result;
    };
  }

  window.syncCloudNow=writeCloud;
  window.reloadFromCloud=refreshFromCloud;

  bootstrap();
  setInterval(refreshFromCloud,POLL_MS);
})();
