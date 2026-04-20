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
# Ordered from most specific to least specific
URL_PATTERNS: list[tuple[str, str]] = [
    # TLD-based (highest priority)
    (r"\.(edu|gov)(/|$)", "edu_gov"),

    # Known wikis
    (r"wikipedia\.org|wikia\.com|fandom\.com", "wiki"),

    # Social platforms & profiles
    (r"(linkedin\.com|twitter\.com|x\.com|facebook\.com|instagram\.com|youtube\.com"
     r"|pinterest\.com|tiktok\.com|behance\.net|dribbble\.com|github\.com"
     r"|medium\.com|substack\.com|about\.me|linktree\.com|xing\.com"
     r"|viadeo\.com|malt\.fr|wellfound\.com|glassdoor\.com|crunchbase\.com)", "social_profile"),

    # Press & major media (domain-level recognition)
    (r"(forbes\.com|hbr\.org|techcrunch\.com|inc\.com|entrepreneur\.com"
     r"|businessinsider\.|wired\.com|fastcompany\.com|harvard\.edu"
     r"|theguardian\.com|bbc\.(co\.uk|com)|telegraph\.co\.uk|independent\.co\.uk"
     r"|economist\.com|ft\.com|wsj\.com|nytimes\.com|bloomberg\.com"
     r"|lesechos\.fr|lefigaro\.fr|lemonde\.fr|lequipe\.fr|20minutes\.fr"
     r"|huffpost\.com|slate\.(fr|com)|nouvelobs\.com)", "press_media"),

    # Directories & listings
    (r"(annuaire|directory|repertoire|listing|pages-jaunes|yelp\.com"
     r"|foursquare|yellowpages|hotfrog|kompass|europages|trustpilot\.com"
     r"|capterra\.com|g2\.com|getapp\.com|producthunt\.com|alternativeto\.net"
     r"|clutch\.co|goodfirms\.co|sortlist\.(fr|com|be))", "directory"),

    # Forums & communities
    (r"(forum|community|discuss|phpbb|vbulletin|discourse|reddit\.com"
     r"|quora\.com|stackexchange|stackoverflow|slack\.com|discord\.com"
     r"|groups\.google|community\.|answers\.)", "forum_community"),

    # Testimonials & reviews
    (r"(temoignage|testimonial|avis|review|client|customer|case.stud"
     r"|success.stor|histoire.client|temoins)", "testimonial"),

    # Guest post / write-for-us (URL path signals)
    (r"(write-for-us|write_for_us|guest.post|guest.blog|contribute|submit.article"
     r"|become.author|soumettre|article.invit|redacteur|collaborer|write.with.us"
     r"|become.a.contributor)", "guest_post"),

    # Resource / tools pages (URL path)
    (r"(/ressource|/resource|liens.utiles|useful.links|/outils|/tools|/recommand"
     r"|/bookmark|/favoris|/liste-|/liste_|/top-\d|/best-\d|/best-tools"
     r"|/alternatives|/comparatif|/comparison)", "resource_page"),

    # Statistics & research pages → treat as resource_page (high value, citable)
    (r"(/statistic|/stats|/data|/research|/etude|/rapport|/survey|/benchmark"
     r"|/insight|/whitepaper|/infographic|-statistics|-stats|-data\b)", "resource_page"),

    # Blog articles → guest_post opportunity
    (r"(/blog/|/articles?/|/post/|/actualit|/news/[^$]|/learn/|/guide/|/how-to"
     r"|/tutorial|/glossar|/lexique|/fiche-|/dossier|/conseils)", "guest_post"),

    # Press releases & news section
    (r"(presse|press.release|communique|press-room|newsroom|media.center"
     r"|/news$|/presse$|/actualites$)", "press_media"),

    # Blog comments
    (r"(/comment|#comment|#respond|/avis$)", "comment_blog"),
]

ANCHOR_PATTERNS: list[tuple[str, str]] = [
    (r"(ressource|resource|lien.utile|useful|outil|tool|recommand)", "resource_page"),
    (r"(annuaire|directory|liste|listing)", "directory"),
    (r"(forum|discussion|communauté)", "forum_community"),
    (r"(article|blog|guide|tutoriel|tutorial|how.to|statistique|étude)", "guest_post"),
    (r"(temoignage|avis|review|client)", "testimonial"),
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
