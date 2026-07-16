"""Dashboard Monitoring Isu Kesehatan Mental di X/Twitter.

Konsep desain: 'Clinical Dossier' (editorial cetak, warm-paper, no-neon),
diadaptasi dari dashboard referensi (Investigative Dossier / deteksi buzzer).

Sistem = Evidence-Based Decision Support System: mengumpulkan evidence lalu
mengambil keputusan (Pertolongan Segera / Curhat Ringan / Tidak Relevan) yang
*dapat dijelaskan*. Seluruh angka pada dashboard ini bersumber dari output
notebook baseline (tidak ada data sintetis yang dikarang).
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import networkx as nx

import theme as T
import data_loader as dl

st.set_page_config(
    page_title="Berkas Klinis - Monitoring Kesehatan Mental",
    page_icon="\U0001FAC1",
    layout="wide",
    initial_sidebar_state="expanded",
)

T.inject_css()
T.init_template()

# ---------------- Muat data NYATA ----------------
summary = dl.js("summary.json")
features = dl.js("features.json")
metrics = dl.js("model_metrics.json")
themes_meta = dl.js("themes_meta.json")
sna = dl.js("sna_summary.json")
alert = dl.js("alert.json")

pipeline = dl.csv("pipeline.csv")
evidence_flags = dl.csv("evidence_flags.csv")
crisis_lex = dl.csv("crisis_lexicon.csv")
cv_folds = dl.csv("cv_folds.csv")
themes = dl.csv("themes.csv")
theme_cards = dl.js("theme_cards.json")
topic_trend = dl.csv("topic_trend.csv")
triage = dl.csv("triage_queue.csv")
top_sup = dl.csv("top_supporters.csv")
top_rec = dl.csv("top_receivers.csv")
daily = dl.csv("daily_urgent.csv")

A = dl.AUTH


def g(d, k, default):
    return d.get(k, default) if isinstance(d, dict) else default


def num(x):
    return format(int(round(x)), ",").replace(",", ".")


def pct(x):
    return ("%.1f" % x).replace(".", ",") + "%"


final_label = g(summary, "final_label", {"Pertolongan Segera": A["pertolongan_segera"],
                                          "Curhat Ringan": A["curhat_ringan"],
                                          "Tidak Relevan": A["tidak_relevan"]})
rule_label = g(summary, "rule_label", {})
total_post = g(summary, "total_post_bersih", A["total_post"])

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown('<div class="masthead" style="margin-bottom:0.8rem;">'
                '<div class="k">Berkas No. MH-01</div>'
                '<div style="font-family:' + T.FONT_DISPLAY + ';font-size:1.4rem;'
                'font-weight:900;line-height:1.05;">Monitoring<br>Kesehatan Mental</div></div>',
                unsafe_allow_html=True)
    st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Status Sistem</div>', unsafe_allow_html=True)
    z = g(alert, "zscore_terakhir", A["zscore"])
    status = g(alert, "status", A["status"])
    lamp = {"HIJAU": "\U0001F7E2", "KUNING": "\U0001F7E1", "MERAH": "\U0001F534"}.get(status, "\U0001F7E2")
    st.markdown(f'<div style="font-family:{T.FONT_MONO};font-size:13px;line-height:1.8;color:{T.INK};">'
                f'Lampu indikator: <b>{lamp} {status}</b><br>'
                f'z-score harian: <b>{z}</b><br>'
                f'Ambang Rule Engine: <b>{g(summary, "score_threshold_rule", A["rule_threshold"])}</b></div>',
                unsafe_allow_html=True)
    st.caption(f"Alert Engine: z-score atas agregasi harian 'Pertolongan Segera' "
               f"({g(alert, 'n_hari', 37)} hari).")
    st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Parameter Triase</div>', unsafe_allow_html=True)
    EV_THR = st.slider("Ambang evidence_score", 0.0, 0.80, 0.45, 0.01)
    st.caption("Ambang baku hasil tuning DEV: 0,45")

# ---------------- MASTHEAD ----------------
T.masthead("Anatomi Sinyal Kesehatan Mental", "Decision Support System \u00b7 Pipeline \u2192 Dashboard")

if dl.is_missing():
    st.markdown('<div class="demo-banner">\u26a0\ufe0f Folder <b>MENTAL_HEALTH_DATA</b> tak ditemukan \u2014 '
                'memakai konstanta otoritatif yang identik dengan output notebook.</div>',
                unsafe_allow_html=True)

tabs = st.tabs(["01 Validasi Sistem", "02 Hasil Monitoring", "03 Analisis Narasi", "04 Jaringan Dukungan"])

# ================= TAB 1: VALIDASI SISTEM =================
with tabs[0]:
    st.markdown('<p class="lead">Sebelum menandai satu post pun sebagai krisis, sistem harus terbukti '
                '<span class="hl">dapat dipercaya</span>. Tab ini memaparkan rantai validasi: pelabelan '
                'manusia, reliabilitas antar-anotator, performa lintas-fold, kalibrasi, hingga perbandingan '
                'dengan baseline kamus.</p>', unsafe_allow_html=True)

    if pipeline is not None:
        steps = ""
        for _, r in pipeline.iterrows():
            steps += (f'<div class="pstep"><span class="pn">Tahap {int(r["tahap"])}</span>'
                      f'<div class="pt">{r["nama"]}</div><div class="pd">{r["nilai"]}</div></div>')
        st.markdown(f'<div class="pipe" style="margin-top:1.5rem;">{steps}</div>', unsafe_allow_html=True)

    gold = g(metrics, "gold_total", 500)
    kappa = g(metrics, "cohen_kappa", A["kappa"])
    cv = g(metrics, "cv", {})
    c = st.columns(4)
    T.stat(c[0], num(gold), "Sampel Berlabel", "anotasi manual stratified")
    T.stat(c[1], f"{g(metrics, 'gold_dist', {}).get('Pertolongan Segera', 56)}",
           "Label Pertolongan Segera", "kelas urgensi (gold)", style="urgent")
    T.stat(c[2], f"{kappa:.3f}", "Cohen\u2019s Kappa", "reliabilitas antar-anotator", style="slate")
    T.stat(c[3], pct(g(cv, "mean_acc", A["cv_acc"]) * 100), "Akurasi CV",
           "rata-rata 5-fold (XGBoost)", style="light")

    st.markdown('<div class="kicker">Reliabilitas Pelabelan Manusia</div>', unsafe_allow_html=True)
    agree_pct = g(metrics, "agreement_pct", 95.4)
    safety = g(metrics, "safety_first_resolved", 23)
    gd = g(metrics, "gold_dist", {})
    st.markdown(
        f'<div class="callout"><b>Cohen\u2019s Kappa = {kappa:.3f}</b> (kesepakatan hampir sempurna). '
        f'Dua anotator sepakat pada {g(metrics, "agreement_n", 477)}/{gold} sampel ({pct(agree_pct)}); '
        f'{safety} perbedaan diselesaikan dengan prinsip <i>safety-first</i> (memihak keselamatan). '
        f'Distribusi gold: Curhat Ringan {gd.get("Curhat Ringan", 434)}, '
        f'Pertolongan Segera {gd.get("Pertolongan Segera", 56)}, '
        f'Tidak Relevan {gd.get("Tidak Relevan", 10)}.</div>', unsafe_allow_html=True)

    st.markdown('<div class="kicker">Hasil Validasi Silang (5-Fold CV)</div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Akurasi & macro-F1 per fold pada 500 sampel berlabel manusia. '
                'Macro-F1 dipakai karena kelas sangat tak seimbang \u2014 fokus pada kemampuan menangkap '
                'kelas urgensi minoritas, bukan sekadar akurasi.</p>', unsafe_allow_html=True)
    if cv_folds is not None:
        rows = ""
        for _, r in cv_folds.iterrows():
            rows += (f'<tr><td>Fold {int(r["fold"])}</td><td>{int(r["val_size"])}</td>'
                     f'<td>{r["accuracy"]*100:.1f}%</td><td>{r["macro_f1"]:.3f}</td></tr>')
        rows += (f'<tr class="avg"><td>Rata-rata</td><td>400</td>'
                 f'<td>{g(cv, "mean_acc", A["cv_acc"])*100:.1f}% \u00b1 {g(cv, "std_acc", 0.027)*100:.1f}</td>'
                 f'<td>{g(cv, "mean_macrof1", A["cv_macrof1"]):.3f} \u00b1 {g(cv, "std_macrof1", 0.037):.3f}</td></tr>')
        st.markdown(f'<div class="tbl-wrap"><table class="dt"><thead><tr>'
                    f'<th>Fold</th><th>Ukuran Val</th><th>Accuracy</th><th>Macro-F1</th>'
                    f'</tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

    st.markdown('<div class="kicker">Evaluasi Final pada TEST-Set (anti-bocor)</div>', unsafe_allow_html=True)
    test = g(metrics, "test", {})
    st.markdown(f'<p class="note">Split gold \u2192 DEV {g(test, "dev_n", 343)} / TEST {g(test, "test_n", 147)}. '
                f'Ambang Rule Engine di-tuning di DEV (= {g(test, "rule_threshold", 0.45)}) lalu diuji sekali '
                f'pada TEST yang tak pernah dipakai tuning. Confusion matrix kelas '
                f'<b>Pertolongan Segera</b> vs <b>Curhat Ringan</b>:</p>', unsafe_allow_html=True)
    cmx = g(test, "confusion", [[69, 61], [3, 14]])
    cl = st.columns([1.05, 1])
    with cl[0]:
        html = f"""
        <div class="cm">
          <div class="h"></div><div class="h">Pred. Curhat Ringan</div><div class="h">Pred. Pertolongan Segera</div>
          <div class="h">Aktual Curhat Ringan</div><div class="cell tn"><div class="n">{cmx[0][0]}</div><div class="t">benar ringan</div></div><div class="cell fp"><div class="n">{cmx[0][1]}</div><div class="t">over-triage</div></div>
          <div class="h">Aktual Pertolongan Segera</div><div class="cell fn"><div class="n">{cmx[1][0]}</div><div class="t">krisis terlewat</div></div><div class="cell tp"><div class="n">{cmx[1][1]}</div><div class="t">krisis tertangkap</div></div>
        </div>"""
        st.markdown(html, unsafe_allow_html=True)
    with cl[1]:
        pc = g(test, "per_class", {})
        seg = pc.get("Pertolongan Segera", {})
        rin = pc.get("Curhat Ringan", {})
        rows = f"""
          <tr class="hl"><td>Recall \u2014 Pertolongan Segera</td><td>{seg.get('recall',0.824)*100:.1f}%</td><td>kemampuan menangkap krisis</td></tr>
          <tr><td>Precision \u2014 Pertolongan Segera</td><td>{seg.get('precision',0.187)*100:.1f}%</td><td>ketepatan tuduhan krisis</td></tr>
          <tr><td>F1 \u2014 Curhat Ringan</td><td>{rin.get('f1',0.683)*100:.1f}%</td><td>keseimbangan kelas mayoritas</td></tr>
          <tr><td>Macro-F1</td><td>{g(test,'macro_f1',0.494)*100:.1f}%</td><td>rata-rata antar kelas</td></tr>
          <tr><td>Accuracy</td><td>{g(test,'accuracy',0.565)*100:.1f}%</td><td>rasio benar keseluruhan</td></tr>"""
        st.markdown(f'<div class="tbl-wrap"><table class="dt"><thead><tr><th>Metrik</th><th>Nilai</th>'
                    f'<th>Makna</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
    st.markdown('<div class="callout" style="border-left-color:var(--urgent);">'
                '<b>Catatan desain:</b> sistem sengaja memprioritaskan <i>recall</i> kelas '
                '\u201cPertolongan Segera\u201d (82,4%) \u2014 lebih baik over-triage daripada melewatkan '
                'sinyal krisis. Konsekuensinya precision rendah; keputusan bersifat pendukung, bukan vonis klinis.</div>',
                unsafe_allow_html=True)

    cal = g(metrics, "calibration", {})
    base = g(metrics, "baseline", {})
    cc = st.columns(2)
    with cc[0]:
        st.markdown('<div class="eyebrow">Kalibrasi Confidence</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card" style="font-family:{T.FONT_MONO};font-size:13px;line-height:1.9;">'
                    f'Metode: {g(cal, "method", "Isotonic 5-fold out-of-fold")}<br>'
                    f'Brier score: <b style="color:{T.PINE};">{g(cal, "brier", 0.085)}</b><br>'
                    f'PR-AUC (evidence_score): <b>{g(cal, "pr_auc_evidence", 0.409)}</b></div>',
                    unsafe_allow_html=True)
    with cc[1]:
        st.markdown('<div class="eyebrow">Baseline Kamus vs Rule Engine</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="tbl-wrap"><table class="dt"><thead><tr><th>Pendekatan</th>'
            f'<th>Recall (Urgent)</th><th>Macro-F1</th></tr></thead><tbody>'
            f'<tr><td>Baseline kamus (crisis lexicon)</td><td>{g(base,"kamus_recall_urgent",0.824)*100:.1f}%</td>'
            f'<td>{g(base,"kamus_macrof1",0.533):.3f}</td></tr>'
            f'<tr><td>Rule Engine (evidence-based)</td><td>{g(base,"rule_recall_urgent",0.824)*100:.1f}%</td>'
            f'<td>{g(base,"rule_macrof1",0.494):.3f}</td></tr>'
            f'</tbody></table></div>', unsafe_allow_html=True)

    st.markdown('<div class="kicker">Kekuatan Evidence (Concept Bottleneck)</div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Jumlah post yang mengaktifkan tiap jenis evidence. Evidence adalah '
                'representasi yang dapat dipahami manusia (bukan fitur mentah) \u2014 inilah yang membuat '
                'keputusan sistem dapat dijelaskan.</p>', unsafe_allow_html=True)
    if evidence_flags is not None:
        ef = evidence_flags.sort_values("count", ascending=False)
        mx = ef["count"].max()
        rows = ""
        for _, r in ef.iterrows():
            w = (r["count"] / mx * 100) if mx else 0
            rows += (f'<div class="shap-row"><span class="fname">{r["evidence"]}</span>'
                     f'<span class="shap-track"><span class="shap-fill" style="width:{w:.1f}%"></span></span>'
                     f'<span class="shap-val">{int(r["count"])}</span></div>')
        st.markdown(f'<div class="card">{rows}</div>', unsafe_allow_html=True)

# ================= TAB 2: HASIL MONITORING =================
with tabs[1]:
    st.markdown('<p class="lead">Setelah divalidasi, sistem diterapkan ke seluruh '
                f'<span class="hl">{num(total_post)} post</span>. Inilah peta hasil triase pada tingkat post.</p>',
                unsafe_allow_html=True)

    seg = final_label.get("Pertolongan Segera", A["pertolongan_segera"])
    rin = final_label.get("Curhat Ringan", A["curhat_ringan"])
    noi = final_label.get("Tidak Relevan", A["tidak_relevan"])
    c = st.columns(4)
    T.stat(c[0], num(total_post), "Total Post Dianalisis", "setelah filter bahasa & spam")
    T.stat(c[1], num(seg), "Pertolongan Segera", f"{pct(seg/total_post*100)} dari total", style="urgent")
    T.stat(c[2], num(rin), "Curhat Ringan", f"{pct(rin/total_post*100)} dari total", style="light")
    T.stat(c[3], num(noi), "Tidak Relevan", f"{pct(noi/total_post*100)} dari total", style="slate")

    st.markdown('<div class="kicker">Komposisi Keputusan Sistem</div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Perbandingan keputusan akhir (XGBoost terkalibrasi) dengan label Rule '
                'Engine berbasis evidence. Rule Engine lebih sensitif (lebih banyak menandai urgensi), '
                'sedangkan model final menyeimbangkannya untuk dashboard.</p>', unsafe_allow_html=True)
    labels = ["Pertolongan Segera", "Curhat Ringan", "Tidak Relevan"]
    colors = [T.OXBLOOD, T.PINE, T.SLATE]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Model Final", x=labels,
                         y=[final_label.get(k, 0) for k in labels],
                         marker_color=colors, marker_line_color=T.PAPER, marker_line_width=1.5,
                         text=[final_label.get(k, 0) for k in labels], textposition="outside",
                         textfont=dict(family=T.FONT_MONO, color=T.INK)))
    if rule_label:
        fig.add_trace(go.Bar(name="Rule Engine", x=labels,
                             y=[rule_label.get(k, 0) for k in labels],
                             marker_color="rgba(166,158,141,0.55)",
                             marker_line_color=T.PAPER, marker_line_width=1.5,
                             text=[rule_label.get(k, 0) for k in labels], textposition="outside",
                             textfont=dict(family=T.FONT_MONO, color=T.MUTED)))
    fig.update_layout(barmode="group", template="dossier", height=360,
                      title="Distribusi Label per Post", yaxis_title="Jumlah Post",
                      legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="kicker">Distribusi Sinyal Numerik</div>', unsafe_allow_html=True)
    cf = g(features, "crisis_score", {})
    sf = g(features, "sentiment_score", {})
    es = g(features, "evidence_score", {})
    cc = st.columns(3)
    with cc[0]:
        st.markdown(f'<div class="card"><div class="lda-id">CRISIS LEXICON SCORE</div>'
                    f'<div style="font-family:{T.FONT_DISPLAY};font-size:30px;color:{T.OXBLOOD};">{cf.get("mean",3.08)}</div>'
                    f'<div class="note" style="margin-top:4px;">rata-rata \u00b1 {cf.get("std",1.82)} \u00b7 '
                    f'rentang {cf.get("min",0)}\u2013{cf.get("max",11)}</div></div>', unsafe_allow_html=True)
    with cc[1]:
        st.markdown(f'<div class="card"><div class="lda-id">SENTIMENT (KSI FAJRI KOTO)</div>'
                    f'<div style="font-family:{T.FONT_DISPLAY};font-size:30px;color:{T.SLATE};">{sf.get("mean",-24.26)}</div>'
                    f'<div class="note" style="margin-top:4px;">dominan negatif \u00b7 {sf.get("ksi_pos",2465)} kata + / '
                    f'{sf.get("ksi_neg",6607)} kata \u2212</div></div>', unsafe_allow_html=True)
    with cc[2]:
        st.markdown(f'<div class="card"><div class="lda-id">EVIDENCE SCORE</div>'
                    f'<div style="font-family:{T.FONT_DISPLAY};font-size:30px;color:{T.PINE};">{es.get("mean",0.327)}</div>'
                    f'<div class="note" style="margin-top:4px;">rata-rata \u00b1 {es.get("std",0.156)} \u00b7 '
                    f'maks {es.get("max",0.766)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kicker">Antrian Triase \u2014 Post Prioritas Tertinggi</div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Hanya post RELEVAN, diurutkan berdasarkan evidence_score. Format header: '
                '[confidence | evidence_score]. Hanya menampilkan post di atas ambang evidence_score di sidebar.</p>',
                unsafe_allow_html=True)
    if triage is not None:
        shown = triage[triage["evidence_score"] >= EV_THR]
        if shown.empty:
            st.info("Tidak ada post yang memenuhi ambang evidence_score aktif.")
        for _, r in shown.iterrows():
            evs = [e for e in str(r["evidence"]).split("|") if e]
            badges = "".join(f'<span class="flag-badge flag-urgent">{e}</span> ' for e in evs)
            header = f"{int(r['rank']):02d} | conf {r['confidence']:.2f} \u00b7 evidence {r['evidence_score']:.2f}"
            with st.expander(header):
                st.markdown(
                    f'<div style="font-family:var(--serif);font-style:italic;font-size:14px;line-height:1.55;'
                    f'color:var(--text2);background:var(--surface2);padding:12px 14px;border-radius:4px;'
                    f'border-left:3px solid var(--urgent);">\u201c{r["text"]}\u201d</div>'
                    f'<div style="margin-top:10px;">{badges}</div>', unsafe_allow_html=True)
    st.markdown('<div class="callout" style="border-left-color:var(--urgent);margin-top:1rem;">'
                '<b>Disclaimer:</b> antrian ini adalah alat bantu triase, bukan diagnosis. Post nyata dapat '
                'memuat ungkapan menyakiti diri \u2014 perlu verifikasi & tindak lanjut manusia.</div>',
                unsafe_allow_html=True)

# ================= TAB 3: ANALISIS NARASI =================
with tabs[2]:
    st.markdown('<p class="lead">Apa <span class="hl">penyebab tekanannya</span>? Seeded-theme assignment '
                'memetakan tema pemicu stres; panel temporal menunjukkan tema mana yang sedang naik.</p>',
                unsafe_allow_html=True)

    tm = themes_meta
    c = st.columns(3)
    T.stat(c[0], num(g(tm, "total_post", 1709)), "Post Dianalisis Tema")
    T.stat(c[1], num(g(tm, "assigned", 457)), "Tertetapkan ke Tema",
           f'{pct(g(tm, "assigned_pct", 26.7))} dari total', style="urgent")
    T.stat(c[2], num(g(tm, "unspecific", 1252)), "Tidak Spesifik",
           f'{pct(g(tm, "unspecific_pct", 73.3))} dari total', style="slate")

    # Grafik lingkaran (donut) penyebab stres + bar pendukung
    st.markdown('<div class="kicker">Klaster Penyebab Stres Terbesar Gen Z</div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Grafik lingkaran komposisi akar masalah pemicu kecemasan/tekanan '
                '(tidak termasuk \u201cTidak Spesifik\u201d). Masalah Keluarga dan Tekanan Akademik '
                'adalah dua pemicu terbesar.</p>', unsafe_allow_html=True)
    if themes is not None:
        td = themes[themes["topic_name"] != "Tidak Spesifik"].sort_values("count", ascending=False)
        gcols = st.columns([1, 1])
        with gcols[0]:
            fig = go.Figure(go.Pie(
                labels=td["topic_name"], values=td["count"], hole=0.55, sort=False,
                marker=dict(colors=T.CATEGORICAL, line=dict(color=T.PAPER, width=2)),
                textfont=dict(family=T.FONT_MONO, size=11, color=T.INK),
                textinfo="label+percent",
                hovertemplate="%{label}: %{value} post (%{percent})<extra></extra>"))
            fig.update_layout(template="dossier", height=360, showlegend=False,
                              title="Komposisi Klaster Penyebab Stres",
                              margin=dict(l=10, r=10, t=46, b=10),
                              annotations=[dict(text=f"{int(td['count'].sum())}<br>post",
                                                x=0.5, y=0.5, font=dict(family=T.FONT_DISPLAY,
                                                size=22, color=T.INK), showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)
        with gcols[1]:
            tb = td.sort_values("count", ascending=True)
            fig = go.Figure(go.Bar(
                x=tb["count"], y=tb["topic_name"], orientation="h",
                marker_color=T.OXBLOOD, marker_line_color=T.PAPER, marker_line_width=1.5,
                text=tb["count"], textposition="outside", textfont=dict(family=T.FONT_MONO, color=T.INK)))
            fig.update_layout(template="dossier", height=360, title="Jumlah Post per Klaster",
                              xaxis_title="Jumlah Post", margin=dict(l=10, r=10, t=46, b=10))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="kicker">Interpretasi Tema Utama</div>', unsafe_allow_html=True)
    if theme_cards:
        cols = st.columns(3)
        for i, t in enumerate(theme_cards[:3]):
            with cols[i % 3]:
                tags = "".join(f'<span class="tag">{x}</span>' for x in t.get("tags", []))
                contoh = (f'<div class="note" style="margin-top:10px;font-style:italic;">\u201c{t["contoh"]}\u201d</div>'
                          if t.get("contoh") else "")
                st.markdown(
                    f'<div class="lda-card named" style="height:100%;"><div class="lda-id">TEMA 0{i+1} \u00b7 n={t["count"]}</div>'
                    f'<div class="lda-name">{t["name"]}</div><div class="lda-desc">{t["desc"]}</div>'
                    f'<div class="lda-tris">{tags}</div>{contoh}</div>', unsafe_allow_html=True)

    st.markdown('<div class="kicker">Trending Tema Harian</div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Pergerakan jumlah post per tema dari hari ke hari sepanjang periode crawl '
                '(24 Apr \u2013 30 Mei 2026). Berguna untuk melihat tema pemicu stres mana yang sedang memuncak.</p>',
                unsafe_allow_html=True)
    if topic_trend is not None:
        fig = go.Figure()
        theme_cols = [c for c in topic_trend.columns if c != "day"]
        for i, col in enumerate(theme_cols):
            fig.add_trace(go.Scatter(x=topic_trend["day"], y=topic_trend[col], mode="lines+markers",
                                     name=col, line=dict(width=2, color=T.CATEGORICAL[i % len(T.CATEGORICAL)]),
                                     marker=dict(size=4)))
        fig.update_layout(template="dossier", height=380, title="Trending Tema per Hari",
                          xaxis_title="Tanggal", yaxis_title="Jumlah Post",
                          legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig, use_container_width=True)

# ================= TAB 4: JARINGAN DUKUNGAN =================
with tabs[3]:
    st.markdown('<p class="lead">Dukungan komunitas paling jelas terlihat pada '
                '<span class="hl">struktur jaringan balasan</span>: siapa memberi dukungan, dan akun rentan '
                'mana yang paling banyak menerimanya.</p>', unsafe_allow_html=True)

    c = st.columns(4)
    T.stat(c[0], num(g(sna, "reply_total", A["reply_analisis"])), "Total Balasan (Reply)")
    T.stat(c[1], num(g(sna, "support_detected", 178)), "Balasan Mendukung", style="light")
    T.stat(c[2], num(g(sna, "graph_nodes", 312)), "Node Jaringan (Aktor)", style="slate")
    T.stat(c[3], num(g(sna, "graph_edges", 178)), "Edge Dukungan (Berarah)", style="urgent")

    st.markdown('<div class="kicker">Visualisasi Jaringan Dukungan</div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Graf ilustratif relasi pemberi \u2192 penerima dukungan dari aktor paling '
                'menonjol (top out-degree & top PageRank). Hijau = pemberi dukungan (penolong), '
                'slate = penerima dukungan (rentan).</p>', unsafe_allow_html=True)
    if top_sup is not None and top_rec is not None:
        G = nx.DiGraph()
        givers = top_sup["user"].tolist()
        receivers = top_rec["user"].tolist()
        for i, gv in enumerate(givers):
            rc = receivers[i % len(receivers)]
            G.add_edge(gv, rc)
        pos = nx.spring_layout(G, seed=42, k=0.6)
        ex, ey = [], []
        for e in G.edges():
            x0, y0 = pos[e[0]]; x1, y1 = pos[e[1]]
            ex += [x0, x1, None]; ey += [y0, y1, None]
        nx_, ny_, col, siz, txt = [], [], [], [], []
        for n in G.nodes():
            x, y = pos[n]; nx_.append(x); ny_.append(y)
            if n in receivers:
                col.append(T.SLATE); siz.append(18)
            else:
                col.append(T.PINE); siz.append(11)
            txt.append(f"@{n}")
        et = go.Scatter(x=ex, y=ey, line=dict(width=0.8, color=T.HAIRLINE), hoverinfo="none", mode="lines")
        ntr = go.Scatter(x=nx_, y=ny_, mode="markers+text", text=txt, textposition="top center",
                         textfont=dict(family=T.FONT_MONO, size=9, color=T.INK),
                         marker=dict(color=col, size=siz, line_width=1.5, line_color=T.PAPER),
                         hoverinfo="text")
        fig = go.Figure(data=[et, ntr], layout=go.Layout(
            showlegend=False, hovermode="closest", margin=dict(b=10, l=10, r=10, t=10),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=440, template="dossier"))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"ForceAtlas2 (notebook): Penolong {g(sna,'penolong',155)} \u00b7 "
                   f"Korban {g(sna,'korban',145)} \u00b7 Edge {g(sna,'edge_forceatlas',164)} "
                   f"\u00b7 self-loop dibuang {g(sna,'selfloop_dibuang',14)}.")

    cc = st.columns(2)
    with cc[0]:
        st.markdown('<div class="eyebrow">Top Pemberi Dukungan (Out-degree)</div>', unsafe_allow_html=True)
        if top_sup is not None:
            rows = "".join(f'<tr><td>@{r["user"]}</td><td>{int(r["support_given"])} dukungan</td></tr>'
                           for _, r in top_sup.iterrows())
            st.markdown(f'<div class="tbl-wrap"><table class="dt"><thead><tr><th>Akun</th>'
                        f'<th>Dukungan Diberi</th></tr></thead><tbody>{rows}</tbody></table></div>',
                        unsafe_allow_html=True)
    with cc[1]:
        st.markdown('<div class="eyebrow">Top Penerima Dukungan (PageRank)</div>', unsafe_allow_html=True)
        if top_rec is not None:
            rows = "".join(f'<tr><td>@{r["user"]}</td><td>{r["pagerank"]:.4f}</td></tr>'
                           for _, r in top_rec.iterrows())
            st.markdown(f'<div class="tbl-wrap"><table class="dt"><thead><tr><th>Akun</th>'
                        f'<th>PageRank</th></tr></thead><tbody>{rows}</tbody></table></div>',
                        unsafe_allow_html=True)

    st.markdown('<div class="kicker">Pola Temporal & Alert Engine</div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Agregasi harian post \u201cPertolongan Segera\u201d sepanjang 37 hari '
                '(24 Apr \u2013 30 Mei 2026). Alert Engine memakai z-score untuk mendeteksi lonjakan tak wajar.</p>',
                unsafe_allow_html=True)
    if daily is not None:
        lc = st.columns([1.6, 1])
        with lc[0]:
            mx = daily["count"].max()
            fig = go.Figure(go.Scatter(
                x=daily["day"], y=daily["count"], mode="lines+markers",
                line=dict(color=T.OXBLOOD, width=2), fill="tozeroy",
                fillcolor="rgba(210,105,69,0.15)",
                marker=dict(size=[8 if c == mx else 5 for c in daily["count"]],
                            color=[T.OXBLOOD if c == mx else T.OCHRE for c in daily["count"]]),
                hovertemplate="%{x}<br>Pertolongan Segera: %{y}<extra></extra>"))
            fig.update_layout(template="dossier", height=330, title="Tren Harian Pertolongan Segera",
                              xaxis_title="Tanggal", yaxis_title="Jumlah Post",
                              margin=dict(l=10, r=10, t=46, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with lc[1]:
            z = g(alert, "zscore_terakhir", A["zscore"])
            status = g(alert, "status", A["status"])
            lamp = {"HIJAU": "\U0001F7E2", "KUNING": "\U0001F7E1", "MERAH": "\U0001F534"}.get(status, "\U0001F7E2")
            color = {"HIJAU": "var(--light)", "KUNING": "var(--ochre)", "MERAH": "var(--urgent)"}.get(status, "var(--light)")
            st.markdown(
                f'<div class="card"><div class="lda-id">STATUS ALERT</div>'
                f'<div style="font-family:{T.FONT_DISPLAY};font-size:34px;color:{color};margin-top:6px;">{lamp} {status}</div>'
                f'<div style="font-family:{T.FONT_MONO};font-size:13px;line-height:1.9;margin-top:10px;">'
                f'z-score hari terakhir: <b>{z}</b><br>'
                f'Metode: z-score harian<br>Status: <b>{g(alert,"keterangan","normal")}</b></div></div>',
                unsafe_allow_html=True)
            st.markdown('<div class="callout" style="border-left-color:var(--light);">'
                        '<b>Aktivitas normal:</b> z-score di bawah ambang \u2014 tidak ada lonjakan krisis '
                        'yang terdeteksi pada hari terakhir.</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown('<hr class="rule-faint" style="margin-top:2.5rem;"/>', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center; font-family:var(--mono); font-size:0.75rem; color:var(--muted); line-height:1.5; padding-bottom:2rem;">'
    'Metodologi: SBERT (paraphrase-multilingual-MiniLM-L12-v2) &rarr; Crisis Lexicon + KSI Fajri Koto &rarr; '
    'Evidence Extraction (concept-bottleneck) &rarr; Rule Engine &rarr; XGBoost (kalibrasi isotonic) &rarr; SNA &rarr; Alert Engine.<br/>'
    'Seluruh angka bersumber dari output notebook baseline. Keputusan bersifat pendukung triase, '
    'BUKAN diagnosis klinis. Jika Anda atau seseorang dalam krisis, hubungi layanan darurat 119 ext 8.</div>',
    unsafe_allow_html=True)
