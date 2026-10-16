import os
import re
import urllib3
import requests
from bs4 import BeautifulSoup

# Disable HTTPS verification warnings for mirror sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

SCIHUB_MIRRORS = [
    "https://sci-hub.reatk.com",
    "https://sci-hub.se",
    "https://sci-hub.box",
    "https://www.sci-hub.in",
    "https://sci-hub.al",
    "https://sci-hub.st",
    "https://sci-hub.ru"
]


def clean_doi_string(doi: str) -> str:
    """Clean DOI by removing prefixes like https://doi.org/."""
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi


def get_metadata_from_crossref(doi: str) -> dict:
    """Fetch accurate paper metadata from CrossRef API."""
    clean_doi = clean_doi_string(doi)
    url = f"https://api.crossref.org/works/{clean_doi}"
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "SciHub-MCP-Server/1.0 (mailto:admin@isparmo.com)"},
            timeout=10
        )
        if resp.status_code == 200:
            item = resp.json().get("message", {})
            title = item.get("title", [""])[0] if item.get("title") else ""
            authors = []
            for a in item.get("author", []):
                name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                if name:
                    authors.append(name)
            year = ""
            published = item.get("published") or item.get("created") or item.get("issued")
            if published and "date-parts" in published and published["date-parts"]:
                year = str(published["date-parts"][0][0])
            journal = item.get("container-title", [""])[0] if item.get("container-title") else ""
            return {
                "doi": clean_doi,
                "title": title,
                "author": ", ".join(authors),
                "year": year,
                "journal": journal,
                "publisher": item.get("publisher", "")
            }
    except Exception as e:
        print(f"CrossRef error for DOI {clean_doi}: {e}")
    return {"doi": clean_doi}


def get_scihub_pdf_url(doi: str) -> str:
    """Find working Sci-Hub PDF URL across mirrors or python-scihub package."""
    clean_doi = clean_doi_string(doi)

    # 1. Try python scihub package if available
    try:
        from scihub import SciHub
        sh = SciHub()
        sh.timeout = 15
        res = sh.fetch(clean_doi)
        if res and res.get("url"):
            url = res["url"]
            if url.startswith("//"):
                url = "https:" + url
            return url
    except Exception:
        pass

    # 2. Try direct scraping of active Sci-Hub mirrors
    for mirror in SCIHUB_MIRRORS:
        try:
            target_url = f"{mirror}/{clean_doi}"
            resp = requests.get(target_url, headers=HEADERS, verify=False, timeout=12, allow_redirects=True)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Check iframe with PDF
                iframe = soup.find("iframe", id="pdf") or soup.find("iframe")
                if iframe and iframe.get("src"):
                    src = iframe["src"]
                    if src.startswith("//"):
                        return "https:" + src
                    elif src.startswith("/"):
                        return mirror + src
                    elif src.startswith("http"):
                        return src
                
                # Check embed PDF
                embed = soup.find("embed", type="application/pdf") or soup.find("embed")
                if embed and embed.get("src"):
                    src = embed["src"]
                    if src.startswith("//"):
                        return "https:" + src
                    elif src.startswith("/"):
                        return mirror + src
                    elif src.startswith("http"):
                        return src

                # Check download button
                button = soup.find("button", onclick=True)
                if button:
                    match = re.search(r"location\.href=['\"]([^'\"]+)['\"]", button["onclick"])
                    if match:
                        src = match.group(1)
                        if src.startswith("//"):
                            return "https:" + src
                        elif src.startswith("/"):
                            return mirror + src
                        elif src.startswith("http"):
                            return src
        except Exception:
            continue
            
    return ""


def search_paper_by_doi(doi: str) -> dict:
    """Search for a paper on Sci-Hub & CrossRef using its DOI."""
    clean_doi = clean_doi_string(doi)
    if not clean_doi:
        return {"doi": doi, "status": "error", "error": "Empty DOI provided."}
    
    meta = get_metadata_from_crossref(clean_doi)
    pdf_url = get_scihub_pdf_url(clean_doi)
    
    if pdf_url or meta.get("title"):
        return {
            "doi": clean_doi,
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "year": meta.get("year", ""),
            "journal": meta.get("journal", ""),
            "pdf_url": pdf_url or "",
            "status": "success" if pdf_url else "pdf_not_found",
            "message": "PDF link available" if pdf_url else "Metadata found, but PDF not available on Sci-Hub"
        }
    
    return {
        "doi": clean_doi,
        "status": "not_found",
        "error": f"Paper with DOI '{clean_doi}' was not found."
    }


def search_scihub_direct(query: str, limit: int = 5) -> list:
    """Search directly on Sci-Hub mirror search engine for papers that exist in Sci-Hub."""
    papers = []
    search_mirrors = [
        "https://sci-hub.reatk.com/search/?q=",
        "https://sci-hub.se/search/?q="
    ]
    
    for base_url in search_mirrors:
        try:
            url = f"{base_url}{requests.utils.quote(query.strip())}"
            resp = requests.get(url, headers=HEADERS, verify=False, timeout=12)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Check for <a class="article" href="/10....">
                article_links = soup.find_all("a", class_="article")
                if not article_links:
                    article_links = [a for a in soup.find_all("a") if a.get("href", "").lstrip("/").startswith("10.")]
                
                for art in article_links[:limit]:
                    doi = art.get("href", "").lstrip("/")
                    if doi.startswith("10.") and not any(p.get("doi") == doi for p in papers):
                        paper_data = search_paper_by_doi(doi)
                        papers.append(paper_data)
                
                if papers:
                    break
        except Exception as e:
            print(f"Direct Sci-Hub search error on {base_url}: {e}")
            continue

    return papers


def search_paper_by_title(title: str) -> dict:
    """Search for a paper by title using Sci-Hub direct search first, then CrossRef fallback."""
    if not title or not title.strip():
        return {"title": title, "status": "error", "error": "Empty title provided."}
    
    # 1. Try direct search on Sci-Hub
    direct_results = search_scihub_direct(title, limit=1)
    if direct_results and direct_results[0].get("status") == "success":
        return direct_results[0]
    
    # 2. Fallback to CrossRef to resolve DOI
    try:
        url = f"https://api.crossref.org/works?query.title={requests.utils.quote(title.strip())}&rows=1"
        resp = requests.get(url, headers={"User-Agent": "SciHub-MCP-Server/1.0 (mailto:admin@isparmo.com)"}, timeout=10)
        if resp.status_code == 200:
            items = resp.json().get("message", {}).get("items", [])
            if items and items[0].get("DOI"):
                return search_paper_by_doi(items[0]["DOI"])
    except Exception as e:
        print(f"CrossRef search error: {e}")
    
    return {
        "title": title,
        "status": "not_found",
        "error": f"No paper found matching title '{title}'."
    }


def search_papers_by_keyword(keyword: str, num_results: int = 5) -> list:
    """Search for papers matching keywords, prioritizing papers available on Sci-Hub."""
    if not keyword or not keyword.strip():
        return []
    
    limit = max(1, min(int(num_results), 20))
    
    # 1. Search directly on Sci-Hub mirror search engines first (guarantees papers are on Sci-Hub)
    papers = search_scihub_direct(keyword, limit=limit)
    
    # 2. If results are fewer than requested and keyword contains stopwords (like 'and', 'or', 'in'),
    # try cleaning stopwords to find additional relevant papers on Sci-Hub
    if len(papers) < limit:
        cleaned_kw = re.sub(r'\b(and|or|in|the|with|for|of|dan|yang|di)\b', ' ', keyword, flags=re.IGNORECASE)
        cleaned_kw = ' '.join(cleaned_kw.split())
        if cleaned_kw.lower() != keyword.strip().lower():
            more_papers = search_scihub_direct(cleaned_kw, limit=limit)
            for p in more_papers:
                if not any(existing.get("doi") == p.get("doi") for existing in papers):
                    papers.append(p)
                    if len(papers) >= limit:
                        break

    if papers:
        return papers

    # 3. Fallback to CrossRef API if direct Sci-Hub search returned empty
    try:
        url = f"https://api.crossref.org/works?query={requests.utils.quote(keyword.strip())}&rows={limit}"
        resp = requests.get(url, headers={"User-Agent": "SciHub-MCP-Server/1.0 (mailto:admin@isparmo.com)"}, timeout=10)
        if resp.status_code == 200:
            items = resp.json().get("message", {}).get("items", [])
            for item in items:
                doi = item.get("DOI")
                if doi and not any(p.get("doi") == doi for p in papers):
                    paper_data = search_paper_by_doi(doi)
                    papers.append(paper_data)
                    if len(papers) >= limit:
                        break
    except Exception as e:
        print(f"Keyword search error: {e}")
        papers.append({"error": str(e), "status": "error"})
    
    return papers


def download_paper(pdf_url: str, output_path: str) -> bool:
    """Download paper PDF from given URL to a local destination."""
    try:
        if not pdf_url:
            return False
        resp = requests.get(pdf_url, headers=HEADERS, verify=False, timeout=30, stream=True)
        if resp.status_code == 200:
            dir_name = os.path.dirname(os.path.abspath(output_path))
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        return False
    except Exception as e:
        print(f"Download error: {e}")
        return False
