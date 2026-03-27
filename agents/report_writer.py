import os
from openai import AsyncOpenAI
from datetime import date


async def run_report_writer(
    company_name: str,
    news_summary: str,
    hiring_summary: str,
    web_summary: str,
    analyst_summary: str,
) -> str:
    """최종 영업 브리핑 문서 생성"""
    client = AsyncOpenAI()
    today = date.today().strftime("%Y년 %m월 %d일")

    response = await client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4o"),
        max_tokens=4000,
        messages=[
            {
                "role": "system",
                "content": "당신은 B2B 영업 전문가입니다. 분석 자료를 바탕으로 영업 담당자가 미팅에서 바로 활용할 수 있는 구체적인 브리핑 문서를 작성합니다.",
            },
            {
                "role": "user",
                "content": f"""다음 분석 자료를 바탕으로 {company_name} 고객사 미팅을 위한 영업 브리핑 문서를 작성해주세요.

=== 기업 개요 및 재무 ===
{web_summary}

=== 최신 뉴스 및 동향 ===
{news_summary}

=== 채용 공고 분석 ===
{hiring_summary}

=== 페인포인트 및 기회 분석 ===
{analyst_summary}

---

# {company_name} 영업 브리핑
**작성일:** {today}
**미팅 목적:** 신규 비즈니스 기회 탐색

---

## 1. 기업 스냅샷
(업종, 규모, 핵심 사업, 주요 고객을 2~3문장으로)

## 2. 최신 동향 (지난 3개월)
(뉴스·이슈 중 영업에 중요한 것 3~5개, 각 항목에 영업적 시사점 포함)

## 3. 조직·전략 신호
(채용 공고에서 읽은 전략적 방향과 투자 우선순위)

## 4. 재무·투자 현황
(예산 가용성과 투자 여력을 판단할 수 있는 정보)

## 5. 핵심 페인포인트
(가장 중요한 문제 3개, 각각 어떤 솔루션이 도움이 될지 연결)

## 6. 추천 영업 전략
### 오프닝 멘트 예시
(첫 대화를 자연스럽게 시작할 수 있는 실제 문장 예시)

### 핵심 질문 3가지
(고객의 니즈를 파악하고 우리 솔루션으로 연결할 수 있는 질문)

### 강조할 가치 제안
(이 고객사에 특화된 가치 제안 포인트)

## 7. 주의사항 및 리스크
(미팅 전 알아야 할 민감한 이슈나 주의점)

---
*이 브리핑은 AI가 공개 정보를 기반으로 자동 생성했습니다. 미팅 전 최신 정보를 추가로 확인하세요.*""",
            },
        ],
    )
    return response.choices[0].message.content
