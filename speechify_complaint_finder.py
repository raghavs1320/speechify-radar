"""
Speechify Complaint & Churn Lead Finder (Universal Web & Reddit Search)
----------------------------------------------------------------------
Searches for real-time complaints, angry reviews, and churn discussions 
about Speechify across Reddit, Trustpilot, and tech forums.
"""

import json
import urllib.parse
import urllib.request
import re
from html import unescape
from datetime import datetime

def search_duckduckgo_lite(query, max_results=10):
    """
    Performs a lightweight web search using DuckDuckGo HTML lite.
    No API keys required, works for Reddit, Trustpilot, and forums.
    """
    url = "https://html.duckduckgo.com/html/"
    params = urllib.parse.urlencode({"q": query}).encode("utf-8")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, data=params, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
            
            # Extract links and snippets
            # Results are in <a class="result__snippet" ...> or <div class="result__snippet">
            results = []
            snippets = re.findall(r'<a class="result__snippet[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            titles = re.findall(r'<a class="result__url[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            
            # Alternative pattern for standard DDG HTML
            blocks = re.findall(r'<div class="result__body">(.*?)</div>\s*</div>', html, re.DOTALL)
            for block in blocks:
                title_match = re.search(r'<h2 class="result__title">.*?href="([^"]+)".*?>(.*?)</a>', block, re.DOTALL)
                snippet_match = re.search(r'<a class="result__snippet".*?>(.*?)</a>', block, re.DOTALL)
                
                if title_match:
                    raw_url = title_match.group(1)
                    # Decode DDG redirect url
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                    target_url = parsed.get("uddg", [raw_url])[0]
                    
                    title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
                    title = unescape(title)
                    
                    snippet = ""
                    if snippet_match:
                        snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                        snippet = unescape(snippet)
                        
                    results.append({
                        "title": title,
                        "url": target_url,
                        "snippet": snippet
                    })
                    if len(results) >= max_results:
                        break
            return results
    except Exception as e:
        print(f"[!] Search error: {e}")
        return []

def classify_pain_point(text):
    t = text.lower()
    if any(k in t for k in ["charge", "refund", "trial", "annual", "billed", "$140", "$150", "$200", "bank", "scam"]):
        return "Billing & Unexpected Charges"
    elif any(k in t for k in ["alternative", "switch", "better", "replace"]):
        return "Actively Seeking Alternatives"
    elif any(k in t for k in ["pdf", "bug", "crash", "sync", "freeze", "robotic", "voice", "footnote"]):
        return "Voice Quality & Product Glitches"
    return "General Discontent"

def pitch_recommendation(pain_point):
    guide = {
        "Billing & Unexpected Charges": "Pitch: Transparent monthly pricing, immediate self-serve cancellation, no surprise $150 annual locks.",
        "Actively Seeking Alternatives": "Pitch: Natural AI voice quality (ElevenLabs grade) with half the price and generous trial.",
        "Voice Quality & Product Glitches": "Pitch: Perfect PDF/academic paper reading (ignores footnotes, page headers, citation brackets).",
        "General Discontent": "Pitch: Lightweight, fast browser extension without aggressive marketing popups."
    }
    return guide.get(pain_point, "Pitch: Friendly helpful advice.")

def main():
    print("=" * 65)
    print("🔍 SPEECHIFY REAL-TIME COMPLAINT & CHURN RADAR")
    print("=" * 65)
    
    query = 'site:reddit.com speechify (scam OR refund OR cancel OR overpriced OR alternative)'
    print(f"[*] Crawling live forum discussions: {query}\n")
    
    raw_results = search_duckduckgo_lite(query, max_results=8)
    
    if not raw_results:
        # Fallback query
        query2 = 'speechify complaints reviews trustpilot reddit'
        raw_results = search_duckduckgo_lite(query2, max_results=8)

    leads = []
    for item in raw_results:
        text = f"{item['title']} {item['snippet']}"
        pain = classify_pain_point(text)
        lead = {
            "title": item["title"],
            "url": item["url"],
            "pain_point": pain,
            "pitch_angle": pitch_recommendation(pain),
            "snippet": item["snippet"]
        }
        leads.append(lead)

    print(f"[✓] Discovered {len(leads)} live customer complaint threads!\n")
    for idx, lead in enumerate(leads, 1):
        print(f"[{idx}] {lead['title']}")
        print(f"    Source: {lead['url']}")
        print(f"    Core Pain Point: {lead['pain_point']}")
        print(f"    🎯 Outreach Strategy: {lead['pitch_angle']}")
        print(f"    Context: {lead['snippet'][:180]}...")
        print("-" * 65)

    with open("speechify_complaints_report.json", "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)
    print("\n[✓] Generated 'speechify_complaints_report.json' ready for CRM / Outreach sync.")

if __name__ == "__main__":
    main()
