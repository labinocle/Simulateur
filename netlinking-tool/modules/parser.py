"""
Parse backlink CSV exports from Ahrefs, SEMrush, Majestic, Moz.
Normalizes columns to a standard schema:
  source_url, target_url, anchor_text, domain_rating, domain_authority,
  referring_domain, first_seen, link_type, dofollow
"""
import pandas as pd
import re
from pathlib import Path

STANDARD_COLS = [
    "source_url", "target_url", "anchor_text",
    "domain_rating", "domain_authority", "referring_domain",
    "first_seen", "link_type", "dofollow"
]

# Column name mappings per tool
AHREFS_MAP = {
    "Referring page URL": "source_url",
    "URL To": "target_url",
    "Anchor": "anchor_text",
    "Domain Rating": "domain_rating",
    "Referring Domain": "referring_domain",
    "First seen": "first_seen",
    "Link type": "link_type",
    "Dofollow": "dofollow",
}

SEMRUSH_MAP = {
    # Current SEMrush export format (2024-2025)
    "Source url":    "source_url",
    "Target url":    "target_url",
    "Anchor":        "anchor_text",
    "Page ascore":   "domain_rating",
    "Source title":  "source_title",
    "First seen":    "first_seen",
    "Nofollow":      "_nofollow",   # inverted → dofollow in post-processing
    # Legacy / alternate column names
    "Source URL":    "source_url",
    "Target URL":    "target_url",
    "Anchor Text":   "anchor_text",
    "Authority Score": "domain_rating",
    "Domain ascore": "domain_authority",
    "Active":        "dofollow",
    "Source Title":  "source_title",
}

MAJESTIC_MAP = {
    "SourceURL": "source_url",
    "DestinationURL": "target_url",
    "AnchorText": "anchor_text",
    "TrustFlow": "domain_rating",
    "CitationFlow": "domain_authority",
    "RefDomain": "referring_domain",
    "LastSeen": "first_seen",
}

MOZ_MAP = {
    "Linking Page URL": "source_url",
    "Target URL": "target_url",
    "Anchor Text": "anchor_text",
    "Domain Authority": "domain_authority",
    "Page Authority": "page_authority",
    "Spam Score": "spam_score",
    "Follow": "dofollow",
}


def _detect_tool(df: pd.DataFrame) -> str:
    cols = set(df.columns)
    if "Domain Rating" in cols or "Referring page URL" in cols:
        return "ahrefs"
    if "Page ascore" in cols or "Source url" in cols or "Authority Score" in cols or "Source URL" in cols:
        return "semrush"
    if "TrustFlow" in cols or "SourceURL" in cols:
        return "majestic"
    if "Domain Authority" in cols or "Linking Page URL" in cols:
        return "moz"
    return "generic"


def _extract_domain(url: str) -> str:
    if not isinstance(url, str):
        return ""
    match = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return match.group(1) if match else url


def load_backlinks(filepath: str) -> pd.DataFrame:
    """Load and normalize a backlink export file."""
    path = Path(filepath)
    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(filepath)
    else:
        # Try different encodings/separators
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                df = pd.read_csv(filepath, encoding=enc, sep=None, engine="python")
                break
            except Exception:
                continue
        else:
            raise ValueError(f"Cannot parse file: {filepath}")

    tool = _detect_tool(df)
    mapping = {
        "ahrefs": AHREFS_MAP,
        "semrush": SEMRUSH_MAP,
        "majestic": MAJESTIC_MAP,
        "moz": MOZ_MAP,
        "generic": {},
    }[tool]

    df = df.rename(columns=mapping).copy()

    # SEMrush uses "Nofollow" (True = nofollow), convert to dofollow
    if "_nofollow" in df.columns:
        df["dofollow"] = ~df["_nofollow"].fillna(False).astype(bool)
        df = df.drop(columns=["_nofollow"])

    # Ensure all standard columns exist
    for col in STANDARD_COLS:
        if col not in df.columns:
            df[col] = None

    # Derive referring_domain from source_url if missing
    if df["referring_domain"].isna().all():
        df["referring_domain"] = df["source_url"].apply(_extract_domain)

    # Normalize dofollow to bool (for tools using text values)
    if "dofollow" in df.columns and df["dofollow"].dtype == object:
        df["dofollow"] = df["dofollow"].astype(str).str.lower().isin(
            ["true", "yes", "1", "dofollow", "follow"]
        )

    # Use best available authority score
    auth = df["domain_rating"].fillna(df.get("domain_authority", pd.Series(dtype=float))).fillna(0)
    df["authority_score"] = pd.to_numeric(auth, errors="coerce").fillna(0)

    df["_source_tool"] = tool
    return df[STANDARD_COLS + ["authority_score", "_source_tool"]].drop_duplicates(
        subset=["source_url"]
    )
