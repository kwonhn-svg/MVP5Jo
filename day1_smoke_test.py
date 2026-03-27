"""
Step 1 검증: 단일 뉴스 에이전트 동작 확인
실행: python day1_smoke_test.py
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    company = input("테스트할 회사명 입력 (기본값: 삼성전자): ").strip() or "삼성전자"

    # API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ .env 파일에 OPENAI_API_KEY를 설정해주세요.")
        return

    print(f"\n🔍 [{company}] 뉴스 에이전트 테스트 시작...\n")

    from agents.news_agent import run_news_agent
    result = await run_news_agent(company)

    print("✅ 뉴스 에이전트 결과:\n")
    print(result)
    print("\n✅ smoke test 통과! main.py를 실행해 전체 에이전트를 사용하세요.")


if __name__ == "__main__":
    asyncio.run(main())
