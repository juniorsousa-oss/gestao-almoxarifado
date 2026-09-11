from pathlib import Path

path = Path("streamlit_app.py")
text = path.read_text(encoding="utf-8")
changed = False

# Replace the old organogram/card CSS block with the validated layout CSS.
css_start = text.find(".org-main{")
css_end = text.find('div[data-testid="stExpander"]{{', css_start)
if css_start >= 0 and css_end > css_start and ".org-viewport{{" not in text[css_start:css_end]:
    css = r'''.org-wrap{{background:linear-gradient(145deg,#111714,#0c100f)!important;border:1px solid #34413b!important;border-radius:18px!important;padding:22px!important;min-height:620px!important;box-shadow:0 14px 40px rgba(0,0,0,.18)!important;overflow:hidden!important}}
.org-title-row{{display:flex;align-items:center;gap:18px;margin:0 0 18px}}
.org-title-row .org-title{{margin:0!important;text-align:left!important;font-size:20px!important;color:#f4f5f4!important}}
.org-title-sub{{font-size:11px;color:#8f9994;margin-top:5px}}
.org-viewport{{width:100%;min-height:500px;max-height:760px;overflow:auto;border:1px solid #26312c;border-radius:14px;background:radial-gradient(circle at 50% 0%,rgba(255,212,61,.045),transparent 38%),#0a0e0d;padding:24px 20px 34px;box-sizing:border-box}}
.org-zoom{{width:max-content;min-width:100%;transform-origin:top center}}
.org-tree{{display:flex;flex-direction:column;align-items:center;min-width:max-content;padding:8px 24px 20px;box-sizing:border-box}}
.org-node{{width:240px!important;min-height:132px!important;box-sizing:border-box;padding:14px 13px 12px!important;border:1px solid #3b4741!important;border-radius:15px!important;background:linear-gradient(160deg,#18201c,#0d1210)!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:flex-start!important;position:relative!important;box-shadow:0 8px 24px rgba(0,0,0,.2)!important;overflow:hidden!important}}
.org-node.root{{border:2px solid #ffd43d!important;background:linear-gradient(160deg,#20271f,#111613)!important}}
.org-node img,.org-node .ge-avatar-fallback{{width:66px!important;height:66px!important;min-width:66px!important;min-height:66px!important;border-radius:50%!important;object-fit:cover!important;flex:0 0 66px!important;border:2px solid #ffd43d!important;display:block!important}}
.org-node strong{{display:block!important;width:100%!important;max-width:210px!important;margin-top:10px!important;font-size:12px!important;line-height:1.25!important;font-weight:900!important;color:#f4f5f4!important;text-transform:uppercase!important;text-align:center!important;white-space:normal!important;overflow-wrap:anywhere!important}}
.org-node small{{display:block!important;width:100%!important;max-width:210px!important;margin-top:5px!important;font-size:10px!important;line-height:1.3!important;font-weight:800!important;color:#aeb7b2!important;text-transform:uppercase!important;text-align:center!important;white-space:normal!important;overflow-wrap:anywhere!important}}
.org-down{{height:28px;width:2px;background:#4a5750;flex:0 0 28px}}
.org-level{{display:flex;align-items:flex-start;justify-content:center;gap:28px;position:relative;width:max-content;min-width:100%;padding-top:28px}}
.org-level.single{{padding-top:28px}}
.org-level::before{{content:"";position:absolute;top:14px;left:120px;right:120px;height:2px;background:#4a5750}}
.org-level.single::before{{display:none}}
.org-child{{width:240px;min-width:240px;position:relative;display:flex;flex-direction:column;align-items:center;padding-top:14px;box-sizing:border-box}}
.org-child::before{{content:"";position:absolute;top:-14px;left:50%;width:2px;height:14px;background:#4a5750;transform:translateX(-50%)}}
.org-level.single .org-child::before{{height:28px;top:-28px}}
.org-children-nested{{width:100%;display:flex;flex-direction:column;align-items:center}}
.org-zoom-value{{height:38px;display:flex;align-items:center;justify-content:center;border:1px solid #35403b;border-radius:9px;background:#101513;color:#ffd43d;font-size:11px;font-weight:900}}
.ge-colab-card{{width:100%;min-height:0!important;height:auto!important;border:0!important;background:transparent!important;box-shadow:none!important;padding:0!important;overflow:visible!important}}
.ge-colab-photo-wrap{{width:96px;height:96px;flex:0 0 96px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid #ffd43d;background:#171d19;box-shadow:0 0 0 5px rgba(255,212,61,.07);overflow:hidden;margin:0 auto 13px}}
.ge-colab-photo-wrap img,.ge-colab-photo-wrap .ge-avatar-img{{width:92px!important;height:92px!important;object-fit:cover;display:block!important;border-radius:50%}}
.ge-colab-name{{width:100%;min-height:38px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:13px;line-height:1.25;font-weight:900;color:#f4f5f4;text-transform:uppercase;white-space:normal;overflow-wrap:anywhere}}
.ge-colab-role{{width:100%;min-height:32px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:11px;line-height:1.3;font-weight:900;color:#ffd43d;text-transform:uppercase;margin-top:5px;white-space:normal;overflow-wrap:anywhere}}
.ge-colab-team{{width:100%;min-height:30px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:10px;line-height:1.3;color:#a3ada8;text-transform:uppercase;margin-top:4px;white-space:normal;overflow-wrap:anywhere}}
.ge-colab-meta{{width:100%;min-height:16px;font-size:10px;line-height:1.3;color:#7f8b85;text-align:center;margin-top:6px;white-space:normal;overflow-wrap:anywhere}}
.ge-colab-select{{width:100%;margin-top:10px}}
.ge-colab-select button{{width:100%!important;height:34px!important;min-height:34px!important;border-radius:9px!important;font-size:10px!important;font-weight:900!important;text-transform:uppercase!important}}
.ge-colab-select button[kind="primary"]{{box-shadow:0 0 0 2px rgba(255,212,61,.14)!important}}
@media(max-width:900px){{.org-level{{gap:14px}}.org-level::before{{display:none}}}}
'''
    text = text[:css_start] + css + text[css_end:]
    changed = True

# Replace collaborator card rendering so image, information and action are in one Streamlit container.
colab_anchor = text.find('    with tab_colaboradores:\n')
colab_start = text.find('        if filtrados:\n', colab_anchor)
colab_end = text.find('        escolhido=next(', colab_start)
if colab_anchor >= 0 and colab_start >= 0 and colab_end > colab_start and 'with st.container(border=True):' not in text[colab_start:colab_end]:
    colab = '''        if filtrados:
            selected_id=st.session_state.get("colab_selecionado")
            for base in range(0,len(filtrados),5):
                cols=st.columns(5,gap="medium")
                for col,c in zip(cols,filtrados[base:base+5]):
                    cid=str(c.get("id"));selecionado=selected_id==cid
                    nome=(c.get("nome") or "Sem nome").upper()
                    func=(c.get("funcao") or "SEM FUNÇÃO").upper()
                    equipe=nomes_eq.get(str(c.get("equipe_id")),c.get("equipe_atual") or "SEM EQUIPE")
                    status_txt="ATIVO" if c.get("ativo",True) else "INATIVO"
                    matricula=str(c.get("matricula") or "SEM MATRÍCULA")
                    with col:
                        with st.container(border=True):
                            card_cls="ge-colab-card selected" if selecionado else "ge-colab-card"
                            st.markdown(f'<div class="{card_cls}"><div class="ge-colab-photo-wrap">{foto_html(c,92)}</div><div class="ge-colab-name">{nome}</div><div class="ge-colab-role">{func}</div><div class="ge-colab-team">{equipe.upper()}</div><div class="ge-colab-meta">{status_txt} · {matricula}</div></div>',unsafe_allow_html=True)
                            if st.button("SELECIONADO" if selecionado else "SELECIONAR",key=f"card_colab_{cid}",use_container_width=True,type="primary" if selecionado else "secondary"):
                                st.session_state.colab_selecionado=cid
                                st.rerun()
        else:st.info("Nenhum colaborador encontrado.")
'''
    text = text[:colab_start] + colab + text[colab_end:]
    changed = True

# Replace organogram rendering with the validated recursive hierarchy and local zoom controls.
org_start = text.find('    with tab_organograma:\n')
org_end = text.find('elif pagina=="carreira":', org_start)
if org_start >= 0 and org_end > org_start and 'st.session_state.org_zoom' not in text[org_start:org_end]:
    org = '''    with tab_organograma:
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
                photo=foto_html(c,66)
                return f'<div class="org-node {"root" if isroot else ""}">{photo}<strong>{c.get("nome","")}</strong><small>{c.get("funcao") or "Sem função"}</small></div>'
            def build_children(parents,root_id):
                children=defaultdict(list)
                for cid in ids:
                    if cid==root_id:
                        continue
                    pid=parents.get(cid,"")
                    if pid and pid in ids and pid!=cid:
                        children[pid].append(cid)
                    else:
                        children[root_id].append(cid)
                for pid in children:
                    children[pid].sort(key=lambda x:(byid[x].get("nome") or "").upper())
                return children
            def render_branch(pid,children):
                kids=children.get(pid,[])
                if not kids:
                    return ""
                single=" single" if len(kids)==1 else ""
                parts=[f'<div class="org-level{single}">']
                for kid in kids:
                    parts.append(f'<div class="org-child">{org_node(byid[kid])}')
                    nested=render_branch(kid,children)
                    if nested:
                        parts.append('<div class="org-children-nested"><div class="org-down"></div>'+nested+'</div>')
                    parts.append('</div>')
                parts.append('</div>')
                return ''.join(parts)
            children=build_children(saved_parents,saved_root)
            root_html=org_node(byid[saved_root],True)
            branch_html=render_branch(saved_root,children)
            if "org_zoom" not in st.session_state:
                st.session_state.org_zoom=80
            c1,c2,c3,c4,c5=st.columns([1,1.4,1.2,1.4,1],gap="small")
            with c1:
                if st.button("−",key="org_zoom_out",use_container_width=True):
                    st.session_state.org_zoom=max(50,st.session_state.org_zoom-10);st.rerun()
            with c2:
                st.session_state.org_zoom=st.slider("ZOOM",50,140,st.session_state.org_zoom,10,key="org_zoom_slider",label_visibility="collapsed")
            with c3:
                st.markdown(f'<div class="org-zoom-value">{st.session_state.org_zoom}%</div>',unsafe_allow_html=True)
            with c4:
                if st.button("ENQUADRAR",key="org_zoom_fit",use_container_width=True):
                    st.session_state.org_zoom=70;st.rerun()
            with c5:
                if st.button("+",key="org_zoom_in",use_container_width=True):
                    st.session_state.org_zoom=min(140,st.session_state.org_zoom+10);st.rerun()
            st.markdown(f'''<div class="org-wrap">
  <div class="org-title-row"><div><div class="org-title">{org.get("titulo") or "ORGANOGRAMA DO ALMOXARIFADO"}</div><div class="org-title-sub">Visualização hierárquica por níveis e subordinados.</div></div></div>
  <div class="org-viewport"><div class="org-zoom" style="zoom:{st.session_state.org_zoom/100}"><div class="org-tree">{root_html}<div class="org-down"></div>{branch_html}</div></div></div>
</div>''',unsafe_allow_html=True)
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
                    if save_global_config():
                        registrar_historico("organograma_atualizado","Organograma atualizado",{"raiz_id":draft_root,"colaboradores":len(people)})
                        st.rerun()
                    else:st.error("Não foi possível salvar o organograma.")
        else:st.info("Cadastre colaboradores ativos para montar o organograma.")

'''
    text = text[:org_start] + org + text[org_end:]
    changed = True

if changed:
    path.write_text(text, encoding="utf-8")
    print("layout validado aplicado")
else:
    print("layout já aplicado; nenhuma alteração")
