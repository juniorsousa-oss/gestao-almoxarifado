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
})();
