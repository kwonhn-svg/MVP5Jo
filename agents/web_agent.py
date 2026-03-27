import os
from openai import AsyncOpenAI


async def run_web_agent(company_name: str) -> str:
    """기업 개요·재무·주요 인물 수집 (OpenAI 웹 검색)"""
    client = AsyncOpenAI()
    response = await client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=f"""{company_name}의 기업 개요, 재무 현황, 주요 인물을 웹에서 검색해서 정리해줘.

## 기업 개요
- 업종·사업 분야
- 규모 (직원 수, 매출 규모 추정)
- 주요 제품·서비스
- 주요 고객사·파트너

## 재무·투자 현황
- 최근 실적 동향
- 투자 유치 또는 재무 이슈
- 성장/수익성 지표

## 주요 인물
- C-레벨 임원 (영업 접근 시 참고)

마크다운으로 작성해.""",
    )
    return response.output_text
