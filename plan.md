# B2B Account Intelligence Agent — 구현 계획 (1일 완성)

## 목표
회사명 하나 입력 → 최신 동향·재무·조직·페인포인트 자동 수집·분석 → 영업 브리핑 문서 자동 생성

---

## 전체 아키텍처

```
회사명 입력
    │
    ▼
┌─────────────────────────────────────────────┐
│            Orchestrator Agent               │
│         (LangGraph + Claude)                │
│  서브 에이전트를 병렬 호출 후 결과 취합      │
└───────────────┬─────────────────────────────┘
                │ 병렬 호출
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐
│ News   │ │Hiring  │ │ Web    │
│ Agent  │ │ Agent  │ │ Agent  │
│(Tavily)│ │(Tavily)│ │(Tavily)│
└────────┘ └────────┘ └────────┘
    │           │           │
    └───────────┴───────────┘
                │ 취합
                ▼
    ┌───────────────────────┐
    │    Analyst Agent      │
    │  (패턴 분석·인사이트) │
    └───────────────────────┘
                │
                ▼
    ┌───────────────────────┐
    │  Report Writer Agent  │
    │  (브리핑 문서 생성)   │
    └───────────────────────┘
                │
                ▼
        Markdown 브리핑 출력 + Gradio UI
```

---

## 브리핑 문서 구성

| 섹션 | 담당 에이전트 |
|------|--------------|
| 기업 개요 (업종·규모·사업) | Web Agent |
| 최신 뉴스·동향 | News Agent |
| 채용 공고 → 조직·전략 신호 | Hiring Agent |
| 재무·투자 현황 | Web Agent |
| 페인포인트·경쟁 압박 | Analyst Agent |
| 영업 접근 전략·인사이트 | Report Writer Agent |

---

## 기술 스택

| 역할 | 기술 |
|------|------|
| 에이전트 프레임워크 | LangGraph |
| LLM | Claude (Anthropic SDK) |
| 검색 도구 | Tavily Search API |
| UI | Gradio |
| 추적 | LangSmith |

---

## 구현 순서 (1일, 4단계)

### Step 1 — 환경 세팅 및 동작 확인
- `anthropic`, `tavily-python` 패키지 설치
- `.env`에 `ANTHROPIC_API_KEY`, `TAVILY_API_KEY` 추가
- 단일 에이전트로 뉴스 수집 → 요약 동작 확인 (`day1_smoke_test.py`)

### Step 2 — 서브 에이전트 구현
- `NewsAgent`: 최신 뉴스 수집 + 요약
- `HiringAgent`: 채용 공고 → 조직/전략 신호 추출
- `WebAgent`: 기업 개요, 재무, 주요 인물 수집
- 각 에이전트를 LangGraph Tool 형태로 구현

### Step 3 — 오케스트레이터 + 분석 연결
- `OrchestratorAgent`: 서브 에이전트 3개 병렬 호출 (`Send` API)
- `AnalystAgent`: 취합 결과 → 페인포인트·인사이트 분석

### Step 4 — 리포트 생성 + Gradio UI
- `ReportWriterAgent`: Markdown 브리핑 문서 생성
- 엔드-투-엔드 테스트
- Gradio UI 연결 (`main.py`)

---

## 파일 구조 (완성 시)

```
MVP5Jo/
├── main.py                  # Gradio UI 진입점
├── day1_smoke_test.py       # Step 1 검증용
├── agents/
│   ├── __init__.py
│   ├── news_agent.py
│   ├── hiring_agent.py
│   ├── web_agent.py
│   ├── analyst_agent.py
│   ├── report_writer.py
│   └── orchestrator.py
└── .env                     # ANTHROPIC_API_KEY, TAVILY_API_KEY 추가 필요
```

---

## .env 추가 필요 항목

```
ANTHROPIC_API_KEY=...
TAVILY_API_KEY=...
```

---

## 검토 포인트
- Claude 모델: `claude-sonnet-4-6` 사용 (성능·비용 균형)
- Tavily 무료 플랜: 월 1,000회 검색 제한
- 병렬 호출: 서브 에이전트 3개 동시 실행
