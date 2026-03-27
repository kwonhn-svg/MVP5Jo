from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """DuckDuckGo로 웹 검색 후 결과 반환"""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            })
    return results

def search_dart_url(company_name: str) -> str:
    """DART에서 회사명으로 공시 페이지 URL을 찾아서 반환"""
    query = f"site:dart.fss.or.kr {company_name} 사업보고서"
    results = web_search(query, max_results=3)
    for r in results:
        if "dart.fss.or.kr" in r.get("url", ""):
            return r["url"]

    # dart에서 못 찾으면 네이버 금융으로 fallback
    query2 = f"site:finance.naver.com {company_name} 기업정보"
    results2 = web_search(query2, max_results=3)
    for r in results2:
        if "finance.naver.com" in r.get("url", ""):
            return r["url"]

    return ""