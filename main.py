"""
B2B Account Intelligence Agent — Gradio UI
실행: python main.py  →  http://localhost:7860
"""
import os
import gradio as gr
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()


def check_env() -> str | None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "❌ .env 파일에 ANTHROPIC_API_KEY를 설정해주세요."
    if not os.getenv("TAVILY_API_KEY"):
        return "❌ .env 파일에 TAVILY_API_KEY를 설정해주세요."
    return None


def generate_briefing(company_name: str):
    company_name = company_name.strip()
    if not company_name:
        yield "⚠️ 회사명을 입력해주세요."
        return

    err = check_env()
    if err:
        yield err
        return

    yield f"⏳ **{company_name}** 정보 수집 중...\n\nClaude가 웹 검색·채용공고·뉴스를 자율적으로 수집합니다."

    try:
        report = run_agent(company_name)

        # 마크다운 파일로도 저장
        filename = f"briefing_{company_name}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        yield report + f"\n\n---\n📄 `{filename}` 저장 완료"

    except Exception as e:
        yield f"❌ 오류 발생: {e}\n\nAPI 키와 네트워크 연결을 확인해주세요."


with gr.Blocks(title="B2B Account Intelligence Agent") as demo:
    gr.Markdown("""
# 🎯 B2B Account Intelligence Agent
**회사명 하나 입력 → 영업 브리핑 문서 자동 생성**

Claude Sonnet이 웹 검색·채용공고·뉴스를 자율적으로 수집·분석합니다.
    """)

    with gr.Row():
        company_input = gr.Textbox(
            placeholder="예: 카카오 / 현대자동차 / LG화학 ...",
            label="고객사 회사명",
            scale=5,
        )
        submit_btn = gr.Button("브리핑 생성 🚀", variant="primary", scale=1)

    output = gr.Markdown(
        label="영업 브리핑 문서",
        value="회사명을 입력하고 **브리핑 생성** 버튼을 클릭하세요.",
    )

    submit_btn.click(fn=generate_briefing, inputs=company_input, outputs=output)
    company_input.submit(fn=generate_briefing, inputs=company_input, outputs=output)

    gr.Markdown("""
---
> ℹ️ Claude Sonnet 4.5 + Tavily Search | Anthropic SDK 기반 단일 에이전트 루프
    """)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, theme=gr.themes.Soft())
