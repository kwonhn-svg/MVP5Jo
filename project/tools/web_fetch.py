import requests
from bs4 import BeautifulSoup


def web_fetch(url: str, timeout: int = 10) -> str:
    """URL의 본문 텍스트를 추출하여 반환"""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AccountIntelBot/1.0)"}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 불필요한 태그 제거
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # 연속 빈 줄 정리 후 최대 3000자 반환
        lines = [l for l in text.splitlines() if l.strip()]
        return "\n".join(lines)[:3000]
    except Exception as e:
        return f"[ERROR] {url} 가져오기 실패: {e}"
