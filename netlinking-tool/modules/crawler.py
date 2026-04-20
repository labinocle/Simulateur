"""
Lightweight URL crawler:
- Checks if a page is still alive (HTTP 200)
- Detects contact forms / email addresses
- Detects "write for us" / submission pages
- Detects broken outbound links (for broken link building)
"""
import re
import time
import urllib.parse
from typing import Optional
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BacklinkBot/1.0; "
        "+https://github.com/labinocle/simulateur)"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}
TIMEOUT = 10

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", re.IGNORECASE
)
WRITE_FOR_US_RE = re.compile(
    r"(write.for.us|guest.post|contribute|submit.article|article.invit"
    r"|devenir.auteur|redacteur.invit|soumettre.contenu)",
    re.IGNORECASE
)
CONTACT_KEYWORDS = re.compile(
    r"(contact|nous.écrire|nous.contacter|get.in.touch)", re.IGNORECASE
)


def _get(url: str, session: requests.Session) -> Optional[requests.Response]:
    try:
        resp = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return resp
    except Exception:
        return None


def analyze_url(url: str, session: requests.Session, check_broken: bool = False) -> dict:
    result = {
        "url": url,
        "status_code": None,
        "alive": False,
        "has_contact_form": False,
        "contact_email": None,
        "has_write_for_us": False,
        "contact_page_url": None,
        "broken_links_found": 0,
        "error": None,
    }

    resp = _get(url, session)
    if resp is None:
        result["error"] = "timeout_or_error"
        return result

    result["status_code"] = resp.status_code
    result["alive"] = resp.status_code == 200

    if not result["alive"]:
        return result

    try:
        soup = BeautifulSoup(resp.text, "lxml")
    except Exception:
        soup = BeautifulSoup(resp.text, "html.parser")

    # Detect contact form
    forms = soup.find_all("form")
    for form in forms:
        action = str(form.get("action", ""))
        text = form.get_text().lower()
        if any(k in text for k in ["contact", "message", "email", "send", "envoyer"]):
            result["has_contact_form"] = True
            break
        if CONTACT_KEYWORDS.search(action):
            result["has_contact_form"] = True
            break

    # Extract email addresses
    emails = EMAIL_RE.findall(resp.text)
    # Filter out common false positives
    filtered = [e for e in emails if not any(
        x in e.lower() for x in ["example", "domain.com", "sentry", "schema.org",
                                   "w3.org", "yoursite", ".png", ".jpg"]
    )]
    if filtered:
        result["contact_email"] = filtered[0]

    # Detect write-for-us / guest post opportunities
    page_text = soup.get_text()
    all_links = [a.get("href", "") for a in soup.find_all("a", href=True)]
    all_link_text = " ".join(a.get_text() for a in soup.find_all("a", href=True))
    full_text = page_text + " " + all_link_text

    if WRITE_FOR_US_RE.search(full_text):
        result["has_write_for_us"] = True
        # Try to find the actual write-for-us page URL
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            text = a.get_text().lower()
            if WRITE_FOR_US_RE.search(href + " " + text):
                result["contact_page_url"] = urllib.parse.urljoin(url, href)
                break

    # Find contact page link
    if not result["contact_page_url"]:
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").lower()
            text = a.get_text().lower()
            if CONTACT_KEYWORDS.search(href + " " + text):
                result["contact_page_url"] = urllib.parse.urljoin(url, a["href"])
                break

    # Broken link detection (optional, more expensive)
    if check_broken:
        broken = 0
        base_domain = urllib.parse.urlparse(url).netloc
        for a in soup.find_all("a", href=True)[:50]:  # limit to 50 links
            href = a["href"]
            if not href.startswith("http"):
                continue
            link_domain = urllib.parse.urlparse(href).netloc
            if link_domain == base_domain:
                continue
            link_resp = _get(href, session)
            if link_resp is not None and link_resp.status_code in (404, 410, 0):
                broken += 1
            time.sleep(0.2)
        result["broken_links_found"] = broken

    return result


def crawl_batch(
    urls: list[str],
    check_broken: bool = False,
    delay: float = 1.0,
    progress_callback=None
) -> list[dict]:
    """Crawl a list of URLs with rate limiting."""
    session = requests.Session()
    results = []
    for i, url in enumerate(urls):
        if progress_callback:
            progress_callback(i, len(urls), url)
        r = analyze_url(url, session, check_broken=check_broken)
        results.append(r)
        time.sleep(delay)
    session.close()
    return results
