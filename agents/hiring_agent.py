import os
from openai import AsyncOpenAI


async def run_hiring_agent(company_name: str) -> str:
    """채용 공고 검색 → 조직·전략 신호 추출 (OpenAI 웹 검색)"""
    client = AsyncOpenAI()
    response = await client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=f"""{company_name}의 최근 채용 공고를 웹에서 검색해서 조직 변화와 전략 신호를 분석해줘.

## 채용 공고 → 조직·전략 신호
- 주요 채용 직군 및 역할 (어떤 역량을 강화하려는가)
- 조직 확장 영역 (신사업, 기술 투자 방향)
- 기술 스택 변화 (도입 중인 기술/플랫폼)
- 전략적 우선순위 (채용 공고에서 읽히는 경영 방향)
- 의사결정권자 역할 (영업 접점이 될 수 있는 포지션)

마크다운으로 작성해.""",
    )
    return response.output_text
