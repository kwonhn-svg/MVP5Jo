"""
B2B Account Intelligence Agent
단일 에이전트 루프: Claude가 도구를 자율적으로 호출해 최종 브리핑 생성
"""
import os
import json
import anthropic
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# ── 1. 도구 정의 ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "web_search",
        "description": "회사 관련 최신 뉴스·재무·동향을 검색합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "검색어 (예: '카카오 2025 최신 뉴스')"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "web_fetch",
        "description": "특정 URL의 웹페이지 본문을 가져옵니다. 뉴스 기사나 공시 원문 확인 시 사용하세요.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "가져올 페이지 URL"}
            },
            "required": ["url"],
        },
    },
    {
        "name": "search_hiring",
        "description": "회사의 최근 채용공고를 검색해 조직·전략 신호를 파악합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "채용 공고를 검색할 회사명"}
            },
            "required": ["company_name"],
        },
    },
]

SYSTEM_PROMPT = """당신은 B2B 영업 전문가입니다.
주어진 도구를 적극적으로 활용해 회사 정보를 수집하고,
영업 담당자가 고객사 미팅 직전에 바로 활용할 수 있는 브리핑 문서를 작성합니다.

도구 활용 전략:
- web_search: 최신 뉴스, 재무 현황, 기업 개요 수집 (최소 4~5회 호출)
- search_hiring: 채용 공고로 조직 변화·투자 방향 파악
- web_fetch: 중요 기사나 공시 원문 상세 확인

최종 브리핑 문서에 반드시 포함할 항목:
1. 기업 스냅샷 (업종·규모·핵심 사업·주요 고객)
2. 최신 뉴스 및 동향 (최근 3개월, 영업 시사점 포함)
3. 조직·전략 신호 (채용 공고 분석)
4. 재무·투자 현황
5. 핵심 페인포인트 (근거 포함)
6. 추천 영업 전략
   - 오프닝 멘트 예시
   - 핵심 질문 3가지
   - 강조할 가치 제안
7. 주의사항 및 리스크

마크다운 형식으로 작성하고, 구체적·실용적인 내용을 담아주세요."""


# ── 2. 도구 실행 함수 ─────────────────────────────────────────────────────────

def _web_search(query: str) -> str:
    try:
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = tavily.search(query=query, max_results=5, search_depth="advanced")
        items = [
            f"제목: {r.get('title', '')}\n내용: {r.get('content', '')}\nURL: {r.get('url', '')}"
            for r in results.get("results", [])
        ]
        return "\n\n---\n\n".join(items) if items else "검색 결과 없음"
    except Exception as e:
        return f"검색 실패: {e}"


def _web_fetch(url: str) -> str:
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SalesAgent/1.0)"},
        )
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        # 너무 긴 경우 앞부분만 사용
        return text[:4000] if len(text) > 4000 else text
    except Exception as e:
        return f"페이지 로드 실패: {e}"


def _search_hiring(company_name: str) -> str:
    try:
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = tavily.search(
            query=f"{company_name} 채용공고 2025 원티드 사람인 직무",
            max_results=5,
            search_depth="advanced",
        )
        items = [
            f"제목: {r.get('title', '')}\n내용: {r.get('content', '')}\nURL: {r.get('url', '')}"
            for r in results.get("results", [])
        ]
        return "\n\n---\n\n".join(items) if items else "채용 공고 없음"
    except Exception as e:
        return f"채용 검색 실패: {e}"


def execute_tools(content_blocks: list) -> list:
    """Claude의 tool_use 블록을 실행하고 tool_result 리스트 반환"""
    results = []
    for block in content_blocks:
        if block.type != "tool_use":
            continue

        print(f"  🔧 {block.name}({json.dumps(block.input, ensure_ascii=False)})")

        if block.name == "web_search":
            output = _web_search(block.input["query"])
        elif block.name == "web_fetch":
            output = _web_fetch(block.input["url"])
        elif block.name == "search_hiring":
            output = _search_hiring(block.input["company_name"])
        else:
            output = f"알 수 없는 도구: {block.name}"

        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": output,
        })
    return results


# ── 3. 에이전트 루프 ──────────────────────────────────────────────────────────

def run_agent(company_name: str) -> str:
    """
    회사명 입력 → Claude가 도구를 자율 호출 → 최종 브리핑 반환
    """
    client = anthropic.Anthropic()
    today = date.today().strftime("%Y년 %m월 %d일")

    messages = [
        {
            "role": "user",
            "content": (
                f"오늘은 {today}입니다.\n"
                f"**{company_name}**에 대한 영업 브리핑 리포트를 작성해주세요.\n"
                "도구를 충분히 활용해 최신 정보를 수집한 뒤 완성도 높은 문서를 만들어 주세요."
            ),
        }
    ]

    turn = 0
    print(f"\n{'='*60}")
    print(f"🚀 [{company_name}] 영업 브리핑 생성 시작")
    print(f"{'='*60}\n")

    while True:
        turn += 1
        print(f"[Turn {turn}] Claude 호출 중...")

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            tools=TOOLS,
            system=SYSTEM_PROMPT,
            messages=messages,
        )

        # 도구 호출 없이 최종 리포트 완성
        if response.stop_reason == "end_turn":
            print(f"\n✅ 브리핑 완성 (총 {turn}턴)\n")
            return next(b.text for b in response.content if b.type == "text")

        # 도구 호출 실행
        tool_results = execute_tools(response.content)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})


# ── 4. 직접 실행 ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    company = input("회사명 입력: ").strip() or "카카오"

    report = run_agent(company)

    # 마크다운 파일로 저장
    filename = f"briefing_{company}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n📄 저장 완료: {filename}")
