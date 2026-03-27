"""
B2B Account Intelligence 에이전트 메인 루프
OpenAI (GPT-4o)와 도구를 활용한 자율적 에이전트 구현
"""

import os
import json
from datetime import datetime
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

from tools import TOOLS, execute_tool
from prompts import SYSTEM_PROMPT

# 환경변수 로드
load_dotenv()


def run_agent(company_name: str) -> str:
    """
    B2B Account Intelligence 에이전트 메인 루프
    
    Args:
        company_name (str): 분석할 회사명
        
    Returns:
        str: 생성된 영업 브리핑 리포트
    """
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "❌ 오류: OPENAI_API_KEY 환경변수가 설정되지 않았습니다."
    
    # OpenAI 클라이언트 초기화
    client = OpenAI(api_key=api_key)
    
    # 초기 메시지
    user_message = f"아래 회사를 분석해서 영업 브리핑 리포트를 작성해주세요:\n\n회사명: {company_name}"
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    print(f"\n🚀 {company_name} 분석 시작...\n")
    
    step = 1
    max_steps = 15
    
    # 에이전트 루프
    while step <= max_steps:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=8192,
            tools=TOOLS,
            messages=messages
        )
        
        # 응답 처리
        finish_reason = response.choices[0].finish_reason
        assistant_message = response.choices[0].message
        
        if finish_reason == "tool_calls":
            # 도구 호출 처리
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": assistant_message.tool_calls
            })
            
            # 각 도구 호출 처리
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                tool_id = tool_call.id
                
                # 도구 실행 로깅
                print(f"[Step {step}] 도구 호출: {tool_name} | 입력: {json.dumps(tool_input, ensure_ascii=False)}")
                
                # 도구 실행
                tool_result = execute_tool(tool_name, tool_input)
                
                # 결과를 메시지에 추가
                messages.append({
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_id
                })
            
            step += 1
        
        elif finish_reason == "stop":
            # 최종 텍스트 반환
            final_text = assistant_message.content
            print(f"\n✅ [Step {step}] 분석 완료!\n")
            return final_text if final_text else ""
        
        else:
            # 예상치 못한 finish_reason
            print(f"⚠️  예상치 못한 finish_reason: {finish_reason}")
            break
    
    # 최대 스텝 초과
    print(f"\n⚠️  경고: 최대 반복 횟수({max_steps})를 초과했습니다.")
    final_text = assistant_message.content if assistant_message.content else ""
    return final_text if final_text else f"분석 중 오류가 발생했습니다."


def save_report(company_name: str, report_content: str) -> str:
    """
    리포트를 마크다운 파일로 저장합니다.
    
    Args:
        company_name (str): 회사명
        report_content (str): 리포트 내용
        
    Returns:
        str: 저장된 파일 경로
    """
    # 타임스탬프 생성 (YYYYMMDD_HHMM)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"briefing_{company_name}_{timestamp}.md"
    
    # 파일 저장
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    return filename


def main():
    """메인 진입점"""
    print("\n" + "=" * 60)
    print("📊 B2B Account Intelligence 에이전트")
    print("=" * 60 + "\n")
    
    # 회사명 입력
    company_name = input("분석할 회사명을 입력하세요: ").strip()
    
    if not company_name:
        print("❌ 회사명을 입력해주세요.")
        return
    
    # 에이전트 실행
    report = run_agent(company_name)
    
    # 리포트 저장
    filepath = save_report(company_name, report)
    
    print(f"\n✅ 리포트 저장 완료!")
    print(f"📄 파일: {filepath}")
    print("\n" + "=" * 60)
    print("분석을 완료했습니다.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
