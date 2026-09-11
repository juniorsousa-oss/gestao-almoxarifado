from __future__ import annotations

import re
import streamlit as st

_ORIGINAL_MARKDOWN = st.markdown
_PATCHED = False

_LAYOUT_CSS = r'''
<style>
/* Cards de colaboradores: a coluna Streamlit passa a ser o contêiner visual real. */
[data-testid="column"]:has(.ge-colab-card) {
  background:linear-gradient(145deg,#111714,#0c100f)!important;
  border:1px solid #35403b!important;
  border-radius:16px!important;
  padding:14px 14px 12px!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
  min-height:278px!important;
  box-shadow:0 8px 22px rgba(0,0,0,.14)!important;
}
[data-testid="column"]:has(.ge-colab-card) .ge-colab-card {
  width:100%!important;min-height:0!important;height:auto!important;
  border:0!important;background:transparent!important;box-shadow:none!important;
  padding:0!important;overflow:visible!important;
}
[data-testid="column"]:has(.ge-colab-card) img {
  max-width:92px!important;width:92px!important;height:92px!important;
  object-fit:cover!important;border-radius:50%!important;display:block!important;
  margin:2px auto 13px!important;border:2px solid #ffd43d!important;
  box-shadow:0 0 0 5px rgba(255,212,61,.07)!important;
}
[data-testid="column"]:has(.ge-colab-card) .ge-colab-photo-fallback {
  width:92px!important;height:92px!important;border-radius:50%!important;
  margin:2px auto 13px!important;box-sizing:border-box!important;
}
[data-testid="column"]:has(.ge-colab-card) .ge-colab-name,
[data-testid="column"]:has(.ge-colab-card) .ge-colab-role,
[data-testid="column"]:has(.ge-colab-card) .ge-colab-team,
[data-testid="column"]:has(.ge-colab-card) .ge-colab-meta {
  width:100%!important;white-space:normal!important;overflow-wrap:anywhere!important;
  text-align:center!important;
}
[data-testid="column"]:has(.ge-colab-card) [data-testid="stButton"] button {
  width:100%!important;height:34px!important;min-height:34px!important;
  border-radius:9px!important;font-size:10px!important;font-weight:900!important;
  text-transform:uppercase!important;
}

/* Organograma: conectores por nível, sem linhas quebradas entre subordinados. */
.org-wrap{background:linear-gradient(145deg,#111714,#0c100f)!important;border:1px solid #34413b!important;border-radius:18px!important;padding:22px!important;min-height:620px!important;box-shadow:0 14px 40px rgba(0,0,0,.18)!important;overflow:hidden!important}
.org-title-row{display:flex;align-items:center;gap:18px;margin:0 0 18px}
.org-title-row .org-title{margin:0!important;text-align:left!important;font-size:20px!important;color:#f4f5f4!important}
.org-title-sub{font-size:11px;color:#8f9994;margin-top:5px}
.org-viewport{width:100%;min-height:500px;max-height:760px;overflow:auto;border:1px solid #26312c;border-radius:14px;background:radial-gradient(circle at 50% 0%,rgba(255,212,61,.045),transparent 38%),#0a0e0d;padding:24px 20px 34px;box-sizing:border-box}
.org-zoom{width:max-content;min-width:100%;transform-origin:top center}
.org-zoom-value{height:38px;display:flex;align-items:center;justify-content:center;border:1px solid #35403b;border-radius:9px;background:#101513;color:#ffd43d;font-size:11px;font-weight:900}
.org-main .org-tree{display:flex!important;flex-direction:column!important;align-items:center!important;min-width:max-content!important;padding:8px 24px 20px!important;box-sizing:border-box!important;overflow:visible!important}
.org-main .org-node{width:240px!important;min-height:132px!important;box-sizing:border-box!important;padding:14px 13px 12px!important;border:1px solid #3b4741!important;border-radius:15px!important;background:linear-gradient(160deg,#18201c,#0d1210)!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:flex-start!important;position:relative!important;box-shadow:0 8px 24px rgba(0,0,0,.2)!important;overflow:hidden!important}
.org-main .org-node.root{border:2px solid #ffd43d!important;background:linear-gradient(160deg,#20271f,#111613)!important}
.org-main .org-node img,.org-main .org-node .ge-avatar-fallback{width:66px!important;height:66px!important;min-width:66px!important;min-height:66px!important;border-radius:50%!important;object-fit:cover!important;flex:0 0 66px!important;border:2px solid #ffd43d!important;display:block!important}
.org-main .org-node strong{display:block!important;width:100%!important;max-width:210px!important;margin-top:10px!important;font-size:12px!important;line-height:1.25!important;font-weight:900!important;color:#f4f5f4!important;text-transform:uppercase!important;text-align:center!important;white-space:normal!important;overflow-wrap:anywhere!important}
.org-main .org-node small{display:block!important;width:100%!important;max-width:210px!important;margin-top:5px!important;font-size:10px!important;line-height:1.3!important;font-weight:800!important;color:#aeb7b2!important;text-transform:uppercase!important;text-align:center!important;white-space:normal!important;overflow-wrap:anywhere!important}
.org-main .org-children{display:flex!important;justify-content:center!important;align-items:flex-start!important;gap:28px!important;position:relative!important;width:max-content!important;min-width:100%!important;padding-top:28px!important;margin-top:0!important}
.org-main .org-children::before{content:""!important;position:absolute!important;top:14px!important;left:120px!important;right:120px!important;height:2px!important;background:#4a5750!important}
.org-main .org-children:has(>.org-child:only-child)::before{display:none!important}
.org-main .org-child{position:relative!important;display:flex!important;flex-direction:column!important;align-items:center!important;min-width:240px!important;width:240px!important;padding-top:14px!important;box-sizing:border-box!important}
.org-main .org-child::before{content:""!important;position:absolute!important;top:-14px!important;left:50%!important;width:2px!important;height:14px!important;background:#4a5750!important;transform:translateX(-50%)!important}
.org-main .org-child>.org-connector{display:none!important}
.org-main .org-connector{display:none!important}
.org-main .org-grandchildren{width:100%!important}
@media(max-width:900px){.org-main .org-children{gap:14px!important}.org-main .org-children::before{display:none!important}}
</style>
'''


def _render_validated_org(body: str) -> None:
    # Keep the already generated hierarchy from streamlit_app.py, but place it
    # inside a controlled viewport and apply a local zoom value.
    title_match = re.search(r'<div class="org-title">(.*?)</div>', body, re.S)
    title = title_match.group(1) if title_match else "ORGANOGRAMA DO ALMOXARIFADO"
    tree_match = re.search(r'<div class="org-tree">(.*)</div></div>\s*$', body, re.S)
    tree = tree_match.group(1) if tree_match else body

    if "org_zoom" not in st.session_state:
        st.session_state.org_zoom = 80

    c1,c2,c3,c4,c5=st.columns([1,1.4,1.2,1.4,1],gap="small")
    with c1:
        if st.button("−",key="org_zoom_out_patch",use_container_width=True):
            st.session_state.org_zoom=max(50,st.session_state.org_zoom-10)
            st.rerun()
    with c2:
        st.session_state.org_zoom=st.slider("ZOOM",50,140,st.session_state.org_zoom,10,key="org_zoom_slider_patch",label_visibility="collapsed")
    with c3:
        _ORIGINAL_MARKDOWN(f'<div class="org-zoom-value">{st.session_state.org_zoom}%</div>',unsafe_allow_html=True)
    with c4:
        if st.button("ENQUADRAR",key="org_zoom_fit_patch",use_container_width=True):
            st.session_state.org_zoom=70
            st.rerun()
    with c5:
        if st.button("+",key="org_zoom_in_patch",use_container_width=True):
            st.session_state.org_zoom=min(140,st.session_state.org_zoom+10)
            st.rerun()

    html=f'''<div class="org-wrap">
<div class="org-title-row"><div><div class="org-title">{title}</div><div class="org-title-sub">Visualização hierárquica por níveis e subordinados.</div></div></div>
<div class="org-viewport"><div class="org-zoom" style="zoom:{st.session_state.org_zoom/100}"><div class="org-tree">{tree}</div></div></div>
</div>'''
    _ORIGINAL_MARKDOWN(html,unsafe_allow_html=True)


def _patched_markdown(body, *args, **kwargs):
    global _PATCHED
    if not _PATCHED:
        _ORIGINAL_MARKDOWN(_LAYOUT_CSS,unsafe_allow_html=True)
        _PATCHED=True
    if isinstance(body,str) and 'class="org-wrap org-main"' in body and 'class="org-tree"' in body:
        _render_validated_org(body)
        return None
    return _ORIGINAL_MARKDOWN(body,*args,**kwargs)


st.markdown = _patched_markdown
