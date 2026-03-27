from tools.web_search import web_search


def search_hiring_signals(company_name: str, max_results: int = 5) -> list[dict]:
    """채용 공고를 검색하여 회사의 성장 신호를 파악"""
    query = f"{company_name} 채용 공고 2024 2025"
    results = web_search(query, max_results=max_results)
    return results


def search_hiring_by_role(company_name: str, role: str, max_results: int = 5) -> list[dict]:
    """특정 직군 채용 여부로 사업 방향 파악"""
    query = f"{company_name} {role} 채용"
    results = web_search(query, max_results=max_results)
    return results
