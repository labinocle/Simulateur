#!/usr/bin/env python3
"""
Netlinking Automation Tool
--------------------------
Analyse les backlinks de vos concurrents et identifie vos meilleures
opportunités de netlinking gratuites, classées par priorité.

Usage:
  python backlink_tool.py analyze --input fichier.csv --output rapport.xlsx
  python backlink_tool.py analyze --input "*.csv" --crawl --output rapport.xlsx
  python backlink_tool.py demo
"""
import sys
import os
import glob
import time
from pathlib import Path
import click
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(__file__))
from modules.parser import load_backlinks
from modules.classifier import classify_dataframe
from modules.scorer import score_opportunities, deduplicate_domains
from modules.reporter import export_excel, export_csv, generate_outreach_templates, print_summary
from modules.crawler import crawl_batch


@click.group()
def cli():
    """Netlinking Automation Tool — Trouvez vos meilleures opportunités de backlinks."""
    pass


@cli.command()
@click.option("--input", "-i", "input_files", multiple=True, required=True,
              help="Fichier(s) CSV/XLSX d'exports backlinks (Ahrefs, SEMrush, Majestic, Moz)")
@click.option("--output", "-o", "output_path", default="rapport_netlinking.xlsx",
              help="Fichier de sortie (.xlsx ou .csv)")
@click.option("--crawl/--no-crawl", default=False,
              help="Crawler les pages pour détecter contacts et liens cassés (lent)")
@click.option("--crawl-broken/--no-crawl-broken", default=False,
              help="Activer la détection de liens cassés sur chaque page (très lent)")
@click.option("--dedup/--no-dedup", default=True,
              help="Dédupliquer par domaine (garder le meilleur par domaine)")
@click.option("--min-score", default=0, type=float,
              help="Score minimum pour inclure une opportunité (0-100)")
@click.option("--top", default=0, type=int,
              help="Limiter aux N meilleures opportunités (0 = toutes)")
@click.option("--your-site", default="",
              help="URL de votre site (pour les templates d'outreach)")
@click.option("--templates/--no-templates", default=True,
              help="Générer les templates d'email d'outreach")
@click.option("--delay", default=1.5, type=float,
              help="Délai entre requêtes crawler (secondes)")
def analyze(input_files, output_path, crawl, crawl_broken, dedup,
            min_score, top, your_site, templates, delay):
    """Analyser des exports backlinks et générer un rapport priorisé."""

    # --- 1. Load files ---
    click.echo(f"\n📂 Chargement des fichiers...")
    all_dfs = []
    files_to_load = []
    for pattern in input_files:
        matches = glob.glob(pattern)
        files_to_load.extend(matches if matches else [pattern])

    if not files_to_load:
        click.echo("❌ Aucun fichier trouvé.", err=True)
        sys.exit(1)

    for f in files_to_load:
        try:
            df = load_backlinks(f)
            click.echo(f"  ✓ {f} — {len(df)} backlinks ({df['_source_tool'].iloc[0]})")
            all_dfs.append(df)
        except Exception as e:
            click.echo(f"  ✗ {f} — Erreur: {e}", err=True)

    if not all_dfs:
        click.echo("❌ Aucun fichier chargé avec succès.", err=True)
        sys.exit(1)

    df = pd.concat(all_dfs, ignore_index=True).drop_duplicates(subset=["source_url"])
    click.echo(f"\n  Total: {len(df)} URLs uniques\n")

    # --- 2. Classify ---
    click.echo("🔍 Classification des opportunités...")
    df = classify_dataframe(df)

    # --- 3. Score ---
    click.echo("📊 Scoring et priorisation...")
    df = score_opportunities(df)

    if dedup:
        before = len(df)
        df = deduplicate_domains(df)
        click.echo(f"  Déduplication: {before} → {len(df)} (1 URL par domaine)")

    if min_score > 0:
        df = df[df["score"] >= min_score]
        click.echo(f"  Filtre score ≥ {min_score}: {len(df)} opportunités restantes")

    if top > 0:
        df = df.head(top)

    # --- 4. Crawl (optional) ---
    if crawl:
        click.echo(f"\n🕷️  Crawl des pages ({len(df)} URLs, délai={delay}s)...")
        urls = df["source_url"].tolist()

        crawl_results = []
        with tqdm(total=len(urls), unit="url") as pbar:
            def progress(i, total, url):
                pbar.set_postfix_str(url[:60])
                pbar.update(1 if i > 0 else 0)

            crawl_results = crawl_batch(
                urls, check_broken=crawl_broken, delay=delay,
                progress_callback=progress
            )

        crawl_df = pd.DataFrame(crawl_results)
        df = df.merge(
            crawl_df[["url", "alive", "has_contact_form", "contact_email",
                       "has_write_for_us", "contact_page_url", "broken_links_found"]],
            left_on="source_url", right_on="url", how="left"
        ).drop(columns=["url"])

        # Bonus de score pour les pages avec contact détecté
        df.loc[df["has_contact_form"] == True, "score"] += 5
        df.loc[df["contact_email"].notna(), "score"] += 5
        df.loc[df["has_write_for_us"] == True, "score"] += 10
        df = df.sort_values("score", ascending=False).reset_index(drop=True)
        df["rank"] = df.index + 1

        dead_count = (df["alive"] == False).sum()
        contact_count = df["has_contact_form"].sum()
        wfu_count = df["has_write_for_us"].sum()
        click.echo(f"  Pages mortes: {dead_count} | Formulaires contact: {contact_count} | Write-for-us: {wfu_count}")

    # --- 5. Export ---
    click.echo(f"\n💾 Export: {output_path}")
    if output_path.endswith(".csv"):
        out = export_csv(df, output_path)
    else:
        out = export_excel(df, output_path, your_site=your_site)
    click.echo(f"  ✓ Rapport sauvegardé: {out}")

    # --- 6. Templates ---
    if templates:
        templates_dir = Path(output_path).stem + "_templates"
        generated = generate_outreach_templates(df, templates_dir, your_site=your_site or "VOTRE_SITE")
        if generated:
            click.echo(f"  ✓ Templates outreach: {templates_dir}/ ({len(generated)} fichiers)")

    # --- 7. Summary ---
    print_summary(df)


@cli.command()
def demo():
    """Générer un jeu de données de démonstration et lancer une analyse."""
    click.echo("🚀 Génération des données de démonstration...")
    demo_data = _generate_demo_data()
    demo_path = "/tmp/demo_backlinks.csv"
    demo_data.to_csv(demo_path, index=False)
    click.echo(f"  Fichier demo: {demo_path} ({len(demo_data)} backlinks)")
    click.echo("\n" + "-"*50)

    from click.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(analyze, [
        "--input", demo_path,
        "--output", "/tmp/demo_rapport.xlsx",
        "--your-site", "https://votre-site.fr",
        "--no-crawl",
    ])
    click.echo(result.output)
    if result.exit_code != 0 and result.exception:
        import traceback
        traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)


def _generate_demo_data() -> pd.DataFrame:
    """Generate realistic demo data similar to an Ahrefs CSV export."""
    import random
    random.seed(42)

    sample_domains = [
        ("https://annuaire-pme.fr/listing/votre-niche", 25, "Votre niche", True),
        ("https://blog-marketing.fr/ressources-seo", 62, "ressources SEO", True),
        ("https://fr.wikipedia.org/wiki/Marketing_digital", 92, "", True),
        ("https://forum.webmaster.fr/thread/outils-seo", 38, "outils SEO", True),
        ("https://universite-lyon.edu/ressources/marketing", 78, "marketing", True),
        ("https://linkedin.com/company/votre-secteur", 84, "", False),
        ("https://presse-numerique.fr/article/tendances-2025", 71, "tendances 2025", True),
        ("https://blog-concurrent1.fr/write-for-us", 55, "Rédigez pour nous", True),
        ("https://blog-concurrent2.fr/guest-blogging", 48, "Article invité", True),
        ("https://pages-jaunes.fr/pro/votre-niche", 45, "votre niche", True),
        ("https://yelp.fr/biz/votre-entreprise", 72, "avis client", True),
        ("https://tool-saas.com/testimonials", 61, "témoignage client", False),
        ("https://ressources-web.fr/liens-utiles", 44, "liens utiles", True),
        ("https://expert-blog.fr/guide-complet-seo", 58, "guide SEO", True),
        ("https://twitter.com/votre-secteur", 88, "", False),
        ("https://github.com/votre-compte", 90, "", True),
        ("https://medium.com/@expert-seo/article", 76, "", True),
        ("https://reddit.com/r/franceseo/comments/xyz", 90, "", False),
        ("https://stackoverflow.com/questions/123456", 93, "", False),
        ("https://annuaire-startup.fr/fiche/votre-site", 31, "startup France", True),
        ("https://blog-disparu.fr/ressources", 42, "liens rompus ici", True),
        ("https://mention-sans-lien.fr/article-sur-votre-secteur", 53, "votre marque", True),
        ("https://site-partenaire.fr/outils-recommandes", 67, "outil recommandé", True),
        ("https://journaliste-tech.fr/interview", 74, "expert cité", True),
        ("https://haro-source.fr/reponse", 69, "", True),
    ]

    rows = []
    for url, dr, anchor, dofollow in sample_domains:
        rows.append({
            "Referring page URL": url,
            "URL To": "https://votre-site.fr/page-cible",
            "Anchor": anchor,
            "Domain Rating": dr + random.randint(-5, 5),
            "Referring Domain": url.split("/")[2],
            "First seen": "2024-01-15",
            "Link type": "text",
            "Dofollow": "Yes" if dofollow else "No",
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    cli()
