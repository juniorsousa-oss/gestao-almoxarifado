from pathlib import Path
import re

# Executa a versão original do aplicativo aplicando apenas otimizações de
# transferência de dados. A lógica funcional e o layout permanecem no arquivo
# original preservado em streamlit_app_original.py.
_original = Path(__file__).with_name("streamlit_app_original.py")
_source = _original.read_text(encoding="utf-8")

# -----------------------------------------------------------------------------
# Fotos de colaboradores
# Antes a tela de equipes fazia SELECT * e transferia cerca de 20 MB de fotos
# Base64 em cada leitura. Agora a listagem usa somente thumbnails pequenas.
# Para registros antigos ainda sem thumbnail, ela é criada automaticamente na
# primeira visualização e passa a ser reutilizada nas próximas consultas.
# -----------------------------------------------------------------------------
_photo_block = re.compile(
    r"def df\(data\):return pd\.DataFrame\(data\) if data else pd\.DataFrame\(\)\n\n"
    r"def foto_html\(c,tamanho=72\):\n"
    r".*?\n"
    r"def nome_curto\(nome\):",
    re.S,
)

_photo_replacement = '''def df(data):return pd.DataFrame(data) if data else pd.DataFrame()

def criar_thumb_base64(raw,max_px=180):
    if not raw:return ""
    try:
        imagem=Image.open(BytesIO(raw)).convert("RGB")
        imagem.thumbnail((max_px,max_px))
        saida=BytesIO()
        imagem.save(saida,format="JPEG",quality=72,optimize=True)
        return base64.b64encode(saida.getvalue()).decode("ascii")
    except Exception:
        return ""

@st.cache_data(ttl=86400,show_spinner=False)
def carregar_foto_visual(colaborador_id,atualizado_em=""):
    try:
        resultado=get_client().table("almox_colaboradores").select("foto_base64,foto_mime").eq("id",colaborador_id).limit(1).execute()
        if not resultado.data:return "", "image/jpeg"
        registro=resultado.data[0]
        original=registro.get("foto_base64") or ""
        mime=registro.get("foto_mime") or "image/jpeg"
        if not original:return "", mime
        try:
            thumb=criar_thumb_base64(base64.b64decode(original))
        except Exception:
            thumb=""
        if thumb:
            try:get_client().table("almox_colaboradores").update({"foto_thumb_base64":thumb}).eq("id",colaborador_id).execute()
            except Exception:pass
            return thumb, "image/jpeg"
        return original, mime
    except Exception:
        return "", "image/jpeg"

def foto_html(c,tamanho=72):
    if not c:return '<div class="ge-avatar-fallback">?</div>'
    b64=c.get("foto_thumb_base64") or ""
    mime="image/jpeg" if b64 else (c.get("foto_mime") or "image/jpeg")
    if not b64 and c.get("id"):
        b64,mime=carregar_foto_visual(str(c.get("id")),str(c.get("atualizado_em") or ""))
    if b64:return f'<img class="ge-avatar-img" style="width:{tamanho}px;height:{tamanho}px" src="data:{mime};base64,{b64}">'
    nome=(c.get("nome") or "?").strip();return f'<div class="ge-avatar-fallback" style="width:{tamanho}px;height:{tamanho}px">{nome[:1].upper()}</div>'

def nome_curto(nome):'''

_source, _n = _photo_block.subn(_photo_replacement, _source, count=1)
if _n != 1:
    raise RuntimeError("Bloco de fotos do Gestão Almoxarifado não encontrado.")

_old_team_query='colaboradores_raw=rows("almox_colaboradores",order="nome",desc=False)'
_new_team_query='colaboradores_raw=rows("almox_colaboradores",order="nome",desc=False,columns="id,nome,funcao,equipe_atual,ativo,criado_em,atualizado_em,matricula,data_admissao,equipe_id,foto_thumb_base64,foto_mime,foto_nome")'
if _old_team_query not in _source:
    raise RuntimeError("Consulta de colaboradores não encontrada para otimização.")
_source=_source.replace(_old_team_query,_new_team_query,1)

_old_new_photo='eqid=equipes_opts.get(eq_label);b64=base64.b64encode(foto.getvalue()).decode("ascii")'
_new_new_photo='eqid=equipes_opts.get(eq_label);_foto_bytes=foto.getvalue();b64=base64.b64encode(_foto_bytes).decode("ascii");thumb=criar_thumb_base64(_foto_bytes)'
if _old_new_photo not in _source:
    raise RuntimeError("Cadastro de foto não encontrado para otimização.")
_source=_source.replace(_old_new_photo,_new_new_photo,1)
_source=_source.replace('"foto_base64":b64,"foto_mime":foto.type or "image/jpeg"','"foto_base64":b64,"foto_thumb_base64":thumb,"foto_mime":foto.type or "image/jpeg"',1)

_old_edit='dados.update({"foto_base64":base64.b64encode(foto_e.getvalue()).decode("ascii"),"foto_mime":foto_e.type or "image/jpeg","foto_nome":foto_e.name})'
_new_edit='_foto_e_bytes=foto_e.getvalue();dados.update({"foto_base64":base64.b64encode(_foto_e_bytes).decode("ascii"),"foto_thumb_base64":criar_thumb_base64(_foto_e_bytes),"foto_mime":foto_e.type or "image/jpeg","foto_nome":foto_e.name})'
if _old_edit not in _source:
    raise RuntimeError("Edição de foto não encontrada para otimização.")
_source=_source.replace(_old_edit,_new_edit,1)

exec(compile(_source,"streamlit_app_original.py","exec"),globals(),globals())
