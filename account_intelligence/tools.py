"""
B2B Account Intelligence 에이전트용 도구 정의
3개의 도구: web_search, web_fetch, search_hiring
데모 버전 (빠른 응답)
"""

import json
from typing import Optional
import os


def web_search(query: str) -> str:
    """
    회사 관련 최신 뉴스와 동향을 검색합니다 (데모 버전).
    
    Args:
        query (str): 검색 쿼리
        
    Returns:
        str: 검색 결과 문자열
    """
    try:
        # 데모 데이터 (빠른 응답)
        demo_results = {
            "LG전자": [
                {"title": "LG전자, AI 반도체 사업 확대 발표", "body": "LG전자가 2025년 AI 반도체 분야 투자를 대폭 확대하기로 결정했습니다.", "href": "demo.com/1"},
                {"title": "LG디스플레이, OLED 생산 증설 계획", "body": "LG디스플레이가 OLED 패널 생산을 50% 증설할 계획을 발표했습니다.", "href": "demo.com/2"}
            ],
            "Google": [
                {"title": "Google, Gemini 3.0 AI 공개", "body": "Google이 새로운 Gemini 3.0 AI 모델을 발표했습니다.", "href": "demo.com/3"},
                {"title": "Google Cloud, AI 서비스 강화", "body": "Google Cloud가 기업용 AI 서비스를 대폭 강화하고 있습니다.", "href": "demo.com/4"}
            ]
        }
        
        result_text = f"📰 검색 쿼리: '{query}'\n\n"
        
        # 회사명 추출
        company = None
        for key in demo_results:
            if key.lower() in query.lower() or key in query:
                company = key
                break
        
        if company and company in demo_results:
            for i, result in enumerate(demo_results[company][:3], 1):
                title = result.get("title", "제목 없음")
                body = result.get("body", "")[:300]
                href = result.get("href", "")
                result_text += f"{i}. {title}\n"
                result_text += f"   내용: {body}\n\n"
        else:
            result_text += "관련 뉴스 정보가 있습니다.\n"
            result_text += "1. 최근 기술 동향\n"
            result_text += "   내용: 시장 변화에 대응하고 있습니다.\n\n"
        
        return result_text
        
    except Exception as e:
        return f"❌ 오류: 검색 실패 - {str(e)}"


def web_fetch(url: str) -> str:
    """
    특정 URL의 웹페이지 내용을 가져옵니다 (데모 버전).
    
    Args:
        url (str): 웹페이지 URL
        
    Returns:
        str: 정제된 웹페이지 텍스트
    """
    try:
        # 데모 데이터
        demo_content = {
            "google.com": """
            Google 공식 홈페이지
            
            About Google
            Google은 세계 최대의 검색 엔진 회사입니다.
            
            Our Products:
            - Search (검색)
            - Google Cloud (클라우드)
            - Android (모바일)
            - Chrome (브라우저)
            - YouTube (동영상)
            
            2025년 주요 전략:
            - AI 기술 강화
            - 클라우드 서비스 확대
            - 엔터프라이즈 솔루션 개발
            """,
            "lg.com": """
            LG 공식 홈페이지
            
            LG Electronics
            LG전자는 전자제품 제조 및 판매 회사입니다.
            
            Business Divisions:
            - Home Appliance (가전)
            - Consumer Electronics (소비자 전자)
            - Mobile (모바일)
            - Industrial Components (산업용 부품)
            
            2025년 전략:
            - AI 반도체 투자 확대
            - OLED 디스플레이 생산 증설
            - 스마트홈 솔루션 강화
            """
        }
        
        # 데모 응답
        result_text = f"📄 URL: {url}\n\n"
        
        for key in demo_content:
            if key in url.lower() or key in url:
                return result_text + demo_content[key]
        
        # 일반적인 응답
        return result_text + """
        기업 플러프 페이지 컨텐츠
        
        회사 소개
        이 회사는 혁신적인 기술 기업입니다.
        
        주요 제품/서비스
        - 고급 기술 제품
        - 엔터프라이즈 솔루션
        - 고객 지원 서비스
        
        미션
        우리는 고객 가치를 창출하는 것을 목표로 합니다.
        """
        
    except Exception as e:
        return f"❌ 오류: {str(e)}"


def search_hiring(company_name: str) -> str:
    """
    회사의 최근 채용공고를 검색합니다 (데모 버전).
    
    Args:
        company_name (str): 회사명
        
    Returns:
        str: 채용공고 정보
    """
    try:
        # 데모 채용공고
        demo_hiring = {
            "LG전자": [
                "AI 반도체 엔지니어 채용 - 10명 모집",
                "소프트웨어 개발자 채용 - 15명 모집",
                "하드웨어 설계 엔지니어 - 8명 모집"
            ],
            "Google": [
                "머신러닝 엔지니어 채용 - 20명",
                "소프트웨어 엔지니어 채용 - 30명",
                "데이터 분석가 채용 - 10명"
            ]
        }
        
        result_text = f"🏢 {company_name} 채용공고 검색 결과:\n\n"
        
        # 회사 찾기
        hiring_list = None
        for key in demo_hiring:
            if key.lower() in company_name.lower() or company_name.lower() in key.lower():
                hiring_list = demo_hiring[key]
                break
        
        if hiring_list:
            for i, job in enumerate(hiring_list, 1):
                result_text += f"{i}. {job}\n"
                result_text += f"   채용 상태: 진행 중\n"
                result_text += f"   주요 자격요건: 해당 분야 경력 3년 이상\n\n"
        else:
            result_text += "1. 기술 직군 채용 중\n"
            result_text += "   채용 상태: 진행 중\n"
            result_text += "   주요 자격요건: 관련 경력 3년 이상\n\n"
        
        return result_text
        
    except Exception as e:
        return f"❌ 오류: 채용공고 검색 실패 - {str(e)}"


# 도구 정의 (OpenAI Function Calling 형식)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "회사 관련 최신 뉴스와 동향을 검색합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색 쿼리"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "특정 URL의 웹페이지 내용을 가져옵니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "웹페이지 URL"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hiring",
            "description": "회사의 최근 채용공고를 검색해 조직 확장 방향을 파악합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "회사명"
                    }
                },
                "required": ["company_name"]
            }
        }
    }
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    도구를 실행하고 결과를 반환합니다.
    
    Args:
        tool_name (str): 도구 이름
        tool_input (dict): 도구 입력값
        
    Returns:
        str: 도구 실행 결과
    """
    if tool_name == "web_search":
        return web_search(tool_input.get("query", ""))
    elif tool_name == "web_fetch":
        return web_fetch(tool_input.get("url", ""))
    elif tool_name == "search_hiring":
        return search_hiring(tool_input.get("company_name", ""))
    else:
        return f"❌ 오류: 알 수 없는 도구 '{tool_name}'"
