from pathlib import Path

p = Path("controle_acesso.py")
text = p.read_text(encoding="utf-8")

if "import streamlit.components.v1 as components" not in text:
    text = text.replace("import streamlit as st\n", "import streamlit as st\nimport streamlit.components.v1 as components\n", 1)

helper = r'''

def _habilitar_autofill_login() -> None:
    """Marca os campos de login para gerenciadores de senha do navegador/iOS."""
    components.html(
        """
        <script>
        (() => {
          const doc = window.parent.document;
          const apply = () => {
            const box = doc.querySelector('div[data-testid="stForm"]');
            if (!box) return false;
            const inputs = Array.from(box.querySelectorAll('input'));
            const user = inputs.find((el) => el.type !== 'password');
            const pass = inputs.find((el) => el.type === 'password');

            if (user) {
              user.setAttribute('autocomplete', 'username');
              user.setAttribute('name', 'username');
              user.setAttribute('autocapitalize', 'none');
              user.setAttribute('spellcheck', 'false');
            }
            if (pass) {
              pass.setAttribute('autocomplete', 'current-password');
              pass.setAttribute('name', 'password');
            }

            const htmlForm = box.querySelector('form') || box.closest('form');
            if (htmlForm) htmlForm.setAttribute('autocomplete', 'on');
            return Boolean(user && pass);
          };

          apply();
          let attempts = 0;
          const timer = setInterval(() => {
            attempts += 1;
            if (apply() || attempts > 30) clearInterval(timer);
          }, 100);

          const observer = new MutationObserver(() => apply());
          observer.observe(doc.body, {childList: true, subtree: true});
          setTimeout(() => observer.disconnect(), 5000);
        })();
        </script>
        """,
        height=0,
        width=0,
    )
'''

anchor = "\ndef render_login() -> tuple[Client | None, dict[str, Any] | None]:"
if "def _habilitar_autofill_login()" not in text:
    if anchor not in text:
        raise SystemExit("Ponto de insercao do helper nao encontrado")
    text = text.replace(anchor, helper + anchor, 1)

form_anchor = '        entrar = st.form_submit_button("ENTRAR", use_container_width=True)\n\n    if entrar:'
form_replacement = '        entrar = st.form_submit_button("ENTRAR", use_container_width=True)\n\n    _habilitar_autofill_login()\n\n    if entrar:'
if "    _habilitar_autofill_login()\n\n    if entrar:" not in text:
    if form_anchor not in text:
        raise SystemExit("Ponto de chamada do autofill nao encontrado")
    text = text.replace(form_anchor, form_replacement, 1)

p.write_text(text, encoding="utf-8")
