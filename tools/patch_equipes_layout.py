from pathlib import Path

p=Path("streamlit_app.py")
s=p.read_text(encoding="utf-8")

# Organograma como segunda aba.
s=s.replace('tab_geral,tab_equipes,tab_colaboradores,tab_organograma=st.tabs(["VISÃO GERAL","EQUIPES","COLABORADORES","ORGANOGRAMA"])','tab_geral,tab_organograma,tab_equipes,tab_colaboradores=st.tabs(["VISÃO GERAL","ORGANOGRAMA","EQUIPES","COLABORADORES"])')

# Admissões recentes alinhadas.
old='''        cards=[]
        for c in recentes:
            dt=pd.to_datetime(c.get("data_admissao"),errors="coerce");cards.append(f'<div style="text-align:center"><div>{foto_html(c,60)}</div><div style="font-weight:900;font-size:12px;margin-top:8px">{nome_curto(c.get("nome"))}</div><div class="muted" style="font-size:11px">{dt.strftime("%d/%m/%Y") if not pd.isna(dt) else "—"}</div></div>')
        if cards:st.markdown('<div class="panel"><div class="ge-panel-title">ADMISSÕES MAIS RECENTES</div><div style="display:grid;grid-template-columns:repeat(5,1fr);gap:18px">'+''.join(cards)+'</div></div>',unsafe_allow_html=True)'''
new='''        cards=[]
        for c in recentes:
            dt=pd.to_datetime(c.get("data_admissao"),errors="coerce")
            data_txt=dt.strftime("%d/%m/%Y") if not pd.isna(dt) else "—"
            cards.append(f'<div class="ge-admissao-card"><div class="ge-admissao-photo">{foto_html(c,60)}</div><div class="ge-admissao-name">{nome_curto(c.get("nome"))}</div><div class="ge-admissao-date">{data_txt}</div></div>')
        if cards:st.markdown('<div class="panel ge-admissoes-panel"><div class="ge-panel-title">ADMISSÕES MAIS RECENTES</div><div class="ge-admissoes-grid">'+''.join(cards)+'</div></div>',unsafe_allow_html=True)'''
if old in s:s=s.replace(old,new)

# Organograma principal limpo; ajustes de hierarquia somente no expander.
start=s.find('    with tab_organograma:')
end=s.find('\nelif pagina=="carreira":',start)
if start!=-1 and end!=-1:
    block='''    with tab_organograma:
        st.markdown('<div class="org-focus-head"><div class="org-focus-title">ORGANOGRAMA</div><div class="org-focus-sub">Estrutura hierárquica visual do almoxarifado.</div></div>',unsafe_allow_html=True)
        people=ativos_colaboradores
        ids=[str(c.get("id")) for c in people]
        byid={str(c.get("id")):c for c in people}
        org=config.get("organograma",{})
        saved_parents={str(k):str(v) for k,v in (org.get("pais") or {}).items()}
        saved_parents={k:v for k,v in saved_parents.items() if k in ids and v in ids and k!=v}
        saved_root=str(org.get("raiz_id")) if str(org.get("raiz_id")) in ids else (ids[0] if ids else "")
        if people:
            def org_node(c,isroot=False):
                photo=foto_html(c,58)
                return f'<div class="org-node {"root" if isroot else ""}">{photo}<strong>{c.get("nome","")}</strong><small>{c.get("funcao") or "Sem função"}</small></div>'
            def build_children(parents,root_id):
                children=defaultdict(list)
                for cid in ids:
                    if cid==root_id:continue
                    pid=parents.get(cid,"")
                    if pid and pid in ids and pid!=cid:children[pid].append(cid)
                    else:children[root_id].append(cid)
                return children
            def render_children(pid,children):
                kids=children.get(pid,[])
                if not kids:return ""
                inner=""
                for kid in kids:
                    inner+=f'<div class="org-child"><div class="org-connector"></div>{org_node(byid[kid])}{render_children(kid,children)}</div>'
                return f'<div class="org-children">{inner}</div>'
            children=build_children(saved_parents,saved_root)
            st.markdown(f'<div class="org-wrap org-main"><div class="org-title">{org.get("titulo") or "ORGANOGRAMA DO ALMOXARIFADO"}</div><div class="org-tree">{org_node(byid[saved_root],True)}<div class="org-connector"></div>{render_children(saved_root,children)}</div></div>',unsafe_allow_html=True)
            with st.expander("⚙ AJUSTAR ORGANOGRAMA",expanded=False):
                root_opts={f"{c.get('nome','')} — {(c.get('funcao') or 'Sem função').upper()}":str(c.get('id')) for c in people}
                root_labels=list(root_opts.keys());root_index=list(root_opts.values()).index(saved_root) if saved_root in root_opts.values() else 0
                titulo_org=st.text_input("Título",value=org.get("titulo") or "ORGANOGRAMA DO ALMOXARIFADO",key="org_titulo_ajuste")
                root_label=st.selectbox("Responsável / raiz",root_labels,index=root_index,key="org_root_ajuste")
                draft_root=str(root_opts[root_label]);st.caption("Defina o superior imediato de cada colaborador. A visualização principal mostra somente o organograma.")
                novas_pais={}
                for c in people:
                    cid=str(c.get("id"));options={"NÍVEL 1 — RAIZ":""}
                    for superior in people:
                        sid=str(superior.get("id"))
                        if sid!=cid:options[f"{nome_curto(superior.get('nome'))} — {(superior.get('funcao') or 'Sem função').upper()}"]=sid
                    atual=saved_parents.get(cid,"");vals=list(options.values());idx=vals.index(atual) if atual in vals else 0
                    escolha=st.selectbox(f"{c.get('nome','')} · {c.get('funcao') or 'Sem função'}",list(options.keys()),index=idx,key=f"org_parent_ajuste_{cid}")
                    novas_pais[cid]=options[escolha]
                def has_cycle(start_id,parents):
                    seen=set();cur=start_id
                    while cur:
                        if cur in seen:return True
                        seen.add(cur);cur=parents.get(cur,"")
                    return False
                for cid in list(novas_pais):
                    if cid!=draft_root and has_cycle(cid,novas_pais):novas_pais[cid]=""
                    if cid==draft_root:novas_pais[cid]=""
                if st.button("SALVAR ORGANOGRAMA",type="primary",use_container_width=True,key="salvar_org_ajuste"):
                    config["organograma"]={"titulo":titulo_org.strip() or "ORGANOGRAMA DO ALMOXARIFADO","raiz_id":draft_root,"pais":novas_pais}
                    if save_global_config():registrar_historico("organograma_atualizado","Organograma atualizado",{"raiz_id":draft_root,"colaboradores":len(people)});st.rerun()
                    else:st.error("Não foi possível salvar o organograma.")
        else:st.info("Cadastre colaboradores ativos para montar o organograma.")
'''
    s=s[:start]+block+s[end:]

# Colaboradores: volta ao cartão visual e o cartão inteiro seleciona.
cstart=s.find('        if filtrados:\n',s.find('    with tab_colaboradores:'))
cend=s.find('        escolhido=next(',cstart)
if cstart!=-1 and cend!=-1:
    block='''        if filtrados:
            selected_id=st.session_state.get("colab_selecionado")
            for base in range(0,len(filtrados),5):
                cols=st.columns(5)
                for col,c in zip(cols,filtrados[base:base+5]):
                    cid=str(c.get("id"));selecionado=selected_id==cid
                    nome=(c.get("nome") or "Sem nome").upper();func=(c.get("funcao") or "Sem função").upper()
                    equipe=nomes_eq.get(str(c.get("equipe_id")),c.get("equipe_atual") or "SEM EQUIPE");status_txt="ATIVO" if c.get("ativo",True) else "INATIVO"
                    with col:
                        if c.get("foto_base64"):
                            mime=c.get("foto_mime") or "image/jpeg";b64=c.get("foto_base64")
                            st.markdown("<style>div.st-key-card_colab_"+cid+" button{background-image:url('data:"+mime+";base64,"+b64+")!important;}</style>",unsafe_allow_html=True)
                        label=nome+"\n"+func+"\n"+equipe.upper()+"\n"+status_txt+" · "+str(c.get('matricula') or 'SEM MATRÍCULA')
                        if st.button(label,key=f"card_colab_{cid}",use_container_width=True,type="primary" if selecionado else "secondary"):
                            st.session_state.colab_selecionado=cid;st.rerun()
        else:st.info("Nenhum colaborador encontrado.")
'''
    s=s[:cstart]+block+s[cend:]

# CSS extra.
anchor='.ge-click-card{{width:100%;border:1px solid #34413b!important;'
extra='''
.ge-admissoes-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;align-items:start}.ge-admissao-card{text-align:center;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-start}.ge-admissao-photo{height:70px;display:flex;align-items:center;justify-content:center}.ge-admissao-name{height:30px;display:flex;align-items:center;justify-content:center;width:100%;font-size:12px;font-weight:900;color:#f4f5f4;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ge-admissao-date{height:18px;font-size:11px;color:#9aa39f}.ge-admissoes-panel{padding:16px 18px 14px}.ge-admissoes-panel .ge-panel-title{margin-bottom:8px}.org-focus-head{margin:4px 0 12px}.org-focus-title{font-size:22px;font-weight:900;color:#f4f5f4;text-transform:uppercase}.org-focus-sub{font-size:12px;color:#8f9994;margin-top:4px}.org-main{min-height:620px}.org-main .org-title{font-size:20px;margin-bottom:34px}.org-main .org-node{width:220px;padding:12px}.org-main .org-node strong{font-size:13px}.org-main .org-node small{font-size:10px}.org-main .org-children{gap:36px}div[data-testid="stExpander"]{border:1px solid #34413b!important;border-radius:12px!important;background:#0d1210!important;margin-top:14px}
div[class*="st-key-card_colab_"] button{height:238px!important;min-height:238px!important;border-radius:16px!important;border:1px solid #34413b!important;background-color:#101513!important;background-repeat:no-repeat!important;background-position:center 15px!important;background-size:88px 88px!important;padding:116px 10px 10px!important;display:flex!important;align-items:flex-start!important;justify-content:center!important;text-align:center!important;white-space:pre-line!important;box-shadow:none!important;font-size:12px!important;font-weight:900!important;line-height:1.45!important;color:#f4f5f4!important}div[class*="st-key-card_colab_"] button:hover{border-color:#ffd43d!important}div[class*="st-key-card_colab_"] button[kind="primary"]{border:2px solid #ffd43d!important;background-color:#171b15!important}div[class*="st-key-card_colab_"] button p{white-space:pre-line!important;text-align:center!important;font-weight:900!important;width:100%!important}
'''
if anchor in s:s=s.replace(anchor,extra+'\n'+anchor,1)
s=s.replace('[data-testid="stSidebar"] .stButton>button p{{color:inherit!important;margin:0!important}}','[data-testid="stSidebar"] .stButton>button p{{color:inherit!important;margin:0!important;text-align:left!important;width:100%!important;display:block!important}} [data-testid="stSidebar"] .stButton>button>div{{width:100%!important;justify-content:flex-start!important}}')
p.write_text(s,encoding="utf-8")
print("patch_equipes_layout: OK")
