"""
Netlinking Dashboard — Streamlit UI
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from modules.parser import load_backlinks
from modules.classifier import classify_dataframe, OPPORTUNITY_TYPES
from modules.scorer import score_opportunities, deduplicate_domains
from modules.reporter import generate_outreach_templates, TEMPLATES

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Netlinking Dashboard",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ────────────────────────────────────────────────────────────────────
PRIORITY_COLORS = {
    "A - Prioritaire": "#22c55e",
    "B - Bon":         "#f59e0b",
    "C - Moyen":       "#f97316",
    "D - Faible":      "#ef4444",
}
EFFORT_COLORS = {"low": "#22c55e", "medium": "#f59e0b", "high": "#ef4444"}
EFFORT_LABELS = {"low": "🟢 Facile", "medium": "🟡 Moyen", "high": "🔴 Difficile"}

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
.priority-A { color: #22c55e; font-weight: 700; }
.priority-B { color: #f59e0b; font-weight: 700; }
.priority-C { color: #f97316; }
.priority-D { color: #ef4444; }
.stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; }
div[data-testid="metric-container"] {
    background: #1e293b; border-radius: 12px; padding: 16px;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def process_files(file_bytes_list: list[tuple[str, bytes]], dedup: bool) -> pd.DataFrame:
    dfs = []
    for name, data in file_bytes_list:
        try:
            # Write to temp file so load_backlinks can detect extension
            import tempfile, pathlib
            suffix = pathlib.Path(name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            df = load_backlinks(tmp_path)
            df["_filename"] = name
            dfs.append(df)
            os.unlink(tmp_path)
        except Exception as e:
            st.warning(f"Impossible de lire **{name}**: {e}")
    if not dfs:
        return pd.DataFrame()
    combined = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["source_url"])
    classified = classify_dataframe(combined)
    scored = score_opportunities(classified)
    if dedup:
        scored = deduplicate_domains(scored)
    return scored


def demo_data() -> pd.DataFrame:
    import random
    random.seed(42)
    rows = [
        ("https://annuaire-pme.fr/listing/seo",            25, "votre niche",     True,  "Ahrefs"),
        ("https://blog-marketing.fr/ressources-seo",        62, "ressources SEO",  True,  "Ahrefs"),
        ("https://fr.wikipedia.org/wiki/Marketing_digital", 92, "",                True,  "Majestic"),
        ("https://forum.webmaster.fr/thread/outils-seo",    38, "outils SEO",      True,  "Ahrefs"),
        ("https://universite-lyon.edu/ressources/marketing", 78, "marketing",       True,  "SEMrush"),
        ("https://linkedin.com/company/votre-secteur",       84, "",                False, "Ahrefs"),
        ("https://presse-numerique.fr/article/tendances",    71, "tendances 2025",  True,  "Ahrefs"),
        ("https://blog-concurrent1.fr/write-for-us",         55, "Rédigez pour nous",True,"SEMrush"),
        ("https://blog-concurrent2.fr/guest-blogging",       48, "Article invité",  True,  "Ahrefs"),
        ("https://pages-jaunes.fr/pro/niche",                45, "votre niche",     True,  "Moz"),
        ("https://yelp.fr/biz/votre-entreprise",             72, "avis client",     True,  "Ahrefs"),
        ("https://tool-saas.com/testimonials",               61, "témoignage",      False, "SEMrush"),
        ("https://ressources-web.fr/liens-utiles",           44, "liens utiles",    True,  "Ahrefs"),
        ("https://expert-blog.fr/guide-complet-seo",         58, "guide SEO",       True,  "Ahrefs"),
        ("https://twitter.com/votre-secteur",                88, "",                False, "Ahrefs"),
        ("https://github.com/votre-compte",                  90, "",                True,  "Ahrefs"),
        ("https://medium.com/@expert-seo/article",           76, "",                True,  "Majestic"),
        ("https://reddit.com/r/franceseo/comments/xyz",      90, "",                False, "Ahrefs"),
        ("https://stackoverflow.com/questions/123456",       93, "",                False, "Ahrefs"),
        ("https://annuaire-startup.fr/fiche/votre-site",     31, "startup France",  True,  "Moz"),
        ("https://mention-sans-lien.fr/article",             53, "votre marque",    True,  "SEMrush"),
        ("https://site-partenaire.fr/outils-recommandes",    67, "outil recommandé",True,  "Ahrefs"),
        ("https://journaliste-tech.fr/interview",            74, "expert cité",     True,  "Ahrefs"),
        ("https://haro-source.fr/reponse",                   69, "",                True,  "SEMrush"),
        ("https://beta-directory.fr/annuaire/digital",       29, "annuaire",        True,  "Moz"),
    ]
    data = [{
        "Referring page URL": url,
        "URL To": "https://votre-site.fr/page-cible",
        "Anchor": anchor,
        "Domain Rating": dr + random.randint(-3, 3),
        "Referring Domain": url.split("/")[2],
        "First seen": "2024-01-15",
        "Link type": "text",
        "Dofollow": "Yes" if dof else "No",
        "_filename": f"demo_{tool}.csv",
    } for url, dr, anchor, dof, tool in rows]
    import tempfile
    df_raw = pd.DataFrame(data)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df_raw.to_csv(tmp.name, index=False)
    tmp.close()
    from modules.parser import load_backlinks
    df = load_backlinks(tmp.name)
    os.unlink(tmp.name)
    df["_filename"] = df_raw["_filename"].values[:len(df)]
    df = classify_dataframe(df)
    df = score_opportunities(df)
    return df


def export_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Opportunités")
        summary = (
            df.groupby("opportunity_label")
              .agg(count=("rank", "count"), score_moy=("score", "mean"))
              .round(1).reset_index().sort_values("score_moy", ascending=False)
        )
        summary.to_excel(writer, index=False, sheet_name="Résumé par type")
    return buf.getvalue()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/link.png", width=60)
    st.title("Netlinking Tool")
    st.markdown("---")

    st.subheader("📂 Import des backlinks")
    uploaded = st.file_uploader(
        "CSV / XLSX (Ahrefs, SEMrush, Majestic, Moz)",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        help="Exportez les backlinks de vos concurrents depuis votre outil SEO favori."
    )
    use_demo = st.checkbox("Utiliser les données de démo", value=not bool(uploaded))

    st.markdown("---")
    st.subheader("⚙️ Paramètres")
    your_site = st.text_input("URL de votre site", placeholder="https://votre-site.fr")
    dedup = st.toggle("1 URL max par domaine", value=True)
    min_score = st.slider("Score minimum", 0, 80, 0)

    st.markdown("---")
    st.subheader("🔍 Filtres")
    effort_filter = st.multiselect(
        "Effort", ["low", "medium", "high"],
        default=["low", "medium", "high"],
        format_func=lambda x: EFFORT_LABELS[x]
    )
    priority_filter = st.multiselect(
        "Priorité", ["A - Prioritaire", "B - Bon", "C - Moyen", "D - Faible"],
        default=["A - Prioritaire", "B - Bon", "C - Moyen", "D - Faible"]
    )


# ── Load data ──────────────────────────────────────────────────────────────────
if use_demo or not uploaded:
    with st.spinner("Chargement des données de démo..."):
        df_full = demo_data()
    st.info("Mode démo activé — importez vos propres fichiers dans la barre latérale.", icon="ℹ️")
else:
    file_bytes = [(f.name, f.read()) for f in uploaded]
    with st.spinner(f"Analyse de {len(file_bytes)} fichier(s)..."):
        df_full = process_files(file_bytes, dedup)
    if df_full.empty:
        st.error("Aucun backlink chargé. Vérifiez le format de vos fichiers.")
        st.stop()

# Apply filters
df = df_full.copy()
if min_score > 0:
    df = df[df["score"] >= min_score]
if effort_filter:
    df = df[df["effort"].isin(effort_filter)]
if priority_filter:
    df = df[df["priority"].isin(priority_filter)]
df = df.reset_index(drop=True)
df["rank"] = df.index + 1


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎯 Opportunités", "✉️ Templates", "📖 Méthodologie"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## Vue d'ensemble")

    # KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    total = len(df)
    prio_a = (df["priority"] == "A - Prioritaire").sum()
    easy   = (df["effort"] == "low").sum()
    avg_da = df["authority_score"].mean()
    dofollow_pct = df["dofollow"].fillna(False).astype(bool).mean() * 100

    col1.metric("Total opportunités", f"{total:,}")
    col2.metric("Priorité A 🥇", f"{prio_a}", delta=f"{prio_a/max(total,1)*100:.0f}%")
    col3.metric("Quick wins 🟢", f"{easy}")
    col4.metric("DA moyen", f"{avg_da:.0f}")
    col5.metric("Dofollow", f"{dofollow_pct:.0f}%")

    st.markdown("---")

    # Row 1: Priority donut + Effort bar
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Répartition par priorité")
        prio_counts = df["priority"].value_counts().reset_index()
        prio_counts.columns = ["priority", "count"]
        fig_donut = px.pie(
            prio_counts, names="priority", values="count",
            color="priority",
            color_discrete_map=PRIORITY_COLORS,
            hole=0.55,
        )
        fig_donut.update_traces(textposition="outside", textinfo="percent+label")
        fig_donut.update_layout(
            showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
            height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.markdown("#### Opportunités par type")
        type_summary = (
            df.groupby(["opportunity_label", "effort"])
              .agg(count=("rank", "count"), avg_score=("score", "mean"))
              .reset_index().sort_values("avg_score", ascending=True)
        )
        fig_bar = px.bar(
            type_summary, x="count", y="opportunity_label",
            color="effort",
            color_discrete_map=EFFORT_COLORS,
            orientation="h",
            text="count",
            labels={"count": "Nb opportunités", "opportunity_label": "", "effort": "Effort"},
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.05),
            xaxis_title="", yaxis_title="",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Row 2: Opportunity map (DA vs Effort) + Score distribution
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### Carte des opportunités (DA vs Facilité)")
        effort_num = {"low": 90, "medium": 50, "high": 15}
        map_df = df.copy()
        map_df["ease"] = map_df["effort"].map(effort_num)
        map_df["size"] = 8
        fig_scatter = px.scatter(
            map_df, x="ease", y="authority_score",
            color="priority",
            color_discrete_map=PRIORITY_COLORS,
            hover_name="referring_domain",
            hover_data={"opportunity_label": True, "score": True, "ease": False},
            labels={"ease": "Facilité d'acquisition →", "authority_score": "Domain Authority →"},
            size="size", size_max=10,
        )
        fig_scatter.add_shape(type="rect", x0=65, y0=50, x1=100, y1=100,
                               fillcolor="rgba(34,197,94,0.08)", line_width=0)
        fig_scatter.add_annotation(x=82, y=97, text="Zone idéale", showarrow=False,
                                    font=dict(color="#22c55e", size=11))
        fig_scatter.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 105], tickvals=[15, 50, 90],
                       ticktext=["Difficile", "Moyen", "Facile"]),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c4:
        st.markdown("#### Distribution des scores")
        fig_hist = px.histogram(
            df, x="score", nbins=20,
            color="priority",
            color_discrete_map=PRIORITY_COLORS,
            labels={"score": "Score (0-100)", "count": "Nb"},
            barmode="stack",
        )
        fig_hist.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.05),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Row 3: Sources breakdown (if multi-file)
    if "_filename" in df.columns and df["_filename"].nunique() > 1:
        st.markdown("#### Couverture par concurrent")
        src_df = df.groupby("_filename")["referring_domain"].count().reset_index()
        src_df.columns = ["Fichier source", "Opportunités"]
        fig_src = px.bar(src_df, x="Fichier source", y="Opportunités",
                         color="Opportunités", color_continuous_scale="Blues")
        fig_src.update_layout(height=200, margin=dict(t=10, b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_src, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — OPPORTUNITIES TABLE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## Liste des opportunités")

    # Top-bar: search + export
    search_col, export_col = st.columns([4, 1])
    with search_col:
        search = st.text_input("🔍 Rechercher (domaine, URL, type...)", "")
    with export_col:
        st.markdown("<br>", unsafe_allow_html=True)
        xlsx_bytes = export_excel_bytes(df)
        st.download_button(
            "⬇️ Exporter Excel",
            data=xlsx_bytes,
            file_name="rapport_netlinking.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # Type filter pills
    all_types = sorted(df["opportunity_label"].unique())
    selected_types = st.multiselect(
        "Types d'opportunité", all_types, default=all_types,
        label_visibility="collapsed"
    )

    display_df = df.copy()
    if search:
        mask = (
            display_df["referring_domain"].str.contains(search, case=False, na=False) |
            display_df["source_url"].str.contains(search, case=False, na=False) |
            display_df["opportunity_label"].str.contains(search, case=False, na=False) |
            display_df["anchor_text"].astype(str).str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]
    if selected_types:
        display_df = display_df[display_df["opportunity_label"].isin(selected_types)]

    st.markdown(f"**{len(display_df)} opportunités** affichées")

    # Color-coded table
    show_cols = ["rank", "score", "priority", "opportunity_label", "effort",
                 "referring_domain", "source_url", "anchor_text",
                 "authority_score", "dofollow", "action"]
    show_cols = [c for c in show_cols if c in display_df.columns]

    def color_priority(val):
        colors = {
            "A - Prioritaire": "background-color: #14532d; color: #bbf7d0",
            "B - Bon":         "background-color: #451a03; color: #fde68a",
            "C - Moyen":       "background-color: #431407; color: #fed7aa",
            "D - Faible":      "background-color: #450a0a; color: #fecaca",
        }
        return colors.get(str(val), "")

    def color_effort(val):
        m = {"low": "color: #86efac", "medium": "color: #fcd34d", "high": "color: #fca5a5"}
        return m.get(str(val), "")

    def color_score(val):
        try:
            v = float(val)
            if v >= 75:   return "background-color: #14532d; color: #bbf7d0; font-weight:700"
            if v >= 55:   return "background-color: #451a03; color: #fde68a"
            if v >= 30:   return "background-color: #431407; color: #fed7aa"
            return "background-color: #450a0a; color: #fecaca"
        except (ValueError, TypeError):
            return ""

    styled = (
        display_df[show_cols]
        .style
        .map(color_priority, subset=["priority"])
        .map(color_effort, subset=["effort"])
        .map(color_score, subset=["score"])
        .format({"score": "{:.0f}", "authority_score": "{:.0f}"}, na_rep="-")
    )
    st.dataframe(styled, width="stretch", height=520, hide_index=True)

    # Detail panel for selected domain
    st.markdown("---")
    st.markdown("#### Détail d'une opportunité")
    selected_domain = st.selectbox(
        "Sélectionner un domaine",
        options=display_df["referring_domain"].tolist(),
        index=0
    )
    row = display_df[display_df["referring_domain"] == selected_domain].iloc[0]
    d1, d2, d3 = st.columns(3)
    d1.metric("Score", f"{row['score']:.0f} / 100")
    d2.metric("Priorité", str(row.get("priority", "-")))
    d3.metric("DA", f"{row.get('authority_score', 0):.0f}")
    st.markdown(f"**URL** : [{row['source_url']}]({row['source_url']})")
    st.markdown(f"**Type** : {row.get('opportunity_label', '-')}  |  **Effort** : {EFFORT_LABELS.get(row.get('effort', ''), '-')}")
    st.info(f"**Action recommandée** : {row.get('action', '-')}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — OUTREACH TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## Templates d'outreach")

    site_name = your_site or "https://votre-site.fr"
    opp_types_present = df["opportunity_type"].unique()
    available_templates = {k: v for k, v in TEMPLATES.items() if k in opp_types_present}

    if not available_templates:
        st.warning("Aucun template disponible pour les types d'opportunités filtrés.")
    else:
        tc1, tc2 = st.columns([1, 2])
        with tc1:
            st.markdown("#### Types disponibles")
            for opp_type, template_text in available_templates.items():
                label = OPPORTUNITY_TYPES.get(opp_type)
                count = (df["opportunity_type"] == opp_type).sum()
                effort = OPPORTUNITY_TYPES.get(opp_type).effort if opp_type in OPPORTUNITY_TYPES else "medium"
                st.markdown(f"{EFFORT_LABELS[effort]} **{label.name}** — {count} sites")

        with tc2:
            selected_tpl = st.selectbox(
                "Choisir un template",
                options=list(available_templates.keys()),
                format_func=lambda k: OPPORTUNITY_TYPES[k].name if k in OPPORTUNITY_TYPES else k
            )
            tpl_text = available_templates[selected_tpl].replace("{your_site}", site_name)

            st.markdown("#### Template")
            edited_tpl = st.text_area("Personnalisez le template :", value=tpl_text, height=300)

            # Top targets for this type
            targets = df[df["opportunity_type"] == selected_tpl].head(5)
            if not targets.empty:
                st.markdown("#### Top cibles pour ce template")
                for _, r in targets.iterrows():
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    col_a.markdown(f"[{r['referring_domain']}]({r['source_url']})")
                    col_b.markdown(f"Score: **{r['score']:.0f}**")
                    col_c.markdown(f"DA: **{r['authority_score']:.0f}**")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## Méthodologie Ninja Linking")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("### 🟢 Effort faible")
        for opp_type, opp in OPPORTUNITY_TYPES.items():
            if opp.effort == "low":
                st.markdown(f"**{opp.name}**")
                st.caption(opp.strategy)
    with m2:
        st.markdown("### 🟡 Effort moyen")
        for opp_type, opp in OPPORTUNITY_TYPES.items():
            if opp.effort == "medium":
                st.markdown(f"**{opp.name}**")
                st.caption(opp.strategy)
    with m3:
        st.markdown("### 🔴 Effort élevé")
        for opp_type, opp in OPPORTUNITY_TYPES.items():
            if opp.effort == "high":
                st.markdown(f"**{opp.name}**")
                st.caption(opp.strategy)

    st.markdown("---")
    st.markdown("### Sprint mensuel recommandé")
    weeks = {
        "Semaine 1 — Setup & Quick wins": [
            "Importer les backlinks de 3 concurrents",
            "Traiter tous les Priorité A avec effort=low (profils, annuaires)",
            "Configurer Google Alerts pour les mentions de marque",
        ],
        "Semaine 2 — Batch outreach ressources": [
            "Filtrer opportunity_type = resource_page",
            "Personnaliser le template et envoyer 15-20 emails",
        ],
        "Semaine 3 — Broken links & Mentions": [
            "Utiliser le mode --crawl pour détecter les liens cassés",
            "Traiter les unlinked mentions détectées",
        ],
        "Semaine 4 — Guest posts & Presse": [
            "Choisir 2-3 blogs (effort=high, score>60)",
            "Rédiger propositions d'articles",
            "Répondre aux demandes HARO de la semaine",
        ],
    }
    for week, tasks in weeks.items():
        with st.expander(week, expanded=False):
            for t in tasks:
                st.checkbox(t, key=f"{week}_{t}")

    st.markdown("---")
    st.markdown("### Formule de scoring")
    st.latex(r"\text{Score} = DA \times 0.40 + \text{Facilité} \times 0.35 + \text{Dofollow} \times 0.10 + \text{Bonus type} \times 0.15")
    st.caption("DA normalisé 0-100 | Facilité: low=100, medium=60, high=20 | Dofollow: 0 ou 100")
