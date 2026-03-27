from tools.web_search import web_search
from tools.web_fetch import web_fetch


def run(company_name: str = "") -> str:
    """
    web_search + web_fetch 조합으로 DART/네이버금융에서
    기업 재무·공시 정보를 수집해서 반환
    """
    company = company_name
    if not company:
        return "[ERROR] company_name이 입력되지 않았습니다."

    collected = []

    # --- 1단계: 네이버 금융에서 기업 기본 정보 ---
    naver_results = web_search(f"{company} 기업정보 매출 영업이익 site:finance.naver.com", max_results=3)
    for r in naver_results:
        url = r.get("url", "")
        if "finance.naver.com" in url:
            content = web_fetch(url)
            if "[ERROR]" not in content:
                collected.append(f"[네이버 금융 기업정보]\n{content[:1500]}")
            break

    # --- 2단계: 최근 실적·재무 뉴스 검색 ---
    news_results = web_search(f"{company} 매출 영업이익 실적 2024", max_results=5)
    snippets = []
    for r in news_results:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        url = r.get("url", "")
        if snippet:
            snippets.append(f"- {title}\n  {snippet}\n  출처: {url}")
    if snippets:
        collected.append(f"[재무·실적 관련 뉴스]\n" + "\n".join(snippets))

    # --- 3단계: DART 공시 검색 ---
    dart_results = web_search(f"{company} 공시 사업보고서 dart", max_results=5)
    dart_snippets = []
    for r in dart_results:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        url = r.get("url", "")
        if "dart" in url.lower() or "공시" in title:
            dart_snippets.append(f"- {title}\n  {snippet}\n  출처: {url}")

    # DART 페이지 직접 fetch 시도
    for r in dart_results:
        url = r.get("url", "")
        if "dart.fss.or.kr" in url:
            content = web_fetch(url)
            if "[ERROR]" not in content:
                dart_snippets.append(f"[DART 페이지 원문]\n{content[:1000]}")
            break

    if dart_snippets:
        collected.append(f"[DART 공시 정보]\n" + "\n".join(dart_snippets))

    # --- 결과 없을 때 ---
    if not collected:
        return f"[{company}] DART 및 재무 정보를 찾을 수 없습니다."

    return f"[{company} 재무·공시 정보]\n\n" + "\n\n".join(collected)