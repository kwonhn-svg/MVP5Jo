import os
from openai import AsyncOpenAI


async def run_analyst_agent(
    company_name: str,
    news_summary: str,
    hiring_summary: str,
    web_summary: str,
) -> str:
    """수집된 정보 → 페인포인트·인사이트 분석"""
    client = AsyncOpenAI()
    response = await client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4o"),
        max_tokens=3000,
        messages=[
            {
                "role": "system",
                "content": "당신은 B2B 영업 전략 전문가입니다. 수집된 기업 정보를 분석해 영업 기회를 발굴하는 것이 목표입니다.",
            },
            {
                "role": "user",
                "content": f"""{company_name}에 대해 수집된 정보를 종합 분석해주세요:

=== 최신 뉴스 및 동향 ===
{news_summary}

=== 채용 공고 분석 ===
{hiring_summary}

=== 기업 개요 및 재무 ===
{web_summary}

## 핵심 페인포인트
- 현재 겪고 있을 주요 비즈니스 문제 3~5개
- 각 문제의 근거 (어떤 정보에서 추론했는지)

## 경쟁 압박 및 시장 도전
- 경쟁사 대비 위협 요소
- 시장 변화로 인한 도전 과제

## 의사결정 트리거
- 현재 구매 의사결정을 촉진할 수 있는 요인
- 예산/조직 변화 신호

## 기회 영역
- 솔루션 도입이 필요할 수 있는 구체적 영역

마크다운으로 작성해.""",
            },
        ],
    )
    return response.choices[0].message.content
