# Berkas Klinis — Dashboard Monitoring Isu Kesehatan Mental di X/Twitter

Dashboard Streamlit untuk memvisualisasikan hasil **Sistem Monitoring Isu Kesehatan Mental** (Evidence-Based Decision Support System) dari notebook mental health.

Struktur, gaya visual ("Clinical Dossier" — warm-paper, editorial cetak), dan pola interaksi mengikuti dashboard referensi (deteksi buzzer), namun **seluruh konteks, data, label, dan narasi telah disesuaikan untuk domain kesehatan mental**.

> ⚠️ Seluruh angka pada dashboard ini bersumber dari **output nyata notebook** (folder `hasil_monitoring/`). Tidak ada data yang dikarang. File data ada di `data/MENTAL_HEALTH_DATA/`.

## Cara menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Lalu buka http://localhost:8501

## Struktur

```
dashboard/
├── app.py              # Aplikasi utama (4 tab)
├── theme.py            # Tema visual 'Clinical Dossier'
├── data_loader.py      # Pembacaan data + fallback konstanta otoritatif
├── requirements.txt
├── .streamlit/config.toml
└── data/MENTAL_HEALTH_DATA/   # Data NYATA hasil notebook (17 file)
```

## Empat Tab (dipetakan dari referensi)

| Referensi (Buzzer) | Dashboard ini (Mental Health) |
|---|---|
| 01 Validasi Model | **01 Validasi Sistem** — pipeline, Cohen's Kappa, 5-fold CV, confusion matrix TEST, kalibrasi, baseline vs rule engine, kekuatan evidence |
| 02 Hasil Investigasi | **02 Hasil Monitoring** — komposisi label, distribusi sinyal, antrian triase |
| 03 Analisis Narasi | **03 Analisis Narasi** — grafik lingkaran klaster penyebab stres + trending tema harian (35 hari) |
| 04 Jaringan Serangan | **04 Jaringan Dukungan** — SNA dukungan komunitas, PageRank, alert engine (37 hari) |

## Data temporal lengkap

Versi ini memuat **seri waktu penuh** hasil regenerasi dari file output:
- `topic_trend.csv`: 35 hari (24 Apr – 30 Mei 2026), 7 tema bernama — direkonstruksi dengan join `05_clusters.csv` × tanggal post `01_clean_df.csv`.
- `daily_urgent.csv`: 37 hari penuh dari `08_daily_urgent.csv`.

## Catatan etis

Keputusan sistem bersifat **pendukung triase, bukan diagnosis klinis**. Sistem sengaja memprioritaskan recall kelas "Pertolongan Segera" (82,4%) — lebih baik over-triage daripada melewatkan sinyal krisis. Konten post nyata dapat memuat ungkapan menyakiti diri dan perlu verifikasi serta tindak lanjut manusia.
