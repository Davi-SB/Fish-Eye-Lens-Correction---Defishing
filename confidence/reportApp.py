# compare_two_reports_vs_gabarito.py
import json
import math
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# =============================
# CONFIG (edite aqui)
# =============================
PATH_GABARITO = r"confidence\GABARITO_DATA_GERAL.csv"        # CSV com colunas: Image, count
PATH_REPORT_A = r"confidence\rawImages - oldYOLO\report.json"       # JSON: {"image_000.jpg": [0.77, 0.36, ...], ...}
PATH_REPORT_B = r"confidence\CorrectedImages - YOLO11x\report.json"       # JSON idem
THRESHOLD     = 0.45                     # confiança mínima para contar uma mochila

st.set_page_config(page_title="Comparador: Dois Reports × Gabarito", layout="wide")

# =============================
# Funções auxiliares
# =============================
EXPECTED_GT = ["Image", "count"]

def load_gabarito(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';')
    missing = [c for c in EXPECTED_GT if c not in df.columns]
    if missing:
        raise ValueError(f"GABARITO.csv precisa conter as colunas {EXPECTED_GT} (faltando: {missing})")
    df = df.rename(columns={"Image": "imagem", "count": "gt_count"})
    df["imagem"] = df["imagem"].astype(str)
    df["gt_count"] = pd.to_numeric(df["gt_count"], errors="coerce").fillna(0).astype(int)
    return df[["imagem", "gt_count"]]

def load_report_json(path: str) -> Dict[str, List[float]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out: Dict[str, List[float]] = {}
    for k, v in data.items():
        if isinstance(v, list):
            vals = []
            for x in v:
                try:
                    vals.append(float(x))
                except Exception:
                    pass
            out[str(k)] = vals
        else:
            out[str(k)] = []
    return out

def preds_count_from_confidences(conf_list: List[float], thr: float) -> int:
    return int(sum(1 for c in conf_list if c >= thr))

def compute_per_image(df_gt: pd.DataFrame, det_map: Dict[str, List[float]], thr: float) -> pd.DataFrame:
    """
    Retorna DataFrame com: imagem, gt_count, pred_count, tp, fp, fn, diff_pred_minus_gt
    Universo de imagens = união (gabarito ∪ chaves do report)
    """
    imgs = sorted(set(df_gt["imagem"].tolist()) | set(map(str, det_map.keys())))
    rows = []
    gt_lookup = dict(zip(df_gt["imagem"], df_gt["gt_count"]))
    for img in imgs:
        gt = int(gt_lookup.get(img, 0))
        confs = det_map.get(img, [])
        pred = preds_count_from_confidences(confs, thr)

        tp = min(gt, pred)
        fp = max(0, pred - gt)
        fn = max(0, gt - pred)

        rows.append({
            "imagem": img,
            "gt_count": gt,
            "pred_count": pred,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "diff_pred_minus_gt": pred - gt
        })
    return pd.DataFrame(rows)

def safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if b not in (0, 0.0, np.nan) and b == b else np.nan

def micro_metrics(tp_sum: int, fp_sum: int, fn_sum: int) -> Tuple[float, float, float]:
    precision = safe_div(tp_sum, tp_sum + fp_sum)
    recall    = safe_div(tp_sum, tp_sum + fn_sum)
    f1        = safe_div(2 * tp_sum, 2 * tp_sum + fp_sum + fn_sum)
    return precision, recall, f1

def per_row_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["precision"] = out.apply(lambda r: safe_div(r["tp"], r["tp"] + r["fp"]), axis=1)
    out["recall"]    = out.apply(lambda r: safe_div(r["tp"], r["tp"] + r["fn"]), axis=1)
    out["f1"]        = out.apply(lambda r: safe_div(2 * r["tp"], 2 * r["tp"] + r["fp"] + r["fn"]), axis=1)
    return out

def macro_metrics(per_row_df: pd.DataFrame) -> Tuple[float, float, float]:
    return (
        per_row_df["precision"].mean(skipna=True),
        per_row_df["recall"].mean(skipna=True),
        per_row_df["f1"].mean(skipna=True),
    )

def count_error_metrics(per_img_df: pd.DataFrame) -> Tuple[float, float]:
    diff = (per_img_df["pred_count"] - per_img_df["gt_count"]).astype(float)
    mae  = float(np.abs(diff).mean()) if len(diff) else np.nan
    rmse = float(np.sqrt((diff ** 2).mean())) if len(diff) else np.nan
    return mae, rmse

def style_pct(x: float) -> str:
    return "-" if pd.isna(x) else f"{100*x:.2f}%"

def verdict_line(name_a: str, name_b: str, val_a: float, val_b: float, label: str) -> str:
    if pd.isna(val_a) and pd.isna(val_b):
        return f"{label}: sem dados suficientes."
    if pd.isna(val_a):
        return f"{label}: {name_b} venceu (valor de {name_a} indisponível)."
    if pd.isna(val_b):
        return f"{label}: {name_a} venceu (valor de {name_b} indisponível)."
    if abs(val_a - val_b) < 1e-12:
        return f"{label}: empate."
    return f"{label}: {'A' if val_a > val_b else 'B'} venceu ({name_a if val_a > val_b else name_b})."

# =============================
# UI — Cabeçalho
# =============================
st.title("📊 Dois Reports × Gabarito (contagem por threshold)")
c1, c2, c3 = st.columns([3, 3, 1.5])
with c1:
    st.info(f"**Gabarito**: `{Path(PATH_GABARITO).resolve()}`")
with c2:
    st.info(f"**Reports**: `{Path(PATH_REPORT_A).name}` e `{Path(PATH_REPORT_B).name}`")
with c3:
    st.info(f"**Threshold**: `{THRESHOLD:.2f}`")

# =============================
# Carregamento e cálculo
# =============================
try:
    df_gt = load_gabarito(PATH_GABARITO)
    det_map_A = load_report_json(PATH_REPORT_A)
    det_map_B = load_report_json(PATH_REPORT_B)
except Exception as e:
    st.error(f"Erro ao carregar arquivos: {e}")
    st.stop()

dfA = compute_per_image(df_gt, det_map_A, THRESHOLD)
dfB = compute_per_image(df_gt, det_map_B, THRESHOLD)

# Resumos individuais
def summarize(label: str, df: pd.DataFrame) -> Dict[str, float]:
    tp_sum = int(df["tp"].sum())
    fp_sum = int(df["fp"].sum())
    fn_sum = int(df["fn"].sum())
    pred_sum = int(df["pred_count"].sum())
    gt_sum = int(df["gt_count"].sum())
    prec_mi, rec_mi, f1_mi = micro_metrics(tp_sum, fp_sum, fn_sum)
    per_row = per_row_metrics(df)
    prec_ma, rec_ma, f1_ma = macro_metrics(per_row)
    mae, rmse = count_error_metrics(df)
    return dict(
        label=label,
        n_imagens=len(df),
        gt_sum=gt_sum,
        pred_sum=pred_sum,
        tp_sum=tp_sum,
        fp_sum=fp_sum,
        fn_sum=fn_sum,
        prec_mi=prec_mi, rec_mi=rec_mi, f1_mi=f1_mi,
        prec_ma=prec_ma, rec_ma=rec_ma, f1_ma=f1_ma,
        mae=mae, rmse=rmse
    )

sumA = summarize("A", dfA)
sumB = summarize("B", dfB)

# =============================
# Lado a lado (inspirado em compare_reports.py)
# =============================
colA, colB = st.columns(2)
for (s, col) in [(sumA, colA), (sumB, colB)]:
    with col:
        st.subheader(f"Resumo — Report {s['label']}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Imagens", s["n_imagens"])
        m2.metric("Objetos (GT)", s["gt_sum"])
        m3.metric("Previstos", s["pred_sum"])

        m4, m5, m6 = st.columns(3)
        m4.metric("TP", s["tp_sum"])
        m5.metric("FP", s["fp_sum"])
        m6.metric("FN", s["fn_sum"])

        st.markdown("**Métricas micro (globais):**")
        st.write(
            f"- Precision: {style_pct(s['prec_mi'])}  \n"
            f"- Recall: {style_pct(s['rec_mi'])}  \n"
            f"- F1: {style_pct(s['f1_mi'])}"
        )
        st.markdown("**Métricas macro (média por imagem):**")
        st.write(
            f"- Precision: {style_pct(s['prec_ma'])}  \n"
            f"- Recall: {style_pct(s['rec_ma'])}  \n"
            f"- F1: {style_pct(s['f1_ma'])}"
        )
        st.caption(f"Erros de contagem — MAE: {s['mae']:.2f} • RMSE: {s['rmse']:.2f}")

st.markdown("---")

# =============================
# Comparação simples (global)
# =============================
st.markdown("### 🧮 Comparação simples (global)")
nameA, nameB = "A", "B"
st.write(verdict_line(nameA, nameB, sumA["prec_mi"], sumB["prec_mi"], "Precision (micro)"))
st.write(verdict_line(nameA, nameB, sumA["rec_mi"],  sumB["rec_mi"],  "Recall (micro)"))
st.write(verdict_line(nameA, nameB, sumA["f1_mi"],   sumB["f1_mi"],   "F1 (micro)"))
st.write(verdict_line(nameA, nameB, -sumA["mae"],    -sumB["mae"],    "MAE (quanto MENOR melhor)"))
st.write(verdict_line(nameA, nameB, -sumA["rmse"],   -sumB["rmse"],   "RMSE (quanto MENOR melhor)"))

# =============================
# Tabela por imagem e deltas
# =============================
st.markdown("### 📋 Tabela por imagem (A × B)")

merged = pd.merge(
    dfA.add_suffix("_A"),
    dfB.add_suffix("_B"),
    left_on="imagem_A",
    right_on="imagem_B",
    how="outer",
    indicator=True
)

# coluna de identificação preferida
merged["imagem"] = merged["imagem_A"].fillna(merged["imagem_B"])

# métricas por imagem (A e B)
for side in ["A", "B"]:
    merged[f"precision_{side}"] = (merged[f"tp_{side}"] / (merged[f"tp_{side}"] + merged[f"fp_{side}"])).replace([np.inf], np.nan)
    merged[f"recall_{side}"]    = (merged[f"tp_{side}"] / (merged[f"tp_{side}"] + merged[f"fn_{side}"])).replace([np.inf], np.nan)
    merged[f"f1_{side}"]        = (2 * merged[f"tp_{side}"] / (2 * merged[f"tp_{side}"] + merged[f"fp_{side}"] + merged[f"fn_{side}"])).replace([np.inf], np.nan)

# deltas (B - A)
for col in ["pred_count", "tp", "fp", "fn", "precision", "recall", "f1", "diff_pred_minus_gt"]:
    merged[f"Δ{col}"] = merged.get(f"{col}_B") - merged.get(f"{col}_A")

# quem venceu por F1 na imagem
eps = 1e-12
merged["venceu_por_F1"] = np.where(merged["Δf1"] > eps, "B",
                            np.where(merged["Δf1"] < -eps, "A", "empate"))

cols_show = [
    "imagem",
    "gt_count_A","pred_count_A","tp_A","fp_A","fn_A","f1_A",
    "gt_count_B","pred_count_B","tp_B","fp_B","fn_B","f1_B",
    "Δpred_count","Δtp","Δfp","Δfn","Δf1","venceu_por_F1","_merge"
]
# garante colunas ausentes
for c in cols_show:
    if c not in merged.columns:
        merged[c] = np.nan

st.dataframe(merged[cols_show], use_container_width=True)

# =============================
# Indicadores de mudança + listas top
# =============================
st.markdown("### 📌 Indicadores")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Imagens com TP ↑ (B>A)", int((merged["Δtp"] > 0).sum()))
with c2:
    st.metric("Imagens com FP ↓ (B<A)", int((merged["Δfp"] < 0).sum()))
with c3:
    st.metric("Imagens com FN ↓ (B<A)", int((merged["Δfn"] < 0).sum()))
with c4:
    vc = merged["venceu_por_F1"].value_counts(dropna=False).to_dict()
    st.metric("Vencedor por F1 (contagem)", f"A:{vc.get('A',0)}  B:{vc.get('B',0)}  =:{vc.get('empate',0)}")

st.markdown("### 🟢 Maiores melhorias (ΔF1 > 0)")
improvements = merged.dropna(subset=["Δf1"]).sort_values("Δf1", ascending=False).head(10)
st.dataframe(improvements[cols_show], use_container_width=True)

st.markdown("### 🔴 Maiores regressões (ΔF1 < 0)")
regressions = merged.dropna(subset=["Δf1"]).sort_values("Δf1", ascending=True).head(10)
st.dataframe(regressions[cols_show], use_container_width=True)

# =============================
# Exportar CSV consolidado
# =============================
export_cols = cols_show
csv_bytes = merged[export_cols].to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Baixar comparação (CSV)", data=csv_bytes, file_name="comparacao_reports_vs_gabarito.csv", mime="text/csv")

with st.expander("🔎 Notas"):
    st.markdown(
        "- A comparação é por **contagem** (não há pareamento de boxes).  \n"
        "- `pred_count` = nº de confianças ≥ threshold.  \n"
        "- Por imagem: `tp=min(gt,pred)`, `fp=max(0,pred-gt)`, `fn=max(0,gt-pred)`.  \n"
        "- **Micro**: métricas globais agregando TP/FP/FN. **Macro**: média das métricas por imagem.  \n"
        "- Ajustar o `THRESHOLD` mudará `pred_count` e as métricas."
    )
