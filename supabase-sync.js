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

/* ============================================================
   PATCH ORGANOGRAMA V9 — ÁRVORE PROFISSIONAL + CONECTORES + RESIZE
   Aplicado após o index.html, sem substituir as demais funções do sistema.
   ============================================================ */
(function(){
  const style=document.createElement('style');
  style.id='organograma-v9-runtime';
  style.textContent=`
    #equipes .organogram-panel{position:relative;overflow:visible!important}
    #equipes .free-org-area{
      position:relative!important;
      min-height:500px!important;
      max-height:780px!important;
      overflow:auto!important;
      padding:34px 24px 50px!important;
      background:#0d1210!important;
    }
    #equipes .free-org-stage{
      position:relative!important;
      width:max-content!important;
      min-width:100%!important;
      min-height:440px!important;
      padding:8px 44px 60px!important;
      box-sizing:border-box!important;
    }
    #equipes .free-org-connectors{
      position:absolute!important;
      inset:0!important;
      width:100%!important;
      height:100%!important;
      pointer-events:none!important;
      overflow:visible!important;
      z-index:0!important;
    }
    #equipes .free-org-connector{
      fill:none!important;
      stroke:#59655f!important;
      stroke-width:1.8!important;
      vector-effect:non-scaling-stroke!important;
    }
    #equipes .free-org-root{
      position:relative!important;
      z-index:1!important;
      width:max-content!important;
      min-width:100%!important;
      min-height:390px!important;
      display:flex!important;
      flex-direction:column!important;
      align-items:center!important;
      justify-content:flex-start!important;
      text-align:center!important;
    }
    #equipes .free-org-root-list{
      position:relative!important;
      width:max-content!important;
      min-width:0!important;
      margin:0!important;
      padding:0 44px!important;
      display:flex!important;
      flex-direction:row!important;
      flex-wrap:nowrap!important;
      align-items:flex-start!important;
      justify-content:center!important;
      gap:86px!important;
    }
    #equipes .free-org-node-wrap{
      position:relative!important;
      width:calc(var(--org-size,56px) + 12px)!important;
      min-width:calc(var(--org-size,56px) + 12px)!important;
      max-width:none!important;
      flex:0 0 calc(var(--org-size,56px) + 12px)!important;
      display:flex!important;
      flex-direction:column!important;
      align-items:center!important;
      justify-content:flex-start!important;
    }
    #equipes .free-org-node{
      position:relative!important;
      z-index:2!important;
      width:var(--org-size,56px)!important;
      height:var(--org-size,56px)!important;
      min-width:var(--org-size,56px)!important;
      min-height:var(--org-size,56px)!important;
      max-width:120px!important;
      max-height:120px!important;
      padding:3px!important;
      margin:0!important;
      display:block!important;
      border:2px solid var(--yellow)!important;
      border-radius:50%!important;
      background:#151b18!important;
      box-shadow:0 0 0 3px rgba(255,210,10,.06)!important;
      cursor:grab!important;
      user-select:none!important;
    }
    #equipes .free-org-node:hover{box-shadow:0 0 0 4px rgba(255,210,10,.14)!important;transform:none!important}
    #equipes .free-org-node.dragging{opacity:.42!important}
    #equipes .free-org-node.resizing{cursor:nwse-resize!important;opacity:.9!important}
    #equipes .free-org-node.selected-anchor{box-shadow:0 0 0 4px rgba(255,210,10,.20)!important}
    #equipes .free-org-node .free-org-photo{
      display:block!important;
      width:calc(var(--org-size,56px) - 8px)!important;
      height:calc(var(--org-size,56px) - 8px)!important;
      min-width:0!important;
      min-height:0!important;
      max-width:none!important;
      max-height:none!important;
      margin:0 auto!important;
      border:0!important;
      border-radius:50%!important;
      object-fit:cover!important;
    }
    #equipes .free-org-photo.initials{
      display:grid!important;
      place-items:center!important;
      background:#252d29!important;
      color:#fff!important;
      font-size:calc(var(--org-size,56px) * .34)!important;
      font-weight:900!important;
    }
    #equipes .free-org-node .free-org-name,
    #equipes .free-org-node .free-org-role,
    #equipes .free-org-node .free-org-info,
    #equipes .free-org-node .free-org-actions,
    #equipes .free-org-node .free-org-drag{display:none!important}
    #equipes .free-org-resize-handle{
      position:absolute!important;
      right:-3px!important;
      bottom:-3px!important;
      width:13px!important;
      height:13px!important;
      border-right:3px solid rgba(255,210,10,.95)!important;
      border-bottom:3px solid rgba(255,210,10,.95)!important;
      border-radius:0 0 7px 0!important;
      cursor:nwse-resize!important;
      opacity:0!important;
      z-index:5!important;
    }
    #equipes .free-org-node:hover .free-org-resize-handle,
    #equipes .free-org-node.resizing .free-org-resize-handle{opacity:1!important}
    #equipes .free-org-children{
      position:relative!important;
      width:max-content!important;
      min-width:0!important;
      margin:58px 0 0!important;
      padding:0 44px!important;
      border:0!important;
      display:flex!important;
      flex-direction:row!important;
      flex-wrap:nowrap!important;
      align-items:flex-start!important;
      justify-content:center!important;
      gap:86px!important;
    }
    #equipes .free-org-children::before,
    #equipes .free-org-children::after,
    #equipes .free-org-children .free-org-node-wrap::before,
    #equipes .free-org-children .free-org-node-wrap::after,
    #equipes .free-org-root-list::before,
    #equipes .free-org-root-list::after,
    #equipes .free-org-root-list .free-org-node-wrap::before,
    #equipes .free-org-root-list .free-org-node-wrap::after{
      content:none!important;
      display:none!important;
    }
    #equipes .free-org-empty{padding:90px 20px!important;color:#66716c!important}
    #equipes .org-adjust-menu{
      position:absolute!important;
      top:60px!important;
      right:14px!important;
      z-index:200!important;
    }
    @media(max-width:900px){
      #equipes .free-org-root-list,#equipes .free-org-children{gap:58px!important;padding-left:28px!important;padding-right:28px!important}
    }
    @media(max-width:700px){
      #equipes .free-org-area{padding:26px 12px 40px!important}
      #equipes .free-org-root-list,#equipes .free-org-children{gap:42px!important;padding-left:20px!important;padding-right:20px!important}
      #equipes .free-org-node-wrap{width:calc(var(--org-size,52px) + 10px)!important;min-width:calc(var(--org-size,52px) + 10px)!important}
      #equipes .free-org-node{width:var(--org-size,52px)!important;height:var(--org-size,52px)!important;min-width:var(--org-size,52px)!important;min-height:var(--org-size,52px)!important}
      #equipes .free-org-node .free-org-photo{width:calc(var(--org-size,52px) - 8px)!important;height:calc(var(--org-size,52px) - 8px)!important}
    }
  `;
  document.head.appendChild(style);

  function orgSize(id){
    const m=freeOrgData();
    m.sizes=m.sizes||{};
    return Math.max(44,Math.min(120,Number(m.sizes[String(id)])||56));
  }

  window.renderFreeOrg=function(){
    const el=document.getElementById('freeOrgArea');
    if(!el)return;
    const m=freeOrgData();
    m.sizes=m.sizes||{};
    const peopleById=new Map((state.collaborators||[]).map(p=>[String(p.id),p]));
    const relation=document.getElementById('freeOrgRelationBar');

    if(relation){
      const a=peopleById.get(String(freeOrgAnchorId||''));
      const b=peopleById.get(String(freeOrgPairId||''));
      if(a&&b){
        relation.style.display='flex';
        relation.className='free-org-relation-bar active';
        relation.innerHTML=
          '<div class="free-org-relation-title"><strong>GESTOR:</strong> '+esc(a.name)+
          ' &nbsp;→&nbsp; <strong>COLABORADOR:</strong> '+esc(b.name)+'</div>'+\
          '<div class="free-org-relation-actions">'+\
          '<button class="btn btn-primary btn-small" onclick="applyFreeOrgRelation(\'subordinate\')">SUBORDINADO DE '+esc(a.name).toUpperCase()+'</button>'+\
          '<button class="btn btn-small" onclick="applyFreeOrgRelation(\'same\')">MESMO NÍVEL DE '+esc(a.name).toUpperCase()+'</button>'+\
          '</div>';
      }else if(a){
        relation.style.display='flex';
        relation.className='free-org-relation-bar active';
        relation.innerHTML='<div class="free-org-relation-title"><strong>GESTOR:</strong> '+esc(a.name)+
          '. Selecione outro colaborador para definir a subordinação.</div>';
      }else{
        relation.style.display='none';
        relation.className='free-org-relation-bar';
        relation.innerHTML='';
      }
    }

    const renderNode=(id,stack)=>{
      const sid=String(id);
      const p=peopleById.get(sid);
      if(!p||stack.has(sid))return '';
      const next=new Set(stack);next.add(sid);
      const kids=freeOrgChildren(sid);
      const anchor=String(freeOrgAnchorId||'')===sid?' selected-anchor':'';
      const size=orgSize(sid);
      return '<div class="free-org-node-wrap" data-org-wrap="'+esc(sid)+'">'+
        '<div class="free-org-node'+anchor+'" draggable="true" data-org-id="'+esc(sid)+
        '" style="--org-size:'+size+'px" '+
        'ondragstart="freeOrgDragStart(event,\''+esc(sid)+'\')" '+
        'ondragend="this.classList.remove(\'dragging\')" '+
        'ondragover="freeOrgDragOver(event)" '+
        'ondrop="freeOrgDrop(event,\''+esc(sid)+'\')">'+
        freeOrgAvatar(p)+
        '<span class="free-org-resize-handle" title="Arraste para redimensionar" onmousedown="startFreeOrgResize(event,\''+esc(sid)+'\')"></span>'+
        '</div>'+
        (kids.length?'<div class="free-org-children">'+kids.map(k=>renderNode(k,next)).join('')+'</div>':'')+
        '</div>';
    };

    const roots=freeOrgChildren('');
    el.innerHTML='<div class="free-org-stage">'+
      '<svg class="free-org-connectors" aria-hidden="true"></svg>'+\
      '<div class="free-org-root" ondragover="freeOrgDragOver(event)" ondrop="freeOrgDrop(event,\'\')">'+\
      (roots.length?'<div class="free-org-root-list">'+roots.map(id=>renderNode(id,new Set())).join('')+'</div>':\
      '<div class="free-org-empty">Clique em uma foto acima para adicionar o primeiro gestor.</div>')+\
      '</div></div>';

    requestAnimationFrame(function(){
      drawProfessionalOrgConnectors();
      bindResizeAndConnectorRefresh();
    });
  };

  function drawProfessionalOrgConnectors(){
    const area=document.getElementById('freeOrgArea');
    const stage=area?.querySelector('.free-org-stage');
    const svg=stage?.querySelector('.free-org-connectors');
    if(!stage||!svg)return;

    const nodes=[...stage.querySelectorAll('.free-org-node[data-org-id]')];
    const stageRect=stage.getBoundingClientRect();
    const width=Math.max(stage.scrollWidth,stage.clientWidth);
    const height=Math.max(stage.scrollHeight,stage.clientHeight);
    svg.setAttribute('width',width);
    svg.setAttribute('height',height);
    svg.setAttribute('viewBox','0 0 '+width+' '+height);
    svg.innerHTML='';

    const byId=new Map(nodes.map(n=>[String(n.dataset.orgId),n]));
    const m=freeOrgData();
    const point=node=>{const r=node.getBoundingClientRect();return{x:r.left-stageRect.left+r.width/2,top:r.top-stageRect.top,bottom:r.bottom-stageRect.top};};
    const path=d=>{const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',d);p.setAttribute('class','free-org-connector');svg.appendChild(p);};

    const childrenByParent={};
    nodes.forEach(node=>{
      const id=String(node.dataset.orgId);
      const parent=String(m.parents[id]||'');
      if(parent)(childrenByParent[parent] ||= []).push(id);
    });

    Object.keys(childrenByParent).forEach(parentId=>{
      const parentNode=byId.get(parentId);
      if(!parentNode)return;
      const children=childrenByParent[parentId].filter(id=>byId.has(id));
      if(!children.length)return;
      const p=point(parentNode);
      const cps=children.map(id=>point(byId.get(id))).sort((a,b)=>a.x-b.x);
      const gap=cps[0].top-p.bottom;
      const junctionY=p.bottom+Math.max(24,Math.min(42,gap/2));
      if(children.length===1){path('M '+p.x+' '+p.bottom+' V '+cps[0].top);return;}
      path('M '+p.x+' '+p.bottom+' V '+junctionY);
      path('M '+cps[0].x+' '+junctionY+' H '+cps[cps.length-1].x);
      cps.forEach(c=>path('M '+c.x+' '+junctionY+' V '+c.top));
    });
  }

  function bindResizeAndConnectorRefresh(){
    if(window.__orgV9ResizeBound)return;
    window.__orgV9ResizeBound=true;
    window.addEventListener('resize',function(){requestAnimationFrame(drawProfessionalOrgConnectors)},{passive:true});
    window.addEventListener('scroll',function(){requestAnimationFrame(drawProfessionalOrgConnectors)},{passive:true});
  }

  window.startFreeOrgResize=function(e,id){
    e.preventDefault();
    e.stopPropagation();
    const node=document.querySelector('#freeOrgArea .free-org-node[data-org-id="'+CSS.escape(String(id))+'"]');
    if(!node)return;
    const m=freeOrgData();
    m.sizes=m.sizes||{};
    const sid=String(id);
    const start=orgSize(sid);
    const startX=e.clientX;
    const move=function(ev){
      const size=Math.max(44,Math.min(120,start+(ev.clientX-startX)));
      node.style.setProperty('--org-size',Math.round(size)+'px');
      requestAnimationFrame(drawProfessionalOrgConnectors);
    };
    const up=function(ev){
      const size=Math.max(44,Math.min(120,start+(ev.clientX-startX)));
      m.sizes[sid]=Math.round(size);
      save();
      document.removeEventListener('mousemove',move);
      document.removeEventListener('mouseup',up);
      node.classList.remove('resizing');
      requestAnimationFrame(drawProfessionalOrgConnectors);
    };
    node.classList.add('resizing');
    document.addEventListener('mousemove',move);
    document.addEventListener('mouseup',up,{once:true});
  };

  const oldSetParent=window.setFreeOrgParent;
  if(typeof oldSetParent==='function'){
    window.setFreeOrgParent=function(child,parent){
      oldSetParent(child,parent);
      requestAnimationFrame(drawProfessionalOrgConnectors);
    };
  }

  const oldToggle=window.toggleOrgAdjustMenu;
  if(typeof oldToggle==='function'){
    window.toggleOrgAdjustMenu=function(force){
      oldToggle(force);
      const menu=document.getElementById('orgAdjustMenu');
      if(menu)menu.style.top='60px';
    };
  }

  requestAnimationFrame(function(){
    if(typeof renderTeams==='function')renderTeams();
    if(typeof renderCollaborators==='function')renderCollaborators();
    window.renderFreeOrg();
  });
})();
