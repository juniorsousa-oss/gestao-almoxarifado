from pathlib import Path

APP = Path("streamlit_app.py")
text = APP.read_text(encoding="utf-8")

start_marker = '        st.markdown(\'<div class="ge-overview-panel"><div class="ge-panel-title">Admissões mais recentes</div>\', unsafe_allow_html=True)'
start = text.find(start_marker)
if start < 0:
    raise SystemExit("Início do bloco de admissões não encontrado")

end = text.find("\n    with tab_equipes:", start)
if end < 0:
    raise SystemExit("Fim do bloco de admissões não encontrado")

replacement = '''        st.markdown("""<style>
        .ge-admissions-panel{background:linear-gradient(145deg,#101513,#0d1210);border:1px solid #35403b;border-radius:15px;padding:22px;margin-top:14px}
        .ge-admissions-title{color:#f4f5f4;font-size:16px;font-weight:900;letter-spacing:.4px;text-transform:uppercase;margin:0 0 22px}
        .ge-admissions-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;width:100%}
        .ge-admission-item{min-width:0;text-align:center;padding:0 18px;border-left:1px solid #35403b}
        .ge-admission-item:first-child{border-left:0}
        .ge-admission-photo{display:flex;justify-content:center;align-items:center;min-height:58px}
        .ge-admission-name{margin-top:9px;color:#f4f5f4;font-size:11px;font-weight:900;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .ge-admission-date{margin-top:4px;color:#89938e;font-size:9px}
        @media (max-width:900px){.ge-admissions-grid{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:20px}.ge-admission-item:nth-child(3){border-left:0}}
        @media (max-width:560px){.ge-admissions-grid{grid-template-columns:1fr}.ge-admission-item{border-left:0;border-top:1px solid #35403b;padding:16px 0 0}.ge-admission-item:first-child{border-top:0;padding-top:0}}
        </style>""", unsafe_allow_html=True)

        recentes = sorted(
            [c for c in ativos_colaboradores if c.get("data_admissao")],
            key=lambda x: x.get("data_admissao") or "",
            reverse=True,
        )[:5]

        cards_admissoes = []
        for c in recentes:
            data = pd.to_datetime(c.get("data_admissao"), errors="coerce")
            data_txt = data.strftime("%d/%m/%Y") if not pd.isna(data) else "—"
            cards_admissoes.append(
                '<div class="ge-admission-item">'
                '<div class="ge-admission-photo">' + foto_html(c,54) + '</div>'
                '<div class="ge-admission-name">' + nome_curto(c.get("nome")) + '</div>'
                '<div class="ge-admission-date">' + data_txt + '</div>'
                '</div>'
            )

        if cards_admissoes:
            st.markdown(
                '<div class="ge-admissions-panel">'
                '<div class="ge-admissions-title">Admissões mais recentes</div>'
                '<div class="ge-admissions-grid">'
                + ''.join(cards_admissoes) +
                '</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="ge-admissions-panel">'
                '<div class="ge-admissions-title">Admissões mais recentes</div>'
                '<div class="ge-empty">Nenhuma data de admissão cadastrada.</div>'
                '</div>',
                unsafe_allow_html=True,
            )'''

APP.write_text(text[:start] + replacement + text[end:], encoding="utf-8")
print("Painel de admissões atualizado.")
