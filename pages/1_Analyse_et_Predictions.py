# pages/1_Analyse_et_Predictions.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import colonnes, api_ok, call_api_predict_json, call_api_predict_csv

# ----- CONFIG PAGE -----
st.set_page_config(page_title="Analyse & Prédictions", page_icon="📊", layout="wide")

# ----- STYLES -----
st.markdown("""
<style>
/* Cartes KPI */
.kpi { border:1px solid #eee; border-radius:16px; padding:14px;
       box-shadow:0 8px 20px rgba(0,0,0,0.06); text-align:center; }
.kpi h2 { margin:.25rem 0 0 0; }
.section { background:#fff; border:1px solid #eee; border-radius:16px; padding:16px;
           box-shadow:0 8px 20px rgba(0,0,0,0.04); }
/* Tableau : on laisse Streamlit gérer, mais on colore nous-mêmes via Styler */
</style>
""", unsafe_allow_html=True)

st.title("📊 Analyse & Prédictions")

# ----- RÉCUP SESSION (définie à l'accueil) -----
api_url    = st.session_state.get("api_url", "http://127.0.0.1:8000")
input_df   = st.session_state.get("input_df", None)       # CSV validé et colonnes normalisées
input_bytes = st.session_state.get("input_bytes", None)   # binaire pour appeler l'API

if input_df is None or input_bytes is None:
    st.warning("🛈 Revenez à la page d’accueil pour charger un CSV valide.")
    st.markdown('<div class="center">', unsafe_allow_html=True)
    if st.button("Page d'accueil"):
        # si valider, on bascule vers la page 2
        st.switch_page("streamlit_app.py")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

mode = "JSON"

# ----- APERÇU DATA -----
st.subheader("🔎 Aperçu des données (5 premières lignes)")
st.markdown('<div class="section">', unsafe_allow_html=True)
st.dataframe(input_df.head(), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ----- ACTION : LANCER PRÉDICTIONS -----
col_btn, _ = st.columns([1,3])
with col_btn:
    if st.button("▶️ Lancer les prédictions"):
        if not api_ok(api_url):
            st.error("🔴 L’API ne répond pas.")
        else:
            try:
                if mode == "JSON":
                    data = call_api_predict_json(api_url, input_bytes)
                    preds = pd.DataFrame(data["predictions"])  # index, proba_vrai, classe_predite (string)
                    result_df = input_df.copy()
                    result_df["proba_vrai"] = preds["proba_vrai"].astype(float)
                    result_df["classe_predite"] = preds["classe_predite"]
                else:
                    # CSV direct depuis l'API
                    result_df = call_api_predict_csv(api_url, input_bytes)
                    # s'aligne sur les colonnes si l'API renvoie colonnes dans un autre ordre
                    result_df = result_df[[*colonnes, "proba_vrai", "classe_predite"]]

                # arrondir proprement
                result_df["proba_vrai"] = result_df["proba_vrai"].round(4)

                st.session_state["result_df"] = result_df
                st.success("✅ Prédictions terminées")
            except Exception as e:
                st.exception(e)

# ----- AFFICHAGE RÉSULTATS -----
if "result_df" in st.session_state:
    result_df = st.session_state["result_df"].copy()
    result_df = result_df[[*colonnes, "proba_vrai", "classe_predite"]]

    # === KPI ===
    
    st.subheader("📌 Indicateurs clés")
    n = len(result_df)
    n_vrai = int((result_df["classe_predite"] == "vrai").sum())
    n_faux = n - n_vrai
    p_vrai = (n_vrai / n * 100) if n else 0
    p_faux = 100 - p_vrai if n else 0

    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.markdown(f'<div class="kpi" style="border-color: rgba(148,163,184,.35); background: rgba(148,163,184,.12);">🧾 Total<br><h2>{n}</h2></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi" style="border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.10);">✅ Vrais<br><h2>{n_vrai}</h2></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi" style="border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.10);">✅ % Vrais<br><h2>{p_vrai:.1f}%</h2></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi" style="border-color: rgba(239,68,68,.35); background: rgba(239,68,68,.10);">❌ Faux<br><h2>{n_faux}</h2></div>', unsafe_allow_html=True)
    with k5: st.markdown(f'<div class="kpi" style="border-color: rgba(239,68,68,.35); background: rgba(239,68,68,.10);">❌ % Faux<br><h2>{p_faux:.1f}%</h2></div>', unsafe_allow_html=True)

    # === TABLEAU COLORÉ vert / rouge ===
    st.subheader("📋 Tableau des prédictions")
    def _row_style(row):
        if row.get("classe_predite","").lower() == "vrai":
            return ["background-color: #1e9e51"] * len(row)  # vert pâle
        if row.get("classe_predite","").lower() == "faux":
            return ["background-color: #851717"] * len(row)  # rouge pâle
        return [""] * len(row)

    styled = (result_df.style
              .apply(_row_style, axis=1)
              .format({"proba_vrai": "{:.4f}"}))
    st.write(styled)

    # === TÉLÉCHARGEMENT CSV ===
    st.subheader("⬇️ Télécharger")
    csv_bytes = result_df.to_csv(sep=";", index=False).encode("utf-8-sig")
    st.download_button("Télécharger predictions.csv", data=csv_bytes,
                       file_name="predictions.csv", mime="text/csv")

    # === VISUELS ===
    st.subheader("📈 Visuels")
    c1, c2 = st.columns(2)

    with c1:
        st.caption("Répartition des classes")
        counts = result_df["classe_predite"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.bar(["vrai","faux"], [counts.get("vrai",0), counts.get("faux",0)],
                color=["#22c55e", "#ef4444"])
        ax1.set_xlabel("Classe"); ax1.set_ylabel("Nombre")
        st.pyplot(fig1)

    with c2:
        st.caption("Distribution des probabilités (proba_vrai)")
        fig2, ax2 = plt.subplots()
        ax2.hist(result_df["proba_vrai"], bins=20, color="#0ea5e9")
        ax2.axvline(0.5, linestyle="--")
        ax2.legend()
        ax2.set_xlabel("proba_vrai"); ax2.set_ylabel("Fréquence")
        st.pyplot(fig2)

    if st.button("Revenir à la page d'accueil"):
        # si valider, on bascule vers la page 2
        st.switch_page("streamlit_app.py")