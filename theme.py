"""Tema visual: konsep 'Clinical Dossier' (editorial cetak, warm-paper, no-neon).

Diadaptasi dari dashboard referensi (Investigative Dossier) untuk konteks
Monitoring Kesehatan Mental di X/Twitter. Palet & komponen dipertahankan agar
konsisten; semantik warna disesuaikan:
  - OXBLOOD  -> kelas 'Pertolongan Segera' (urgensi tinggi)
  - PINE     -> kelas 'Curhat Ringan' (organik / ringan)
  - SLATE    -> 'Tidak Relevan' / netral
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# ---- Palet Cheerful & Playful (Mental Health & Optimism) ----
PAPER      = "#FFFDF9"  # Warm soft cream/butter, sangat cerah dan ramah
SURFACE    = "#FFFFFF"  # Putih bersih untuk card & container
INK        = "#2A2E45"  # Navy-charcoal lembut (tidak terlalu dingin, ramah di mata)
MUTED      = "#6A7086"  # Abu-abu biru lembut untuk deskripsi
HAIRLINE   = "#F4EFEA"  # Batas krem sangat lembut
OXBLOOD    = "#FF6B6B"  # Coral-merah muda cerah & ramah untuk 'Pertolongan Segera'
PINE       = "#38B000"  # Hijau daun segar/cerah untuk 'Curhat Ringan'
OCHRE      = "#FFB703"  # Kuning matahari/golden cerah untuk warning
TAUPE      = "#9B5DE5"  # Ungu playful
SAGE       = "#00F5D4"  # Tosca neon/ceria
SLATE      = "#4EA8DE"  # Biru langit cerah yang damai

URGENT  = OXBLOOD
LIGHT   = PINE
SEQ = [PINE, OCHRE, OXBLOOD, SLATE, TAUPE]
CATEGORICAL = [PINE, SLATE, OCHRE, OXBLOOD, SAGE, TAUPE, "#FF9F1C"]

FONT_DISPLAY = "'Outfit', 'Comfortaa', sans-serif"
FONT_BODY    = "'Inter', sans-serif"
FONT_MONO    = "'JetBrains Mono', monospace"

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ===== FORCE LIGHT MODE — override Streamlit dark mode completely ===== */
html, body {
    background-color: #FFFDF9 !important;
    color: @INK@ !important;
    color-scheme: light !important;
}
.stApp, [data-testid="stApp"] {
    background: linear-gradient(135deg, #FFFDF9 0%, #FFF4EE 40%, #EDF8F2 100%) !important;
    color: @INK@ !important;
    color-scheme: light !important;
    font-family: @BODY@;
    --buzzer: @OXBLOOD@; --urgent: @OXBLOOD@; --organic: @PINE@; --light: @PINE@;
    --ochre: @OCHRE@; --slate: @SLATE@; --accent: @PINE@; --muted: @MUTED@;
    --border: @HAIRLINE@; --surface2: @PAPER@; --text: @INK@; --text2: @INK@;
    --serif: @DISPLAY@; --body: @BODY@; --mono: @MONO@;
}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stAppViewContainer"] > section > div,
.main, .main > div {
    background-color: transparent !important;
    color: @INK@ !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
[data-testid="stBottom"] {
    background-color: transparent !important;
    color: @INK@ !important;
}
[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
[data-testid="column"], [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stElementContainer"] {
    background-color: transparent !important;
    color: @INK@ !important;
}
/* Plotly chart containers — only outer wrapper, NOT internal SVG */
div[data-testid="stPlotlyChart"] {
    background-color: @PAPER@ !important;
    color-scheme: light !important;
}
/* Selectbox, multiselect, input widgets */
[data-testid="stMultiSelect"], [data-testid="stSelectbox"],
[data-baseweb="select"], [data-baseweb="popover"],
[data-baseweb="menu"], [data-baseweb="input"],
[data-baseweb="select"] > div {
    background-color: @SURFACE@ !important;
    color: @INK@ !important;
}
[data-baseweb="menu"] li {
    background-color: @SURFACE@ !important;
    color: @INK@ !important;
}
[data-baseweb="menu"] li:hover {
    background-color: @PAPER@ !important;
}
/* Radio, checkbox, slider */
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label,
[data-testid="stSlider"] {
    color: @INK@ !important;
}
/* Tabs */
[data-testid="stTabs"], [data-testid="stTabContent"],
div[role="tabpanel"] {
    background-color: transparent !important;
    color: @INK@ !important;
}
/* Markdown, caption, metric */
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
[data-testid="stMetric"], [data-testid="stMetricValue"] {
    color: @INK@ !important;
}
/* Expander */
[data-testid="stExpander"], [data-testid="stExpander"] details,
[data-testid="stExpander"] summary {
    background-color: @SURFACE@ !important;
    color: @INK@ !important;
}
/* All text elements */
h1,h2,h3,h4 { font-family: @DISPLAY@; color: @INK@ !important; letter-spacing: -0.01em; }
h1 { font-weight: 900; }
p, li, span, label, .stMarkdown { font-family: @BODY@; color: @INK@ !important; }
small { color: @MUTED@ !important; }
/* ===== END FORCE LIGHT MODE ===== */

.block-container { padding-top: 1.6rem; padding-bottom: 4rem; max-width: 1120px; }
.eyebrow { font-family: @MONO@; font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase; color: @PINE@; font-weight: 700; }
.sec-title { font-family: @DISPLAY@; font-size: 2.0rem; font-weight: 900; line-height: 1.05; margin: 0.1rem 0 0.2rem 0; }
.sec-sub { color: @MUTED@; font-size: 1.02rem; max-width: 70ch; margin-bottom: 0.4rem; }
.rule { height: 4px; background: @PINE@; border: none; margin: 0.5rem 0 1.2rem 0; width: 48px; border-radius: 2px; }
.rule-faint { height: 1px; background: @HAIRLINE@; border: none; margin: 2.6rem 0 1.8rem 0; }

.lead { font-family: @DISPLAY@; font-size: 1.25rem; line-height: 1.5; color: @INK@; max-width: 64ch; margin-bottom: 8px; }
.lead .hl { color: @PINE@; font-style: italic; font-weight: 700; }

.kicker { font-family: @MONO@; font-size: 0.72rem; letter-spacing: .18em; text-transform: uppercase; color: @PINE@; display: flex; align-items: center; gap: 10px; margin: 2.5rem 0 1.2rem 0; font-weight: 700; }
.kicker::after { content: ""; flex: 1; height: 1px; background: @HAIRLINE@; }

.note { color: @MUTED@; font-size: 0.95rem; line-height: 1.5; max-width: 74ch; margin: -0.4rem 0 0.8rem 0; }

.pipe { display: flex; flex-wrap: wrap; gap: 12px; align-items: stretch; margin-bottom: 1.5rem; }
.pstep { flex: 1; min-width: 130px; background: @SURFACE@; border: 2px solid @HAIRLINE@; border-radius: 14px; padding: 16px 18px; position: relative; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.pstep:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(78, 168, 222, 0.08); }
.pstep .pn { font-family: @MONO@; font-size: 10px; color: @SLATE@; letter-spacing: .1em; font-weight: 700; }
.pstep .pt { font-size: 13px; font-weight: 700; margin-top: 6px; line-height: 1.3; color: @INK@; }
.pstep .pd { font-family: @MONO@; font-size: 11px; color: @MUTED@; margin-top: 5px; }

.card { background: @SURFACE@; border: 2px solid @HAIRLINE@; border-radius: 20px; padding: 22px; margin-bottom: 1rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02), 0 2px 8px rgba(0, 0, 0, 0.01); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.card:hover { transform: translateY(-2px); box-shadow: 0 16px 36px rgba(78, 168, 222, 0.07); }

.stat { background: @SURFACE@; border: 2px solid @HAIRLINE@; border-radius: 20px; padding: 22px 22px 20px; position: relative; overflow: hidden; height: 100%; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.stat:hover { transform: translateY(-2px); box-shadow: 0 16px 36px rgba(78, 168, 222, 0.08); }
.stat .lab { font-family: @MONO@; font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase; color: @MUTED@; font-weight: 700; }
.stat .val { font-family: @DISPLAY@; font-weight: 900; font-size: 40px; line-height: 1; margin-top: 12px; letter-spacing: -.02em; color: @INK@; }
.stat .sub { font-size: 12px; color: @MUTED@; margin-top: 7px; }
.stat .accentbar { position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: @INK@; }

.stat.plain { background: linear-gradient(135deg, #FFFFFF 0%, #FFF9EB 100%); border-color: #FCEFD5; }
.stat.buzzer, .stat.urgent { background: linear-gradient(135deg, #FFFFFF 0%, #FFF2F2 100%); border-color: #FFD2D2; }
.stat.buzzer .val, .stat.urgent .val { color: @OXBLOOD@; }
.stat.buzzer .accentbar, .stat.urgent .accentbar { background: @OXBLOOD@; }
.stat.organic, .stat.light { background: linear-gradient(135deg, #FFFFFF 0%, #EDF7EE 100%); border-color: #CBEED4; }
.stat.organic .val, .stat.light .val { color: @PINE@; }
.stat.organic .accentbar, .stat.light .accentbar { background: @PINE@; }
.stat.slate { background: linear-gradient(135deg, #FFFFFF 0%, #EEF6FC 100%); border-color: #D2E7F7; }
.stat.slate .val { color: @SLATE@; }
.stat.slate .accentbar { background: @SLATE@; }

table.dt { width: 100%; border-collapse: collapse; font-size: 13.5px; margin: 10px 0; }
table.dt th { font-family: @MONO@; font-size: 10.5px; letter-spacing: .08em; text-transform: uppercase; color: @MUTED@; text-align: left; padding: 11px 14px; border-bottom: 2px solid @HAIRLINE@; font-weight: 700; }
table.dt td { padding: 11px 14px; border-bottom: 1px solid @HAIRLINE@; font-family: @MONO@; color: @INK@; }
table.dt tr:last-child td { border-bottom: none; }
table.dt tr.hl td { background: rgba(255,107,107,0.06); color: @INK@; font-weight: 600; }
table.dt tr.avg td { background: @PAPER@; font-weight: 700; color: @INK@; }
.tbl-wrap { background: @SURFACE@; border: 2px solid @HAIRLINE@; border-radius: 14px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.02); }

.cm { display: grid; grid-template-columns: auto 1fr 1fr; gap: 8px; max-width: 480px; margin: 10px 0; }
.cm .h { font-family: @MONO@; font-size: 10.5px; color: @MUTED@; display: flex; align-items: center; justify-content: center; text-align: center; padding: 6px; font-weight: 700; }
.cm .cell { border-radius: 14px; padding: 18px 12px; text-align: center; border: 2px solid @HAIRLINE@; background: @SURFACE@; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01); }
.cm .cell .n { font-family: @DISPLAY@; font-size: 32px; font-weight: 900; }
.cm .cell .t { font-family: @MONO@; font-size: 10px; color: @MUTED@; text-transform: uppercase; letter-spacing: .08em; margin-top: 4px; font-weight: 600; }
.cm .tp { background: rgba(56, 176, 0, 0.06); border-color: rgba(56, 176, 0, 0.15); }
.cm .tp .n { color: @PINE@; }
.cm .tn { background: rgba(56, 176, 0, 0.06); border-color: rgba(56, 176, 0, 0.15); }
.cm .tn .n { color: @PINE@; }
.cm .fp { background: rgba(255, 107, 107, 0.06); border-color: rgba(255, 107, 107, 0.15); }
.cm .fp .n { color: @OXBLOOD@; }
.cm .fn { background: rgba(255, 107, 107, 0.06); border-color: rgba(255, 107, 107, 0.15); }
.cm .fn .n { color: @OXBLOOD@; }

.shap-row { display: grid; grid-template-columns: 200px 1fr 64px; align-items: center; gap: 14px; padding: 8px 0; border-bottom: 1px solid @HAIRLINE@; }
.shap-row .fname { font-family: @MONO@; font-size: 12px; color: @INK@; }
.shap-track { height: 14px; background: @PAPER@; border-radius: 6px; overflow: hidden; }
.shap-fill { height: 100%; background: linear-gradient(90deg, @PINE@, #70E000); border-radius: 6px; }
.shap-val { font-family: @MONO@; font-size: 12px; color: @PINE@; text-align: right; font-weight: 700; }

.flag-badge { font-family: @MONO@; font-size: 10px; letter-spacing: .05em; padding: 3px 8px; border-radius: 6px; border: 1px solid @HAIRLINE@; white-space: nowrap; display: inline-block; font-weight: 600; }
.flag-buzzer, .flag-urgent { background: rgba(255,107,107,0.08); color: @OXBLOOD@; border-color: rgba(255,107,107,0.18); }
.flag-organic, .flag-light { background: rgba(56,176,0,0.08); color: @PINE@; border-color: rgba(56,176,0,0.18); }
.tag { display: inline-block; font-family: @MONO@; font-size: 10.5px; color: @INK@; background: @PAPER@; border: 1px solid @HAIRLINE@; border-radius: 6px; padding: 3px 9px; margin: 3px 4px 0 0; }

.callout { background: @SURFACE@; border: 2px solid @HAIRLINE@; border-left: 6px solid @OCHRE@; border-radius: 14px; padding: 16px 18px; font-size: 13.5px; color: @INK@; line-height: 1.55; margin-bottom: 1.2rem; box-shadow: 0 4px 14px rgba(0,0,0,0.02); }
.callout b { color: @INK@; }

.lda-card { background: @SURFACE@; border: 2px solid @HAIRLINE@; border-radius: 20px; padding: 20px; border-top: 6px solid @SLATE@; height: 100%; box-shadow: 0 6px 18px rgba(0,0,0,0.02); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.lda-card:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(0,0,0,0.05); }
.lda-card.named { border-top-color: @PINE@; }
.lda-id { font-family: @MONO@; font-size: 10.5px; color: @MUTED@; letter-spacing: .1em; font-weight: 700; }
.lda-name { font-family: @DISPLAY@; font-size: 18px; font-weight: 800; margin: 6px 0 10px; line-height: 1.25; color: @INK@; }
.lda-desc { font-size: 13px; color: @INK@; line-height: 1.5; }
.lda-tris { margin-top: 12px; }

div[data-testid="stExpander"] { background-color: @SURFACE@ !important; border: 2px solid @HAIRLINE@; border-radius: 14px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02); }
div[data-testid="stExpander"] details { border: none; }
div[data-testid="stExpander"] summary { font-family: @DISPLAY@; color: @INK@ !important; font-weight: 700; }

/* Custom Popover Styling */
div[data-testid="stPopover"] { width: 100%; }
div[data-testid="stPopover"] button {
    background-color: @SURFACE@ !important;
    border: 2px solid @HAIRLINE@ !important;
    border-radius: 14px !important;
    padding: 12px 14px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background-color 0.2s ease !important;
    color: @INK@ !important;
    font-family: @DISPLAY@ !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    text-align: center !important;
    width: 100% !important;
    min-height: 50px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
div[data-testid="stPopover"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 22px rgba(78, 168, 222, 0.08) !important;
    border-color: @SLATE@ !important;
    background-color: @PAPER@ !important;
}
div[data-testid="stPopoverBody"] {
    background-color: @SURFACE@ !important;
    border: 2px solid @HAIRLINE@ !important;
    border-radius: 16px !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.08) !important;
    padding: 18px !important;
    max-width: 340px !important;
}

button[data-baseweb="tab"] { font-family: @DISPLAY@; color: @MUTED@ !important; font-size: 15px !important; font-weight: 600 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: @PINE@ !important; border-bottom-color: @PINE@ !important; }

section[data-testid="stSidebar"] { background: @SURFACE@ !important; border-right: 2px solid @HAIRLINE@; }
.demo-banner { background: #EBF2EE; border-left: 6px solid @OCHRE@; padding: 0.7rem 1rem; font-family: @MONO@; font-size: 0.82rem; color: @INK@; margin-bottom: 1rem; border-radius: 10px; }

.masthead { background: linear-gradient(135deg, #1A4D33 0%, #358B61 50%, #4EA8DE 100%); color: #FFFFFF !important; padding: 2.2rem 2rem; border-radius: 24px; box-shadow: 0 12px 30px rgba(56, 176, 0, 0.15); margin-bottom: 2rem; border: none; }
.masthead .k { font-family: @MONO@; font-size: 0.75rem; letter-spacing: 0.25em; text-transform: uppercase; color: rgba(255, 255, 255, 0.8) !important; font-weight: 700; margin-bottom: 0.4rem; }
.masthead h1 { color: #FFFFFF !important; font-weight: 900; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }

#MainMenu, footer, header { visibility: hidden; }
.step-flow { display: flex; align-items: center; justify-content: space-between; gap: 15px; margin: 1.5rem 0; flex-wrap: wrap; }
.flow-node { background: @SURFACE@ !important; border: 2px solid @HAIRLINE@; border-radius: 16px; padding: 18px 20px; flex: 1; min-width: 220px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02); border-top: 5px solid @SLATE@; }
.flow-node.step1 { border-top-color: @SLATE@; }
.flow-node.step2 { border-top-color: @OCHRE@; }
.flow-node.step3 { border-top-color: @OXBLOOD@; }
.flow-node.step4 { border-top-color: @PINE@; }
.flow-arrow { font-size: 24px; color: @MUTED@; font-weight: bold; display: flex; align-items: center; justify-content: center; }
@media (max-width: 768px) {
    .step-flow { flex-direction: column; align-items: stretch; }
    .flow-arrow { transform: rotate(90deg); margin: 5px 0; }
}
"""


def _css():
    repl = {"@PAPER@": PAPER, "@SURFACE@": SURFACE, "@INK@": INK, "@MUTED@": MUTED,
            "@HAIRLINE@": HAIRLINE, "@OXBLOOD@": OXBLOOD, "@OCHRE@": OCHRE,
            "@PINE@": PINE, "@SLATE@": SLATE,
            "@DISPLAY@": FONT_DISPLAY, "@BODY@": FONT_BODY, "@MONO@": FONT_MONO}
    css = _CSS
    for k, v in repl.items():
        css = css.replace(k, v)
    return css


def inject_css():
    st.markdown("<style>" + _css() + "</style>", unsafe_allow_html=True)


def _register_template():
    t = go.layout.Template()
    t.layout = go.Layout(
        font=dict(family=FONT_BODY, size=13, color=INK),
        title=dict(font=dict(family=FONT_DISPLAY, size=17, color=INK), x=0, xanchor="left"),
        paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        colorway=CATEGORICAL,
        xaxis=dict(gridcolor=HAIRLINE, linecolor=INK, zeroline=False, ticks="outside",
                   tickfont=dict(family=FONT_MONO, size=11, color=MUTED)),
        yaxis=dict(gridcolor=HAIRLINE, linecolor=INK, zeroline=False, ticks="outside",
                   tickfont=dict(family=FONT_MONO, size=11, color=MUTED)),
        legend=dict(font=dict(family=FONT_MONO, size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=20, r=20, t=46, b=20),
    )
    pio.templates["dossier"] = t
    pio.templates.default = "dossier"


def masthead(title, kicker):
    st.markdown(
        '<div class="masthead"><div class="k">' + kicker + '</div>'
        '<h1 style="margin:0.1rem 0 0 0; font-size:2.6rem; color:#FFFFFF !important; font-weight:900;">' + title + '</h1></div>',
        unsafe_allow_html=True)


def stat(col, value, label, sub="", style="plain"):
    cls = "stat"
    if style in ["buzzer", "urgent", "organic", "light", "slate"]:
        cls += " " + style
    html = ('<div class="' + cls + '"><div class="accentbar"></div>'
            '<div class="lab">' + label + '</div>'
            '<div class="val">' + str(value) + '</div>')
    if sub:
        html += '<div class="sub">' + sub + '</div>'
    html += '</div>'
    col.markdown(html, unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="rule-faint"/>', unsafe_allow_html=True)


init_template = _register_template
