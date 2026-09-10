from pathlib import Path

p = Path("streamlit_app.py")
s = p.read_text(encoding="utf-8")

replacements = {
    'header[data-testid="stHeader"]{{background:#ffffff !important;height:64px !important;border-bottom:1px solid #e5e7eb !important;box-shadow:0 1px 3px rgba(0,0,0,.06) !important;}}':
    'header[data-testid="stHeader"]{{display:block !important;background:transparent !important;height:0 !important;min-height:0 !important;border:0 !important;box-shadow:none !important;}}',
    '[data-testid="stToolbar"]{{display:flex !important;align-items:center !important;}}':
    '[data-testid="stToolbar"]{{display:none !important;}}',
    'button[data-testid="stSidebarCollapseButton"]{{display:flex !important;visibility:visible !important;pointer-events:auto !important;position:fixed !important;top:64px !important;':
    'button[data-testid="stSidebarCollapseButton"]{{display:flex !important;visibility:visible !important;pointer-events:auto !important;position:fixed !important;top:10px !important;',
    'div[data-testid="collapsedControl"]{{position:fixed !important;top:64px !important;':
    'div[data-testid="collapsedControl"]{{position:fixed !important;top:10px !important;',
    '.block-container{{max-width:1500px;padding:38px 34px 50px}}':
    '.block-container{{max-width:1500px;padding:18px 34px 50px}}',
    '.sidebar-logo-section{{width:100%;display:flex;flex-direction:column;align-items:center;margin:-35px 0 8px;':
    '.sidebar-logo-section{{width:100%;display:flex;flex-direction:column;align-items:center;margin:8px 0 8px;',
}

for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f"Trecho não encontrado: {old[:80]}")
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("Layout superior ajustado: header oculto, toolbar removida, >> preservado e conteúdo elevado.")
