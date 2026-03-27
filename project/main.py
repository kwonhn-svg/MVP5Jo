import json
import os
from openai import OpenAI
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT
from tools.web_search import web_search
from tools.web_fetch import web_fetch
from tools.hiring import search_hiring_signals, search_hiring_by_role
from tools import dart

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# OpenAI function calling용 툴 스펙 정의
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "웹에서 기업 관련 정보를 검색합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색 쿼리"},
                    "max_results": {"type": "integer", "description": "최대 결과 수 (기본 5)", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "특정 URL의 웹페이지 본문을 가져옵니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "가져올 URL"},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_hiring_signals",
            "description": "기업의 채용 공고를 검색하여 성장 신호를 파악합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "기업명"},
                    "max_results": {"type": "integer", "description": "최대 결과 수 (기본 5)", "default": 5},
                },
                "required": ["company_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_hiring_by_role",
            "description": "특정 직군 채용 여부로 사업 방향을 파악합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "기업명"},
                    "role": {"type": "string", "description": "직군명 (예: 데이터 엔지니어, 클라우드)"},
                    "max_results": {"type": "integer", "description": "최대 결과 수 (기본 5)", "default": 5},
                },
                "required": ["company_name", "role"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "dart_lookup",
            "description": "DART 전자공시 및 네이버 금융에서 기업의 재무 정보, 실적, 공시 내용을 조회합니다. 매출, 영업이익, 사업보고서 등 재무 관련 정보가 필요할 때 사용하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "조회할 기업명 (예: 카카오, 삼성전자)"},
                },
                "required": ["company_name"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "web_search": web_search,
    "web_fetch": web_fetch,
    "search_hiring_signals": search_hiring_signals,
    "search_hiring_by_role": search_hiring_by_role,
    "dart_lookup": dart.run,
}


def run_agent(company_name: str) -> str:
    """B2B Account Intelligence 에이전트 실행"""
    from datetime import datetime
    today = datetime.now().strftime("%Y년 %m월 %d일")
    print(f"\n[에이전트 시작] 조사 대상: {company_name}\n")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"'{company_name}' 기업에 대한 Account Intelligence 리포트를 작성해주세요. 오늘 날짜는 {today}입니다."},
    ]

    # 에이전트 루프
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        # 툴 호출이 없으면 최종 답변
        if not message.tool_calls:
            return message.content

        # 툴 실행
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            print(f"  [툴 호출] {fn_name}({fn_args})")
            result = TOOL_FUNCTIONS[fn_name](**fn_args)
            print(f"  [툴 결과] {str(result)[:100]}...")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })


def save_report(company_name: str, report: str) -> str:
    """리포트를 output 폴더에 저장"""
    os.makedirs("output", exist_ok=True)
    filename = f"output/{company_name.replace(' ', '_')}_report.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {company_name} Account Intelligence 리포트\n\n")
        f.write(report)
    return filename


# if __name__ == "__main__":
#     company = input("조사할 기업명을 입력하세요: ").strip()
#     if not company:
#         print("기업명을 입력해야 합니다.")
#     else:
#         report = run_agent(company)
#         print("\n" + "=" * 60)
#         print(report)
#         print("=" * 60)
#
#         filepath = save_report(company, report)
#         print(f"\n리포트 저장 완료: {filepath}")

if __name__ == "__main__":
    import sys
    from datetime import datetime

    company = sys.argv[2] if len(sys.argv) > 2 else "카카오"
    report = run_agent(company)

    os.makedirs("output", exist_ok=True)
    filename = f"output/{company}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n리포트 저장 완료: {filename}")
