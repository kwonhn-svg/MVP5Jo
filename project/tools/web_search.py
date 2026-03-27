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
