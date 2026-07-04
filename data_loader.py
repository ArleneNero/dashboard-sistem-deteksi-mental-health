"""Resolusi & pembacaan data dashboard kesehatan mental.

Semua angka berasal dari output NYATA notebook
'Sistem Monitoring Isu Kesehatan Mental di X/Twitter' (baseline architecture).
File data ada di: data/MENTAL_HEALTH_DATA/ (CSV + JSON).

Tidak ada MODE DEMO yang mengarang data: bila folder data hilang, dashboard
memakai konstanta otoritatif yang identik dengan output notebook (AUTH).
"""
import os, json, functools
import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))

# Angka otoritatif (identik dengan output notebook) -> fallback bila file hilang.
AUTH = dict(
    total_post=1899, raw_rows=1902, after_lang=1900, after_spam=1899,
    root=850, reply=1052, reply_analisis=1051, anchor=1707,
    pertolongan_segera=119, curhat_ringan=1736, tidak_relevan=44,
    pertolongan_pct=6.3, curhat_pct=91.4, relevan_pct=2.3,
    rule_threshold=0.45, sbert_dim=384,
    kappa=0.816, cv_acc=0.845, cv_macrof1=0.614,
    zscore=-0.44, status="HIJAU",
)


@functools.lru_cache(maxsize=1)
def _root():
    """Kembalikan (root_dir, is_missing)."""
    p = os.path.join(HERE, "data", "MENTAL_HEALTH_DATA")
    if os.path.isdir(p):
        return p, False
    return None, True


def is_missing():
    return _root()[1]


def _path(name):
    root, miss = _root()
    if miss or not root:
        return None
    p = os.path.join(root, name)
    return p if os.path.exists(p) else None


def csv(name):
    p = _path(name)
    if p:
        try:
            return pd.read_csv(p)
        except Exception:
            return None
    return None


def js(name):
    p = _path(name)
    if p:
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return {}
    return {}
