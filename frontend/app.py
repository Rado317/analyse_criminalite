from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st


def resolve_api_url() -> str:
    env_value = os.getenv("API_URL")
    if env_value:
        return env_value.rstrip("/")
    try:
        return str(st.secrets.get("API_URL", "https://analyse-criminalite.onrender.com")).rstrip("/")
    except Exception:
        return "https://analyse-criminalite.onrender.com"


API_URL = resolve_api_url()

st.set_page_config(
    page_title="Analyse intelligente des infractions",
    page_icon="📊",
    layout="wide",
)
st.title("Plateforme intelligente d’analyse des infractions")
st.caption(
    "Analyse statistique • clustering • détection d’anomalies • estimation ML — 2024 à 2026-S1"
)


def api_get(path: str, params: dict | None = None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def format_int(value: int | float) -> str:
    return f"{int(value):,}".replace(",", " ")


try:
    years = api_get("/api/v1/years")
    categories = api_get("/api/v1/categories")
except Exception as exc:
    st.error(f"Backend indisponible : {exc}")
    st.code("uvicorn api.main:app --reload", language="bash")
    st.stop()

with st.sidebar:
    st.header("Filtres")
    selected_year = st.selectbox("Période", ["Toutes"] + years)
    selected_category = st.selectbox("Catégorie", ["Toutes"] + categories)
    st.divider()
    st.caption(f"API : {API_URL}")

filters: dict[str, str] = {}
if selected_year != "Toutes":
    filters["annee"] = selected_year
if selected_category != "Toutes":
    filters["categorie"] = selected_category

summary = api_get("/api/v1/summary", filters)
metric_columns = st.columns(6)
metric_columns[0].metric("Plaintes", format_int(summary["plaintes_directes"]))
metric_columns[1].metric("Saisines", format_int(summary["total_saisines"]))
metric_columns[2].metric("Victimes", format_int(summary["victimes"]))
metric_columns[3].metric("Interpellés", format_int(summary["interpelles"]))
metric_columns[4].metric("Résultats DEF", format_int(summary["resultats_def"]))
metric_columns[5].metric("Anomalies", format_int(summary["anomalies"]))

(
    dashboard_tab,
    clusters_tab,
    anomalies_tab,
    quality_tab,
    ml_tab,
    about_tab,
) = st.tabs(
    [
        "Tableau de bord",
        "Clustering",
        "Anomalies",
        "Qualité des données",
        "Estimation ML",
        "À propos",
    ]
)

with dashboard_tab:
    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Infractions les plus représentées")
        top_params = {"metric": "plaintes_directes", "limit": 15}
        if selected_year != "Toutes":
            top_params["annee"] = selected_year
        top_df = pd.DataFrame(api_get("/api/v1/statistics/top-infractions", top_params))
        if not top_df.empty:
            st.bar_chart(top_df.set_index("infraction"))
    with right:
        st.subheader("Comparaison des périodes")
        annual_df = pd.DataFrame(api_get("/api/v1/statistics/by-year"))
        if not annual_df.empty:
            st.line_chart(
                annual_df.set_index("annee")[["plaintes_directes", "victimes", "interpelles"]]
            )
            st.caption("2026-S1 représente uniquement le premier semestre.")

    st.subheader("Données filtrées")
    records_df = pd.DataFrame(api_get("/api/v1/infractions", {**filters, "limit": 1000}))
    st.dataframe(records_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Télécharger les données filtrées",
        records_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="infractions_filtrees.csv",
        mime="text/csv",
    )

with clusters_tab:
    st.subheader("Groupes de profils statistiques")
    cluster_metrics = api_get("/api/v1/clustering-metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Nombre de clusters", cluster_metrics["meilleur_k"])
    c2.metric("Score silhouette", round(cluster_metrics["score_silhouette"], 3))
    c3.metric(
        "Variance PCA expliquée",
        f"{100 * sum(cluster_metrics['variance_pca_expliquee']):.1f} %",
    )
    st.info(cluster_metrics["interpretation"])

    cluster_data = pd.DataFrame(api_get("/api/v1/infractions", {"limit": 1000}))
    cluster_data = cluster_data.dropna(subset=["pca_1", "pca_2", "cluster"])
    if not cluster_data.empty:
        cluster_data["cluster"] = cluster_data["cluster"].astype(str)
        st.scatter_chart(
            cluster_data,
            x="pca_1",
            y="pca_2",
            color="cluster",
            size="plaintes_directes",
        )
    st.subheader("Profil moyen par cluster")
    st.dataframe(pd.DataFrame(api_get("/api/v1/clusters")), use_container_width=True, hide_index=True)

with anomalies_tab:
    st.subheader("Observations inhabituelles à vérifier")
    anomaly_metrics = api_get("/api/v1/anomaly-metrics")
    a1, a2, a3 = st.columns(3)
    a1.metric("Anomalies ML", anomaly_metrics["nombre_anomalies_ml"])
    a2.metric("Anomalies par règles", anomaly_metrics["nombre_anomalies_regles"])
    a3.metric("Anomalies finales", anomaly_metrics["nombre_anomalies_finales"])
    st.warning(anomaly_metrics["avertissement"])

    selected_level = st.selectbox("Niveau", ["Tous", "Élevée", "Moyenne", "Faible"])
    anomaly_params = {"limit": 500}
    if selected_level != "Tous":
        anomaly_params["niveau"] = selected_level
    anomalies_df = pd.DataFrame(api_get("/api/v1/anomalies", anomaly_params))
    st.dataframe(anomalies_df, use_container_width=True, hide_index=True)

with quality_tab:
    st.subheader("Rapport automatique de qualité")
    quality = api_get("/api/v1/data-quality")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Lignes", quality["nombre_lignes"])
    q2.metric("Catégories", quality["nombre_categories"])
    q3.metric("Infractions normalisées", quality["nombre_infractions_normalisees"])
    q4.metric("Écarts avec totaux", quality["ecarts_avec_totaux_officiels"])
    st.json(quality)

    st.subheader("Réconciliation détail / totaux officiels")
    reconciliation_df = pd.DataFrame(api_get("/api/v1/reconciliation"))
    only_differences = st.checkbox("Afficher uniquement les écarts", value=True)
    if only_differences and not reconciliation_df.empty:
        reconciliation_df = reconciliation_df.loc[~reconciliation_df["Concordance"]]
    st.dataframe(reconciliation_df, use_container_width=True, hide_index=True)

def flatten_model_results(resultats: list[dict]) -> pd.DataFrame:
    """Éclate les blocs validation_kfold / validation_par_periode en colonnes
    lisibles au lieu de laisser des dictionnaires JSON bruts dans les cellules."""
    rows = []
    for item in resultats:
        row = {"modele": item["modele"]}
        for prefix, key in [("kfold", "validation_kfold"), ("periode", "validation_par_periode")]:
            for metric_name, value in item.get(key, {}).items():
                row[f"{prefix}_{metric_name}"] = value
        for extra in ("mae_entrainement", "rmse_entrainement", "r2_entrainement"):
            if extra in item:
                row[extra] = item[extra]
        rows.append(row)
    return pd.DataFrame(rows)


with ml_tab:
    st.subheader("Comparaison des modèles de régression")
    model_metrics = api_get("/api/v1/model-metrics")
    metrics_df = flatten_model_results(model_metrics["resultats"])
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    st.success(f"Meilleur modèle selon la RMSE CV : {model_metrics['meilleur_modele']}")
    st.caption(
        "Le modèle est sélectionné sur la RMSE en validation croisée k-fold (colonnes kfold_*). "
        "Les colonnes periode_* montrent la robustesse entre périodes temporelles : "
        "un écart important entre les deux indique une sensibilité au découpage temporel."
    )
    st.warning(model_metrics["avertissement"])

    importance_df = pd.DataFrame(model_metrics["importance_variables_exploratoire"])
    if not importance_df.empty:
        st.subheader("Importance exploratoire des variables")
        st.bar_chart(importance_df.set_index("variable"))

    st.subheader("Tester une estimation de Resultats_DEF")
    with st.form("prediction_form"):
        p1, p2 = st.columns(2)
        year = p1.selectbox("Période", years, index=len(years) - 1)
        category = p2.selectbox("Catégorie", categories)
        c1, c2, c3 = st.columns(3)
        complaints = c1.number_input("Plaintes directes", min_value=0, value=100)
        fd = c2.number_input("FD", min_value=0, value=0)
        st_count = c3.number_input("ST", min_value=0, value=0)
        c4, c5, c6 = st.columns(3)
        victims_h = c4.number_input("Victimes hommes", min_value=0, value=40)
        victims_f = c5.number_input("Victimes femmes", min_value=0, value=20)
        arrested = c6.number_input("Interpellés", min_value=0, value=30)
        submitted = st.form_submit_button("Estimer")

    if submitted:
        payload = {
            "annee": year,
            "categorie": category,
            "saisine_plaintes_directes": complaints,
            "saisine_fd": fd,
            "saisine_st": st_count,
            "saisine_autres": 0,
            "victimes_h": victims_h,
            "victimes_f": victims_f,
            "victimes_g": 0,
            "victimes_f_fille": 0,
            "neutralises": 0,
            "interpelles": arrested,
        }
        response = requests.post(
            f"{API_URL}/api/v1/predict/results-def", json=payload, timeout=20
        )
        if response.ok:
            result = response.json()
            st.metric("Résultats DEF estimés", result["resultats_def_estimes"])
            st.caption(f"Modèle : {result['modele']}")
            st.caption(result["avertissement"])
        else:
            st.error(response.text)

with about_tab:
    st.markdown(
        """
        ### Objet du projet
        La plateforme centralise les données d'infractions, vérifie leur qualité,
        produit des statistiques, regroupe les profils similaires et détecte des
        observations inhabituelles.

        ### Ce que la plateforme ne fait pas
        Elle ne cartographie pas les infractions, car les fichiers ne contiennent
        ni adresse, ni quartier, ni latitude/longitude. Elle ne prédit pas non plus
        la dangerosité d'une personne.

        ### Limite principale
        Les données couvrent deux années complètes et un semestre. Les résultats
        Machine Learning constituent donc une preuve de concept académique.
        """
    )
