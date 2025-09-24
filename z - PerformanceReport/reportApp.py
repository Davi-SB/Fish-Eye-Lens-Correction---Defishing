# app.py
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

# ---------------------------
# Configuração da Página
# ---------------------------
st.set_page_config(page_title="Relatório de Performance | Detecção de Objetos", layout="wide")

# ---------------------------
# Utilidades
# ---------------------------
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}

def find_images_in_dir(root: str) -> List[str]:
    """Lista recursivamente imagens no diretório."""
    p = Path(root).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        return []
    files = []
    for ext in IMAGE_EXTS:
        files.extend([str(pp) for pp in p.rglob(f"*{ext}")])
    files = sorted(files, key=lambda x: x.lower())
    return files

def sanitize_name(name: str) -> str:
    """Remove caracteres inválidos para nome de arquivo."""
    name = name.strip()
    return re.sub(r'[\\/*?:"<>|]+', "_", name) or "report"

def unique_report_path(report_name: str, reports_dir="z - reports") -> str:
    """Gera caminho único para salvar CSV no diretório reports/, sem sobrescrever."""
    os.makedirs(reports_dir, exist_ok=True)
    base = sanitize_name(report_name)
    path = os.path.join(reports_dir, f"{base}.csv")
    if not os.path.exists(path):
        return path
    i = 1
    while True:
        candidate = os.path.join(reports_dir, f"{base} ({i}).csv")
        if not os.path.exists(candidate):
            return candidate
        i += 1

def init_counts_for_images(images: List[str]) -> Dict[str, Dict[str, int]]:
    """Inicializa dicionário de contagens para cada imagem."""
    return {img: {"tp": 0, "fp": 0, "fn": 0} for img in images}

def get_image_name(path: str) -> str:
    return Path(path).name

def save_report(images: List[str], counts: Dict[str, Dict[str, int]], report_name: str) -> Tuple[str, pd.DataFrame]:
    """Salva CSV no formato exigido e retorna caminho salvo e DataFrame."""
    rows = []
    for img in images:
        c = counts.get(img, {"tp": 0, "fp": 0, "fn": 0})
        rows.append({
            "imagem": get_image_name(img),
            "verdadeiros_positivos": int(c.get("tp", 0)),
            "falsos_positivos": int(c.get("fp", 0)),
            "falsos_negativos": int(c.get("fn", 0)),
            "caminho": st.session_state.img_dir.strip("/\\") + "/" + os.path.relpath(img, st.session_state.img_dir).replace("\\", "/")
        })
    df = pd.DataFrame(rows, columns=["imagem", "verdadeiros_positivos", "falsos_positivos", "falsos_negativos", "caminho"])

    out_path = unique_report_path(report_name)
    df.to_csv(out_path, index=False, encoding="utf-8")
    return out_path, df

# ---------------------------
# Estado da Sessão
# ---------------------------
if "images" not in st.session_state:
    st.session_state.images = []

if "counts" not in st.session_state:
    st.session_state.counts = {}

if "idx" not in st.session_state:
    st.session_state.idx = 0

if "report_name" not in st.session_state:
    st.session_state.report_name = ""

if "img_dir" not in st.session_state:
    st.session_state.img_dir = ""

# ---------------------------
# Header
# ---------------------------
st.title("📊 Relatório de Performance — Detecção de Objetos")

# ---------------------------
# Criar Novo Report
# ---------------------------
with st.form("setup_form", clear_on_submit=False):
    st.markdown("#### 1) Configuração Inicial")
    colA, colB = st.columns([2, 1])
    with colA:
        img_dir = st.text_input(
            "Diretório inicial das imagens (caminho local):",
            value=st.session_state.img_dir or "",
            placeholder=r"C:\caminho\para\imagens  ou  /home/user/imagens"
        )
    with colB:
        report_name = st.text_input(
            "Nome do report:",
            value=st.session_state.report_name or "",
            placeholder="ex.: avaliacao_modelo_setembro"
        )
    submitted = st.form_submit_button("Carregar imagens")

if submitted:
    st.session_state.img_dir = img_dir.strip()
    st.session_state.report_name = report_name.strip()

    if not st.session_state.img_dir:
        st.error("Informe o diretório das imagens.")
    elif not os.path.isdir(st.session_state.img_dir):
        st.error("Diretório inválido ou inexistente.")
    elif not st.session_state.report_name:
        st.error("Informe o nome do report.")
    else:
        images = find_images_in_dir(st.session_state.img_dir)
        st.session_state.images = images
        st.session_state.idx = 0
        st.session_state.counts = init_counts_for_images(images)
        if not images:
            st.warning("Nenhuma imagem encontrada nesse diretório (busca recursiva).")
        else:
            st.success(f"Encontradas {len(images)} imagens.")

# Se já há imagens carregadas, mostra a interface de anotação
if st.session_state.images:
    st.markdown("#### 2) Avaliação")
    total = len(st.session_state.images)
    idx = st.session_state.idx
    current_path = st.session_state.images[idx]
    current_counts = st.session_state.counts.get(current_path, {"tp": 0, "fp": 0, "fn": 0})

    # Barra de progresso + status
    st.progress((idx + 1) / total)
    st.caption(f"Imagem {idx + 1} de {total}")
    st.write(f"**Arquivo:** `{get_image_name(current_path)}`")
    st.write(f"**Caminho:** `{current_path}`")

    # ==== LADO A LADO: Imagem ⟷ Form ====
    col_img, col_form = st.columns(2)
    with col_img:
        st.image(current_path, use_container_width=True)

    with col_form:
        with st.form(key=f"form_img_{idx}", clear_on_submit=False):
            st.markdown("##### Contagens desta imagem")
            tp = st.number_input(
                "Verdadeiros Positivos (VP) - Mochilas corretamente detectadas com **confiança >= 45%**",
                min_value=0, step=1, value=int(current_counts.get("tp", 0))
            )
            fn = st.number_input(
                "Falsos Negativos (FN) - Mochilas que **não foram vistas** ou que foram vistas com **confiança < 45%**",
                min_value=0, step=1, value=int(current_counts.get("fn", 0))
            )
            fp = st.number_input(
                "Falsos Positivos (FP) - Alucinações, modelo vendo quaisquer outro objeto que não deveria com **confiança >= 45%**",
                min_value=0, step=1, value=int(current_counts.get("fp", 0))
            )

            st.divider()
            b1, b2, b3 = st.columns(3)
            go_prev = b1.form_submit_button("◀️ Salvar e Anterior", use_container_width=True)
            save_only = b2.form_submit_button("💾 Salvar", use_container_width=True)
            go_next = b3.form_submit_button("Salvar e Próxima ▶️", use_container_width=True)
            finish   = st.form_submit_button("✅ Finalizar & Exportar CSV", use_container_width=True)

    # Aplicar ações conforme botão
    def _save_current_counts():
        st.session_state.counts[current_path] = {"tp": int(tp), "fp": int(fp), "fn": int(fn)}

    if 'tp' in locals() and 'fp' in locals() and 'fn' in locals():
        if go_prev:
            _save_current_counts()
            if st.session_state.idx > 0:
                st.session_state.idx -= 1
            st.rerun()

        if save_only:
            _save_current_counts()
            st.success("Contagens salvas para esta imagem.")

        if go_next:
            _save_current_counts()
            if st.session_state.idx < total - 1:
                st.session_state.idx += 1
            st.rerun()

        # Resumo parcial (opcional)
        with st.expander("Resumo parcial do report (pré-visualização)", expanded=False):
            rows_prev = []
            for img in st.session_state.images:
                c = st.session_state.counts.get(img, {"tp": 0, "fp": 0, "fn": 0})
                rows_prev.append({
                    "imagem": get_image_name(img),
                    "verdadeiros_positivos": int(c.get("tp", 0)),
                    "falsos_positivos": int(c.get("fp", 0)),
                    "falsos_negativos": int(c.get("fn", 0)),
                    "caminho": st.session_state.img_dir.strip("/\\") + "/" + os.path.relpath(img, st.session_state.img_dir).replace("\\", "/")
                })
            df_prev = pd.DataFrame(rows_prev)
            st.dataframe(df_prev, use_container_width=True, hide_index=True)

        # Finalizar e Exportar
        if finish:
            _save_current_counts()
            out_path, df_saved = save_report(st.session_state.images, st.session_state.counts, st.session_state.report_name)
            st.success(f"Report salvo em: `{out_path}`")
            csv_bytes = df_saved.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar CSV agora", data=csv_bytes, file_name=Path(out_path).name, mime="text/csv")
