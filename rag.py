import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import gradio as gr

load_dotenv()

PDF_PATH = "data/pdf/file1.pdf"
VECTORSTORE_PATH = "vectorstore/file1_faiss"

PROMPT_TEMPLATE = """주어진 문서 내용을 바탕으로 질문에 답변해 주세요.
문서에 없는 내용은 "문서에서 해당 정보를 찾을 수 없습니다."라고 답변하세요.

문서 내용:
{context}

질문: {question}

답변:"""


def build_vectorstore():
    print("PDF 로딩 중...")
    loader = PyMuPDFLoader(PDF_PATH)
    docs = loader.load()
    print(f"총 {len(docs)} 페이지 로드 완료")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"총 {len(chunks)} 청크로 분할 완료")

    embeddings = OpenAIEmbeddings(model=os.getenv("EMB_MODEL_NAME", "text-embedding-3-small"))
    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs("vectorstore", exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"벡터 스토어 저장 완료: {VECTORSTORE_PATH}")
    return vectorstore


def load_vectorstore():
    embeddings = OpenAIEmbeddings(model=os.getenv("EMB_MODEL_NAME", "text-embedding-3-small"))
    return FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# 벡터 스토어 초기화
if os.path.exists(VECTORSTORE_PATH):
    print("저장된 벡터 스토어를 로드합니다...")
    vectorstore = load_vectorstore()
else:
    vectorstore = build_vectorstore()

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"), temperature=0)
prompt = PromptTemplate(input_variables=["context", "question"], template=PROMPT_TEMPLATE)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


def answer(question: str, history: list):
    if not question.strip():
        return "", history

    source_docs = retriever.invoke(question)
    answer_text = chain.invoke(question)

    sources = set()
    for doc in source_docs:
        page = doc.metadata.get("page", None)
        if page is not None:
            sources.add(f"p.{page + 1}")

    if sources:
        answer_text += f"\n\n📄 출처: {', '.join(sorted(sources))}"

    history.append((question, answer_text))
    return "", history


with gr.Blocks(title="RAG - file1.pdf") as demo:
    gr.Markdown("## RAG 챗봇 — file1.pdf")
    chatbot = gr.Chatbot(height=500)
    with gr.Row():
        msg = gr.Textbox(
            placeholder="질문을 입력하세요...",
            show_label=False,
            scale=9,
        )
        send = gr.Button("전송", scale=1)

    send.click(answer, inputs=[msg, chatbot], outputs=[msg, chatbot])
    msg.submit(answer, inputs=[msg, chatbot], outputs=[msg, chatbot])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
