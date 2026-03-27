import os
from openai import AsyncOpenAI


async def run_news_agent(company_name: str) -> str:
    """최신 뉴스 및 동향 수집 (OpenAI 웹 검색)"""
    client = AsyncOpenAI()
    response = await client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=f"""{company_name}의 최신 뉴스와 동향을 웹에서 검색해서 영업 담당자 관점으로 정리해줘.

## 최신 뉴스 및 동향
- 주요 뉴스 3~5개 (불릿 포인트, 각 뉴스가 영업에 주는 시사점 포함)
- 사업 확장/축소/전환 신호
- 파트너십·M&A·투자 현황
- 미팅 대화 포인트

마크다운으로 작성해.""",
    )
    return response.output_text
