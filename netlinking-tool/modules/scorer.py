"""
Score and prioritize backlink opportunities.

Final score (0-100) = weighted combination of:
  - authority_score  (DA/DR)
  - effort_score     (inverse of effort: low=100, medium=60, high=20)
  - dofollow_bonus   (+15 if dofollow)
  - type_bonus       (some types are structurally more valuable)
"""
import pandas as pd

EFFORT_SCORE = {"low": 100, "medium": 60, "high": 20}

TYPE_BONUS = {
    "edu_gov":        30,
    "wiki":           25,
    "resource_page":  20,
    "press_media":    20,
    "broken_link":    20,
    "unlinked_mention": 25,
    "testimonial":    15,
    "guest_post":     15,
    "directory":      10,
    "forum_community": 8,
    "social_profile":  5,
    "comment_blog":    3,
    "other":           0,
}

EFFORT_WEIGHT   = 0.35
AUTHORITY_WEIGHT = 0.40
DOFOLLOW_WEIGHT  = 0.10
TYPE_WEIGHT      = 0.15


def score_opportunities(df: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(df).copy()

    # Normalize authority to 0-100 (cap at 100)
    auth = pd.to_numeric(df["authority_score"], errors="coerce").fillna(0).clip(0, 100)

    effort_s  = df["effort"].map(EFFORT_SCORE).fillna(60)
    type_b    = df["opportunity_type"].map(TYPE_BONUS).fillna(0)
    dofollow  = df["dofollow"].fillna(False).astype(bool).astype(int) * 100

    df["score"] = (
        auth       * AUTHORITY_WEIGHT +
        effort_s   * EFFORT_WEIGHT    +
        dofollow   * DOFOLLOW_WEIGHT  +
        type_b     * TYPE_WEIGHT
    ).round(1)

    # Priority tier
    df["priority"] = pd.cut(
        df["score"],
        bins=[0, 30, 55, 75, 101],
        labels=["D - Faible", "C - Moyen", "B - Bon", "A - Prioritaire"],
        right=False
    )

    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


def deduplicate_domains(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the best-scoring URL per referring domain."""
    return (
        df.sort_values("score", ascending=False)
          .drop_duplicates(subset=["referring_domain"])
          .reset_index(drop=True)
    )
