"""
B2B Account Intelligence 에이전트용 도구 정의
3개의 도구: web_search, web_fetch, search_hiring
OpenAI Responses API (web_search_preview) 기반 실제 검색
"""

import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


def web_search(query: str) -> str:
    """
    회사 관련 최신 뉴스와 동향을 검색합니다.
    OpenAI Responses API + web_search_preview 사용

    Args:
        query (str): 검색 쿼리

    Returns:
        str: 검색 결과 문자열
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search_preview"}],
            input=query,
        )
        return response.output_text
    except Exception as e:
        return f"❌ 검색 실패: {e}"


def web_fetch(url: str) -> str:
    """
    특정 URL의 웹페이지 본문을 가져옵니다.
    requests + BeautifulSoup으로 직접 크롤링

    Args:
        url (str): 웹페이지 URL

    Returns:
        str: 정제된 웹페이지 텍스트
    """
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SalesAgent/1.0)"},
        )
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:4000] if len(text) > 4000 else text
    except Exception as e:
        return f"❌ 페이지 로드 실패: {e}"


def search_hiring(company_name: str) -> str:
    """
    회사의 최근 채용공고를 검색합니다.
    OpenAI Responses API + web_search_preview 사용
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search_preview"}],
            input=f"{company_name} 채용공고 2025 최근 모집 직군",
        )
        return response.output_text
    except Exception as e:
        return f"❌ 채용공고 검색 실패: {e}"


def search_competitors(company_name: str) -> str:
    """
    경쟁사 현황 및 시장 포지셔닝을 검색합니다.
    OpenAI Responses API + web_search_preview 사용
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search_preview"}],
            input=f"{company_name} 경쟁사 비교 시장점유율 포지셔닝 2025",
        )
        return response.output_text
    except Exception as e:
        return f"❌ 경쟁사 검색 실패: {e}"


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
    },
    {
        "type": "function",
        "function": {
            "name": "search_competitors",
            "description": "회사의 주요 경쟁사와 시장 포지셔닝을 검색합니다. 경쟁 압박과 차별화 포인트 파악에 사용하세요.",
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
    elif tool_name == "search_competitors":
        return search_competitors(tool_input.get("company_name", ""))
    else:
        return f"❌ 오류: 알 수 없는 도구 '{tool_name}'"
