# 📊 B2B Account Intelligence 에이전트

회사명을 입력하면 **3개의 도구**를 자율적으로 호출하여 정보를 수집하고, **영업 브리핑 리포트**를 자동 생성하는 Claude 기반 AI 에이전트입니다.

## 🎯 주요 기능

### 자율적 도구 호출
1. **web_search** - 회사 관련 최신 뉴스와 동향 검색
2. **web_fetch** - 공식 홈페이지 직접 수집
3. **search_hiring** - 최근 채용공고로 조직 시그널 파악

### 자동 리포트 생성
- 기업 개요
- 최근 동향
- 조직 & 채용 시그널
- 추정 페인포인트
- 영업 접근 앵글 제안
- 미팅 전 체크리스트

---

## 📁 파일 구조

```
account_intelligence/
├── agent.py              # 메인 에이전트 루프 (while True 루프, 도구 호출, 리포트 생성)
├── tools.py              # 3개 도구 구현 (web_search, web_fetch, search_hiring)
├── prompts.py            # SYSTEM_PROMPT 정의 (도구 호출 순서, 리포트 형식)
├── requirements.txt      # 의존성: anthropic, requests, beautifulsoup4, python-dotenv
├── .env.example          # 환경변수 예시
└── README.md             # 이 파일
```

---

## 🔧 설치 및 설정

### 1단계: 환경변수 설정

`.env.example`을 `.env`로 복사하고 API 키를 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 수정:
```env
# Anthropic API 키 (Claude 사용)
ANTHROPIC_API_KEY=sk-ant-...

# Tavily API 키 (웹 검색용)
TAVILY_API_KEY=tvly-...
```

**API 키 구하기:**
- [Anthropic API](https://console.anthropic.com/) - ANTHROPIC_API_KEY
- [Tavily Search API](https://tavily.com/) - TAVILY_API_KEY

### 2단계: 패키지 설치 ✅ (이미 완료)

```bash
# 이미 설치됨
pip install -r requirements.txt
```

**설치된 패키지:**
- `anthropic==0.86.0` - Claude API
- `requests==2.33.0` - HTTP 요청
- `beautifulsoup4==4.12.3` - 웹 스크래이핑
- `python-dotenv==1.0.1` - 환경변수 관리

---

## 🚀 실행 방법

### 기본 사용법

```bash
python account_intelligence/agent.py
```

**실행 흐름:**

```
📊 B2B Account Intelligence 에이전트

분석할 회사명을 입력하세요: Google

🚀 Google 분석 시작...

[Step 1] 도구 호출: web_search | 입력: {"query": "Google 최근 뉴스 이슈 2025"}
[Step 2] 도구 호출: web_search | 입력: {"query": "Google 사업 전략 신규 서비스"}
[Step 3] 도구 호출: web_fetch | 입력: {"url": "google.com"}
[Step 4] 도구 호출: search_hiring | 입력: {"company_name": "Google"}

✅ [Step 4] 분석 완료!

✅ 리포트 저장 완료!
📄 파일: briefing_Google_20250327_1430.md
```

### 생성된 리포트 파일

```markdown
# Google 영업 브리핑 리포트
**생성일**: 2025-03-27

## 1. 기업 개요
Google은 AI, 클라우드, 검색 등 다양한 디지털 서비스를 제공하는 글로벌 기술 기업입니다...

## 2. 최근 동향 (최근 3개월)
- Google Gemini 2.0 출시
- AI 검색 기능 확대
- ...

## 3. 조직 & 채용 시그널
- AI/ML 엔지니어 대량 채용 중
- 클라우드 부문 확장
- ...

## 4. 추정 페인포인트
- ...

## 5. 영업 접근 앵글 제안
- ...

## 6. 미팅 전 체크리스트
- ...
```

---

## 🔄 에이전트 루프 동작 원리

### stop_reason별 처리

```python
while step <= 15:  # 최대 15회 반복
    response = client.messages.create(...)
    
    if response.stop_reason == "tool_use":
        # 도구 호출
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                messages.append(tool_result)
        step += 1
    
    elif response.stop_reason == "end_turn":
        # 최종 텍스트 반환
        return final_text
```

### 필수 도구 호출 순서

SYSTEM_PROMPT에서 지정한 순서:

1. **web_search** - "{회사명} 최근 뉴스 이슈 2025"
2. **web_search** - "{회사명} 사업 전략 신규 서비스"
3. **web_fetch** - "{회사명} 공식 홈페이지"
4. **search_hiring** - "{회사명} 채용공고"

---

## 🛠️ 도구 상세 설명

### 1️⃣ web_search
```python
def web_search(query: str) -> str:
    """회사 관련 최신 뉴스와 동향을 검색합니다"""
    # Tavily API POST https://api.tavily.com/search
    # - search_depth: "basic"
    # - max_results: 5
    # - include_answer: true
    # 반환: answer 요약 + 각 결과의 title/url/content(300자)
```

### 2️⃣ web_fetch
```python
def web_fetch(url: str) -> str:
    """특정 URL의 웹페이지 내용을 가져옵니다"""
    # requests.get + BeautifulSoup
    # - User-Agent 헤더 설정
    # - script, style, nav, footer, header 태그 제거
    # - 최대 2000자로 자르기
    # - 타임아웃: 10초
```

### 3️⃣ search_hiring
```python
def search_hiring(company_name: str) -> str:
    """회사의 최근 채용공고를 검색합니다"""
    # Tavily API 사용
    # - query: "{company_name} 채용공고 2025 site:wanted.co.kr OR site:jumpit.co.kr"
    # - max_results: 5
    # 반환: 채용공고 title + content(400자)
```

---

## ⚙️ 환경변수

### 필수 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `ANTHROPIC_API_KEY` | Claude API 키 | `sk-ant-abc123...` |
| `TAVILY_API_KEY` | Tavily 검색 API 키 | `tvly-abc123...` |

---

## 📊 기술 스택

| 항목 | 버전 |
|------|------|
| Python | 3.11+ |
| anthropic | 0.86.0 |
| requests | 2.33.0 |
| beautifulsoup4 | 4.12.3 |
| python-dotenv | 1.0.1 |

---

## 🎓 사용 예시

### 예시 1: 스타트업 분석

```bash
python account_intelligence/agent.py
분석할 회사명을 입력하세요: OpenAI
```

**생성 파일:** `briefing_OpenAI_20250327_1430.md`

### 예시 2: 대기업 분석

```bash
python account_intelligence/agent.py
분석할 회사명을 입력하세요: Microsoft
```

**생성 파일:** `briefing_Microsoft_20250327_1435.md`

### 예시 3: 한국 기업 분석

```bash
python account_intelligence/agent.py
분석할 회사명을 입력하세요: NAVER
```

**생성 파일:** `briefing_NAVER_20250327_1440.md`

---

## 🐛 문제 해결

### ❌ ANTHROPIC_API_KEY 오류
```
❌ 오류: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.
```
→ `.env` 파일에 API 키를 입력하세요

### ❌ TAVILY_API_KEY 오류
```
❌ 오류: TAVILY_API_KEY 환경변수가 설정되지 않았습니다.
```
→ [Tavily API](https://tavily.com/)에서 API 키를 발급받으세요

### ❌ 타임아웃 오류
```
❌ 오류: 요청 시간 초과 (10초)
```
→ 네트워크 연결을 확인하세요

### ❌ 채용공고 검색 실패
```
최근 채용공고가 없습니다.
```
→ 회사명이 정확한지 확인하세요

---

## 📝 로그 및 디버깅

### 각 스텝 확인

실행 중 각 도구 호출이 콘솔에 출력됩니다:

```
[Step 1] 도구 호출: web_search | 입력: {...}
[Step 2] 도구 호출: web_search | 입력: {...}
[Step 3] 도구 호출: web_fetch | 입력: {...}
[Step 4] 도구 호출: search_hiring | 입력: {...}
```

### 최대 반복 초과

15회 이상 도구 호출 시:
```
⚠️  경고: 최대 반복 횟수(15)를 초과했습니다.
```

---

## 🎯 다음 단계

1. **리포트 검토** - 생성된 `.md` 파일 확인
2. **영업 브리핑** - 리포트 내용으로 팀 회의
3. **접근 전략** - "영업 접근 앵글 제안" 참고
4. **미팅 준비** - "미팅 전 체크리스트" 활용

---

## 📞 지원

필요한 경우:
- API 키 문제: Anthropic/Tavily 공식 문서 참고
- 코드 수정: `agent.py`, `tools.py`, `prompts.py` 확인

---

**Happy Sales Intelligence! 🚀**
