"""
Classify each backlink opportunity by type and acquisition strategy.
Also detects if a URL is a potential "easy win" (low friction).
"""
import re
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd

@dataclass
class OpportunityType:
    name: str
    strategy: str
    effort: str          # low / medium / high
    typical_da: str      # low / medium / high
    action: str


OPPORTUNITY_TYPES: dict[str, OpportunityType] = {
    "directory": OpportunityType(
        "Annuaire / Répertoire",
        "Soumission directe du site",
        "low",
        "low",
        "Créer une fiche sur l'annuaire"
    ),
    "resource_page": OpportunityType(
        "Page de ressources",
        "Email outreach proposant votre lien",
        "medium",
        "medium",
        "Contacter le webmaster pour ajouter votre ressource"
    ),
    "guest_post": OpportunityType(
        "Guest post / Blog",
        "Proposer un article invité",
        "high",
        "high",
        "Envoyer une proposition d'article"
    ),
    "forum_community": OpportunityType(
        "Forum / Communauté",
        "Participation organique + signature/profil",
        "medium",
        "low",
        "Créer un profil et participer aux discussions"
    ),
    "wiki": OpportunityType(
        "Wiki / Wikipedia",
        "Éditer pour ajouter une citation",
        "medium",
        "high",
        "Proposer votre site comme référence"
    ),
    "edu_gov": OpportunityType(
        "Lien .edu / .gov",
        "Partenariat institutionnel / citation",
        "high",
        "high",
        "Contacter le département concerné"
    ),
    "press_media": OpportunityType(
        "Presse / Médias",
        "HARO, communiqué de presse, expert cité",
        "high",
        "high",
        "Répondre aux demandes journalistes ou envoyer un communiqué"
    ),
    "social_profile": OpportunityType(
        "Profil réseau social / plateforme",
        "Création de profil avec lien",
        "low",
        "medium",
        "Créer/compléter le profil avec votre URL"
    ),
    "testimonial": OpportunityType(
        "Témoignage / Review",
        "Écrire un avis sur un outil utilisé",
        "low",
        "medium",
        "Envoyer un témoignage au vendor"
    ),
    "broken_link": OpportunityType(
        "Lien cassé (Broken Link Building)",
        "Proposer votre contenu comme remplacement",
        "medium",
        "high",
        "Identifier le lien mort et contacter le webmaster"
    ),
    "comment_blog": OpportunityType(
        "Commentaire de blog",
        "Commenter avec valeur ajoutée",
        "low",
        "low",
        "Laisser un commentaire pertinent avec votre URL"
    ),
    "unlinked_mention": OpportunityType(
        "Mention sans lien",
        "Demander la conversion en lien",
        "low",
        "medium",
        "Contacter pour demander d'ajouter le lien"
    ),
    "other": OpportunityType(
        "Autre",
        "Analyse manuelle requise",
        "medium",
        "medium",
        "Analyser manuellement la page"
    ),
}

# Pattern rules: (regex_on_url, opportunity_type_key)
URL_PATTERNS: list[tuple[str, str]] = [
    (r"\.(edu|gov)(/|$)", "edu_gov"),
    (r"wikipedia\.org|wikia\.com|fandom\.com", "wiki"),
    (r"(linkedin\.com|twitter\.com|facebook\.com|instagram\.com|youtube\.com"
     r"|pinterest\.com|tiktok\.com|behance\.net|dribbble\.com|github\.com"
     r"|medium\.com|substack\.com|about\.me|linktree\.com)", "social_profile"),
    (r"(annuaire|directory|repertoire|listing|pages-jaunes|yelp\.com"
     r"|foursquare|yellowpages|hotfrog|kompass|europages)", "directory"),
    (r"(forum|community|discuss|phpbb|vbulletin|discourse|reddit\.com"
     r"|quora\.com|stackexchange|stackoverflow)", "forum_community"),
    (r"(write-for-us|guest.post|contribute|submit.article|become.author"
     r"|soumettre|article-invite|redacteur|collaborer)", "guest_post"),
    (r"(ressource|resource|liens.utiles|useful.links|outils|tools|recommand"
     r"|bookmark|favoris)", "resource_page"),
    (r"(temoignage|testimonial|avis|review|client|customer|case.stud)", "testimonial"),
    (r"(presse|press|media|actualite|news|journal|magazine|communique)", "press_media"),
    (r"(/comment|#comment|#respond|/avis)", "comment_blog"),
]

ANCHOR_PATTERNS: list[tuple[str, str]] = [
    (r"(ressource|resource|lien.utile|useful|outil|tool|recommand)", "resource_page"),
    (r"(annuaire|directory|liste|listing)", "directory"),
    (r"(forum|discussion|communauté)", "forum_community"),
    (r"(article|blog|guide|tutoriel|tutorial)", "guest_post"),
]


def classify_url(url: str, anchor: Optional[str] = None) -> str:
    if not isinstance(url, str):
        return "other"
    url_lower = url.lower()

    for pattern, opp_type in URL_PATTERNS:
        if re.search(pattern, url_lower):
            return opp_type

    if isinstance(anchor, str):
        anchor_lower = anchor.lower()
        for pattern, opp_type in ANCHOR_PATTERNS:
            if re.search(pattern, anchor_lower):
                return opp_type

    return "other"


def classify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add opportunity_type and strategy columns to backlink dataframe."""
    df = df.copy()

    df["opportunity_type"] = df.apply(
        lambda row: classify_url(
            str(row.get("source_url", "")),
            str(row.get("anchor_text", ""))
        ),
        axis=1
    )

    df["strategy"] = df["opportunity_type"].map(
        lambda t: OPPORTUNITY_TYPES.get(t, OPPORTUNITY_TYPES["other"]).strategy
    )
    df["effort"] = df["opportunity_type"].map(
        lambda t: OPPORTUNITY_TYPES.get(t, OPPORTUNITY_TYPES["other"]).effort
    )
    df["action"] = df["opportunity_type"].map(
        lambda t: OPPORTUNITY_TYPES.get(t, OPPORTUNITY_TYPES["other"]).action
    )
    df["opportunity_label"] = df["opportunity_type"].map(
        lambda t: OPPORTUNITY_TYPES.get(t, OPPORTUNITY_TYPES["other"]).name
    )

    return df
