# streamlit_app.py — Page d’accueil
import streamlit as st
import pandas as pd
import io
from utils import colonnes, validate_df_strict, api_ok

st.set_page_config(page_title="Détection de faux billets", page_icon="💶", layout="wide")

# --- Styles personnalisés ---
st.markdown("""
<style>
.stApp {
  background: linear-gradient(120deg, #0ea5e9 0%, #22c55e 100%) fixed;
  color: #111827;
  font-family: "Segoe UI", sans-serif;
}
.card {
  background: rgba(255,255,255,0.92);
  border-radius: 18px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}
h1.title {
  text-align: center;
  font-weight: 800;
  color: #0b1221;
}
p.desc {
  font-size: 1.1rem;
  line-height: 1.6;
}
.center-btn {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- Carte principale ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h1 class="title">💶 Bienvenue sur <span style="color:#0ea5e9">BilletGuard</span></h1>', unsafe_allow_html=True)

st.markdown(
    '<p class="desc">BilletGuard est une application intelligente qui vous aide à '
    'détecter automatiquement les <b>faux billets</b> en analysant leurs dimensions. '
    'Grâce à un modèle de <i>Machine Learning</i>, vous pouvez télécharger un fichier CSV '
    'et obtenir instantanément un diagnostic billet par billet.</p>',
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

# --- Instructions CSV ---
st.subheader("📋 Caractéristiques attendues du fichier CSV")
st.write("Pour que l’analyse fonctionne correctement, votre fichier doit respecter ces critères :")
st.markdown(f"""
- Format **CSV** avec le séparateur **;** (point-virgule).
- **Pas** de colonne d’étiquette (uniquement les mesures).
- Doit contenir **exactement 6 colonnes** :
    1. `{colonnes[0]}`
    2. `{colonnes[1]}`
    3. `{colonnes[2]}`
    4. `{colonnes[3]}`
    5. `{colonnes[4]}`
    6. `{colonnes[5]}`
- Toutes les colonnes doivent être **numériques** (décimales possibles).
""")

st.info("💡 Exemple : un fichier de 100 billets mesurés, chacun avec ses 6 caractéristiques.")

# ---------- UPLOAD + VALIDATION ICI (SUR LA PAGE D’ACCUEIL) ----------
st.subheader("📤 Déposez votre fichier CSV")
uploaded = st.file_uploader("Choisir un fichier…", type=["csv"])

valid = False
if uploaded is not None:
    try:
        df_raw = pd.read_csv(io.BytesIO(uploaded.getvalue()), sep=";")
        df_valid = validate_df_strict(df_raw)  # lève ValueError si problème
    except Exception as e:
        st.error(f"❌ Fichier invalide : {e}")
    else:
        valid = True
        st.success("✅ Fichier valide !")
        # Aperçu seulement si valide
        #st.write("🔎 Aperçu (5 premières lignes) ", unsafe_allow_html=True)
        #st.dataframe(df_valid.head(), use_container_width=True)
        # Stocker pour la page suivante
        st.session_state["input_df"] = df_valid
        st.session_state["input_bytes"] = uploaded.getvalue()

# ---------- BOUTON COMMENCER (ACTIF UNIQUEMENT SI VALIDE) ----------
st.markdown('<div class="center">', unsafe_allow_html=True)
if st.button("🚀 Commencer l’analyse", disabled=not valid):
    # si valider, on bascule vers la page 2
    st.switch_page("pages/1_Analyse_et_Predictions.py")
st.markdown('</div>', unsafe_allow_html=True)

if not valid:
    st.caption("Le bouton s’activera une fois que votre CSV aura été validé ✅.")