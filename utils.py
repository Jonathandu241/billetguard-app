# utils.py
import pandas as pd
import requests

colonnes = ['length','height_left','height_right','margin_up','margin_low','diagonal']

def normalize_columns(cols):
    return [str(c).strip().lower().replace(" ", "_") for c in cols]

def validate_df_strict(df: pd.DataFrame):
    """Vérifie colonnes exactes + types numériques. Lève ValueError si problème."""
    df = df.copy()
    df.columns = normalize_columns(df.columns)

    missing = [c for c in colonnes if c not in df.columns]
    extra   = [c for c in df.columns if c not in colonnes]
    if missing or extra or len(df.columns) != len(colonnes):
        raise ValueError(
            f"Colonnes invalides.\n"
            f"Attendu: {colonnes}\n"
            f"Manquantes: {missing}\n"
            f"En trop: {extra}\n"
            f"Reçues: {df.columns.tolist()}"
        )
    X_try = df[colonnes].apply(pd.to_numeric, errors="coerce")
    bad = X_try.isna().sum()
    bad_cols = bad[bad > 0].index.tolist()
    if bad_cols:
        raise ValueError(f"Colonnes non numériques / valeurs invalides: {bad_cols}")
    return df  # normalisé

def api_ok(url: str) -> bool:
    try:
        r = requests.get(f"{url}/health", timeout=5)
        return r.ok
    except Exception:
        return False

def call_api_predict_json(api_url: str, file_bytes: bytes):
    files = {"file": ("billets_production.csv", file_bytes, "text/csv")}
    r = requests.post(f"{api_url}/predict-file", files=files, timeout=60)
    r.raise_for_status()
    return r.json()

def call_api_predict_csv(api_url: str, file_bytes: bytes) -> pd.DataFrame:
    files = {"file": ("billets_production.csv", file_bytes, "text/csv")}
    r = requests.post(f"{api_url}/predict-file-csv", files=files, timeout=60)
    r.raise_for_status()
    import io
    return pd.read_csv(io.BytesIO(r.content), sep=";")

def style_predictions(df: pd.DataFrame):
    """Renvoie un Styler avec lignes vert/rouge selon 'classe_predite'."""
    def _row_style(row):
        if "classe_predite" in row and str(row["classe_predite"]).lower() in ["vrai","true","1"]:
            return ["background-color: #e8f7ee"] * len(row)  # vert pâle
        if "classe_predite" in row and str(row["classe_predite"]).lower() in ["faux","false","0"]:
            return ["background-color: #fdecec"] * len(row)  # rouge pâle
        return [""] * len(row)
    styler = (df.style
              .apply(_row_style, axis=1)
              .format({"proba_vrai": "{:.4f}"}))
    return styler
