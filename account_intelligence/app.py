"""
B2B Account Intelligence Agent — Gradio UI (카드 박스 + 키워드 필터)
실행: python app.py  →  http://localhost:7860
"""
import sys, os, re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
from agent import run_agent, save_report

load_dotenv()

# ── 섹션 아이콘 ───────────────────────────────────────────────────────────────
SECTION_ICONS = {
    "기업 스냅샷": "🏢", "최근 동향": "📰", "조직": "👥",
    "경쟁사": "⚔️", "페인포인트": "🎯", "의사결정자": "👤",
    "구매 신호": "⏰", "영업 전략": "💡", "미팅 시나리오": "🗓️", "체크리스트": "✅",
}
FULL_WIDTH = {"기업 스냅샷", "미팅 시나리오", "체크리스트", "영업 전략", "페인포인트"}

def get_icon(title: str) -> str:
    for key, icon in SECTION_ICONS.items():
        if key in title:
            return icon
    return "📌"

# ── 마크다운 → HTML ───────────────────────────────────────────────────────────
def inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r'<strong style="color:#374151;font-weight:600;">\1</strong>', text)
    text = re.sub(r"\*(.+?)\*",     r'<em>\1</em>', text)
    text = re.sub(r"`(.+?)`",       r'<code style="background:#f3f4f6;padding:1px 5px;border-radius:3px;font-size:12.5px;">\1</code>', text)
    text = text.replace("🔴", '<span style="color:#e53935;">🔴</span>')
    text = text.replace("🟡", '<span style="color:#f9a825;">🟡</span>')
    text = text.replace("🟢", '<span style="color:#43a047;">🟢</span>')
    return text

def md_to_html(text: str) -> str:
    lines = text.strip().split("\n")
    html, in_ul, in_table = [], False, False

    def close_ul():
        nonlocal in_ul
        if in_ul: html.append("</ul>"); in_ul = False

    def close_table():
        nonlocal in_table
        if in_table: html.append("</tbody></table>"); in_table = False

    for line in lines:
        if line.strip().startswith("|") and "|" in line[1:]:
            if "---" in line: continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                close_ul()
                html.append('<table style="width:100%;border-collapse:collapse;margin:8px 0;font-size:13.5px;"><tbody>')
                in_table = True
                row = "".join(f'<th style="background:#f9fafb;border:1px solid #e5e7eb;padding:8px 12px;text-align:left;font-weight:600;color:#374151;">{c}</th>' for c in cells)
            else:
                row = "".join(f'<td style="border:1px solid #e5e7eb;padding:8px 12px;color:#4b5563;">{inline(c)}</td>' for c in cells)
            html.append(f"<tr>{row}</tr>"); continue
        close_table()

        if re.match(r"^- \[[ x]\]", line):
            close_ul()
            checked = "x" in line[3:5]
            html.append(f'<div style="padding:3px 0;font-size:14px;color:#374151;">{"✅" if checked else "⬜"} {inline(line[6:].strip())}</div>')
            continue
        if re.match(r"^[-*] ", line):
            if not in_ul: html.append('<ul style="margin:6px 0 6px 18px;padding:0;">'); in_ul = True
            html.append(f'<li style="margin:4px 0;color:#4b5563;font-size:14px;line-height:1.7;">{inline(line[2:].strip())}</li>')
            continue
        close_ul()

        if line.startswith("### "):
            html.append(f'<h3 style="font-size:13.5px;font-weight:700;color:#374151;margin:12px 0 5px;border-bottom:1px solid #f3f4f6;padding-bottom:3px;">{inline(line[4:])}</h3>')
        elif line.startswith("> "):
            html.append(f'<blockquote style="margin:8px 0;padding:10px 14px;background:#f9fafb;border-left:3px solid #d1d5db;color:#6b7280;font-size:13.5px;border-radius:0 6px 6px 0;">{inline(line[2:])}</blockquote>')
        elif line.strip() in ("", "---"):
            html.append('<div style="margin:4px 0;"></div>')
        else:
            html.append(f'<p style="margin:4px 0;color:#4b5563;font-size:14px;line-height:1.7;">{inline(line)}</p>')

    close_ul(); close_table()
    return "\n".join(html)

# ── 보고서 → 카드 HTML ────────────────────────────────────────────────────────
def render_report(report: str, company: str, generated_at: str, filepath: str) -> str:
    parts = re.split(r"\n## ", report)
    title_match = re.search(r"#\s+(.+)", parts[0])
    title = title_match.group(1) if title_match else f"{company} 영업 브리핑"
    sections = parts[1:]

    html = f"""
<div style="font-family:'Noto Sans KR','Segoe UI',sans-serif;max-width:1100px;margin:0 auto;">
  <div style="padding:8px 4px 20px;">
    <div style="font-size:11px;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">Sales Briefing Report</div>
    <div style="font-size:24px;font-weight:700;color:#111827;letter-spacing:-0.5px;margin-bottom:8px;">{title}</div>
    <div style="display:flex;gap:16px;flex-wrap:wrap;">
      <span style="font-size:13px;color:#6b7280;">📅 {generated_at}</span>
      <span style="font-size:13px;color:#6b7280;">🤖 GPT-4o 자동 생성</span>
      <span style="font-size:13px;color:#6b7280;">📄 {filepath}</span>
    </div>
    <div style="margin-top:14px;border-bottom:2px solid #e5e7eb;"></div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
"""
    for section in sections:
        lines = section.strip().split("\n")
        sec_title = lines[0].strip()
        sec_body  = "\n".join(lines[1:]).strip()
        icon      = get_icon(sec_title)
        col_span  = 'grid-column:1/-1;' if any(k in sec_title for k in FULL_WIDTH) else ''

        html += f"""
    <div style="{col_span}background:#fff;border-radius:12px;overflow:hidden;
                 box-shadow:0 1px 6px rgba(0,0,0,0.07);border:1px solid #e5e7eb;">
      <div style="background:#f8fafc;border-left:4px solid #4f6ef7;padding:12px 18px;display:flex;align-items:center;gap:8px;">
        <span style="font-size:18px;">{icon}</span>
        <span style="font-size:14px;font-weight:700;color:#374151;">{sec_title}</span>
      </div>
      <div style="padding:16px 20px 18px;">{md_to_html(sec_body)}</div>
    </div>"""

    html += """
  </div>
  <div style="text-align:center;color:#d1d5db;font-size:12px;padding:24px 0 8px;">
    본 보고서는 공개 정보 기반 AI 분석 결과입니다. 미팅 전 최신 정보를 추가 확인하세요.
  </div>
</div>"""
    return html

# ── 키워드 필터 결과 → 카드 HTML ──────────────────────────────────────────────
def render_keyword_result(content: str, keyword: str, company: str) -> str:
    parts = re.split(r"\n## ", content)
    sections = parts[1:] if len(parts) > 1 else []

    html = f"""
<div style="font-family:'Noto Sans KR','Segoe UI',sans-serif;max-width:1100px;margin:0 auto;">
  <div style="padding:8px 4px 20px;">
    <div style="font-size:11px;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">Keyword Focus Analysis</div>
    <div style="font-size:22px;font-weight:700;color:#111827;margin-bottom:6px;">
      {company} × <span style="color:#4f6ef7;">"{keyword}"</span> 집중 분석
    </div>
    <div style="margin-top:12px;border-bottom:2px solid #e5e7eb;"></div>
  </div>
"""
    if sections:
        # 아이콘 목록 (순서대로)
        icons = ["🔍", "🎯", "💡", "❓", "⚡"]
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">'
        for i, section in enumerate(sections):
            lines = section.strip().split("\n")
            sec_title = lines[0].strip()
            sec_body  = "\n".join(lines[1:]).strip()
            icon      = icons[i % len(icons)]
            col_span  = 'grid-column:1/-1;' if i == 0 else ''
            html += f"""
      <div style="{col_span}background:#fff;border-radius:12px;overflow:hidden;
                   box-shadow:0 1px 6px rgba(0,0,0,0.07);border:1px solid #e5e7eb;">
        <div style="background:#f0f4ff;border-left:4px solid #4f6ef7;padding:12px 18px;display:flex;align-items:center;gap:8px;">
          <span style="font-size:18px;">{icon}</span>
          <span style="font-size:14px;font-weight:700;color:#374151;">{sec_title}</span>
        </div>
        <div style="padding:16px 20px 18px;">{md_to_html(sec_body)}</div>
      </div>"""
        html += '</div>'
    else:
        html += f'<div style="padding:16px 20px;">{md_to_html(content)}</div>'

    html += "</div>"
    return html

# ── Gradio 함수 ───────────────────────────────────────────────────────────────
LOADING = lambda c, t="분석": f"""
<div style="text-align:center;padding:60px 20px;font-family:'Noto Sans KR',sans-serif;">
  <div style="font-size:36px;margin-bottom:14px;">⚙️</div>
  <div style="font-size:18px;font-weight:700;color:#111827;margin-bottom:6px;">{c} {t} 중...</div>
  <div style="font-size:13px;color:#6b7280;">잠시만 기다려주세요</div>
</div>"""

def generate_briefing(company_name: str):
    company_name = company_name.strip()
    if not company_name:
        yield "<p>⚠️ 회사명을 입력해주세요.</p>", ""
        return
    if not os.getenv("OPENAI_API_KEY"):
        yield "<p>❌ OPENAI_API_KEY를 설정해주세요.</p>", ""
        return

    yield LOADING(company_name), ""

    try:
        report   = run_agent(company_name)
        filepath = save_report(company_name, report)
        now      = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        yield render_report(report, company_name, now, filepath), report
    except Exception as e:
        yield f"<p style='color:red;'>❌ 오류: {e}</p>", ""


def filter_by_keyword(raw_report: str, keyword: str, company_name: str):
    if not raw_report:
        yield "<p style='color:#6b7280;text-align:center;padding:24px;'>⚠️ 먼저 회사 브리핑을 생성해주세요.</p>"
        return
    if not keyword.strip():
        yield "<p style='color:#6b7280;text-align:center;padding:24px;'>⚠️ 관심 키워드를 입력해주세요.</p>"
        return

    kw = keyword.strip()
    yield LOADING(f'"{kw}"', "키워드 검색 중")

    try:
        client = OpenAI()

        # ── Step 1: 키워드 × 기업 추가 웹 검색 (2개 쿼리 병렬) ──────────────
        search_results = []
        for query in [
            f"{company_name} {kw} 최신 뉴스 동향 2025",
            f"{company_name} {kw} 전략 투자 계획 사례",
        ]:
            resp = client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=query,
            )
            search_results.append(f"[검색: {query}]\n{resp.output_text}")

        fresh_data = "\n\n".join(search_results)

        # ── Step 2: 실제 수집 데이터 기반 분석 (할루시네이션 방지) ───────────
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=3000,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 B2B 영업 전문가입니다.\n"
                        "아래 규칙을 반드시 지키세요:\n"
                        "1. 반드시 제공된 [실시간 검색 결과]와 [기존 브리핑] 안에 있는 사실만 사용하세요.\n"
                        "2. 검색 결과에 없는 내용은 절대 추측하거나 지어내지 마세요.\n"
                        "3. 근거가 불충분한 항목은 '확인된 정보 없음'으로 명시하세요.\n"
                        "4. 인용할 때는 출처(뉴스 제목 또는 검색 키워드)를 괄호로 표기하세요."
                    ),
                },
                {
                    "role": "user",
                    "content": f"""아래 두 자료를 바탕으로 {company_name}의 **"{kw}"** 관련 분석을 작성해주세요.
자료에 없는 내용은 추가하지 마세요.

===== 실시간 검색 결과 =====
{fresh_data}

===== 기존 브리핑 리포트 =====
{raw_report}

---

위 자료에 근거해서 아래 항목을 ## 섹션으로 작성하세요.

## 핵심 인사이트
수집된 자료에서 확인된 "{kw}" 관련 사실 3~5가지 (각 항목에 출처 명시)

## 페인포인트 & 기회
자료에서 확인된 문제점과 우리가 제공할 수 있는 기회 (근거 포함)

## 영업 접근 전략
수집된 정보를 기반으로 한 구체적 영업 메시지 (추측 없이 사실 기반으로)

## 추천 질문
"{kw}" 주제로 미팅에서 활용할 질문 3~4개

## 주의사항
자료에서 확인된 민감한 이슈나 리스크 (없으면 '확인된 정보 없음' 표기)""",
                },
            ],
        )
        result = response.choices[0].message.content
        yield render_keyword_result(result, kw, company_name)

    except Exception as e:
        yield f"<p style='color:red;'>❌ 오류: {e}</p>"


# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
.gradio-container { background:#f3f4f6 !important; }
#submit-btn {
    background:linear-gradient(135deg,#4f6ef7,#6366f1) !important;
    color:#fff !important; border:none !important;
    border-radius:10px !important; font-weight:600 !important;
    font-size:15px !important; height:50px !important;
}
#filter-btn {
    background:#111827 !important; color:#fff !important;
    border:none !important; border-radius:10px !important;
    font-weight:600 !important; font-size:14px !important;
    height:46px !important;
}
#keyword-input textarea {
    border-radius:10px !important; border:1.5px solid #e5e7eb !important;
    font-size:14px !important;
}
"""

# ── UI ────────────────────────────────────────────────────────────────────────
with gr.Blocks(title="B2B Account Intelligence", css=CSS) as demo:

    report_state   = gr.State("")   # 원본 리포트 텍스트 저장
    company_state  = gr.State("")   # 회사명 저장

    # 상단 타이틀
    gr.HTML("""
    <div style="padding:24px 4px 16px;border-bottom:1px solid #e5e7eb;margin-bottom:16px;">
      <div style="font-size:11px;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">B2B Sales Intelligence</div>
      <div style="font-size:22px;font-weight:700;color:#111827;">Account Intelligence Agent</div>
      <div style="font-size:13px;color:#6b7280;margin-top:4px;">
        회사명 입력 → 뉴스 · 채용 · 경쟁사 · 재무 자동 수집 → 영업 인사이트 브리핑 자동 생성
      </div>
    </div>
    """)

    # 회사명 입력
    with gr.Group(elem_id="input-row",
                  visible=True):
        with gr.Row():
            company_input = gr.Textbox(
                placeholder="분석할 회사명 입력  (예: 카카오, 삼성전자, 현대자동차 ...)",
                show_label=False, container=False, scale=5,
            )
            submit_btn = gr.Button("브리핑 생성 🚀", variant="primary", scale=1, elem_id="submit-btn")

    # 보고서 출력
    report_output = gr.HTML(
        value="""<div style="text-align:center;padding:60px;color:#9ca3af;font-family:'Noto Sans KR',sans-serif;">
          <div style="font-size:36px;margin-bottom:12px;">📋</div>
          <div style="font-size:15px;font-weight:600;color:#6b7280;">회사명을 입력하고 브리핑 생성을 클릭하세요</div>
        </div>""",
    )

    gr.HTML('<div style="border-top:1px solid #e5e7eb;margin:24px 0 20px;"></div>')

    # 키워드 필터 영역
    gr.HTML("""
    <div style="margin-bottom:12px;">
      <div style="font-size:15px;font-weight:700;color:#111827;margin-bottom:4px;">🔎 관심 키워드로 심층 분석</div>
      <div style="font-size:13px;color:#6b7280;">브리핑 생성 후, 관심 있는 키워드를 입력하면 관련 인사이트만 추출해 보여드립니다.</div>
    </div>
    """)

    with gr.Row():
        keyword_input = gr.Textbox(
            placeholder="예: AI 전환, 클라우드, 비용 절감, 조직 확장, ESG ...",
            show_label=False, container=False, scale=5,
            elem_id="keyword-input",
        )
        filter_btn = gr.Button("키워드 분석 🔍", scale=1, elem_id="filter-btn")

    # 키워드 필터 결과
    keyword_output = gr.HTML(value="")

    # ── 이벤트 연결 ──
    submit_btn.click(
        fn=generate_briefing,
        inputs=company_input,
        outputs=[report_output, report_state],
    ).then(
        fn=lambda c: c,
        inputs=company_input,
        outputs=company_state,
    )
    company_input.submit(
        fn=generate_briefing,
        inputs=company_input,
        outputs=[report_output, report_state],
    ).then(
        fn=lambda c: c,
        inputs=company_input,
        outputs=company_state,
    )

    filter_btn.click(
        fn=filter_by_keyword,
        inputs=[report_state, keyword_input, company_state],
        outputs=keyword_output,
    )
    keyword_input.submit(
        fn=filter_by_keyword,
        inputs=[report_state, keyword_input, company_state],
        outputs=keyword_output,
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
