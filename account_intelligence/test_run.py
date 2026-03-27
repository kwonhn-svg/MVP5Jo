#!/usr/bin/env python3
"""
B2B Account Intelligence 에이전트 테스트 실행
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from agent import run_agent, save_report

def main():
    """테스트 실행"""
    # 테스트할 회사명
    test_companies = ["Google", "Microsoft", "Tesla"]
    
    print("\n" + "=" * 60)
    print("📊 B2B Account Intelligence 에이전트 - 테스트 실행")
    print("=" * 60 + "\n")
    
    # 첫 번째 회사로 테스트
    company = test_companies[0]
    
    print(f"테스트 회사: {company}")
    print(f"OpenAI API 키: {'✅ 설정됨' if os.getenv('OPENAI_API_KEY') else '❌ 미설정'}\n")
    
    # 에이전트 실행
    report = run_agent(company)
    
    # 리포트 저장
    filepath = save_report(company, report)
    
    print(f"\n✅ 테스트 완료!")
    print(f"📄 생성 파일: {filepath}")
    
    # 파일 내용 미리보기
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        preview = content[:500]
        print(f"\n📋 리포트 미리보기:\n{preview}\n...")

if __name__ == "__main__":
    main()
