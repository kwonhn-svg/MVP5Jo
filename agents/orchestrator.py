import asyncio
from .news_agent import run_news_agent
from .hiring_agent import run_hiring_agent
from .web_agent import run_web_agent
from .analyst_agent import run_analyst_agent
from .report_writer import run_report_writer


async def run_orchestrator(company_name: str) -> str:
    """
    1단계: 뉴스·채용·웹 에이전트 병렬 실행
    2단계: 분석 에이전트
    3단계: 리포트 작성 에이전트
    """
    # Step 1 — 3개 서브 에이전트 병렬 실행
    news_task = run_news_agent(company_name)
    hiring_task = run_hiring_agent(company_name)
    web_task = run_web_agent(company_name)

    news_summary, hiring_summary, web_summary = await asyncio.gather(
        news_task, hiring_task, web_task
    )

    # Step 2 — 분석 에이전트
    analyst_summary = await run_analyst_agent(
        company_name, news_summary, hiring_summary, web_summary
    )

    # Step 3 — 리포트 작성
    report = await run_report_writer(
        company_name, news_summary, hiring_summary, web_summary, analyst_summary
    )

    return report
