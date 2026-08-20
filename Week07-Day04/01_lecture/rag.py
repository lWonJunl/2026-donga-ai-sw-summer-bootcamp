"""Milvus 검색 결과를 로컬 EXAONE에 전달하는 CLI RAG 예제."""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from ai02_ingest import create_vector_store


LLM_MODEL = "exaone3.5:7.8b"

PROMPT = ChatPromptTemplate.from_template(
    """당신은 한국어 문서 검색 도우미입니다.
아래 context만 사용해 답하세요.
근거가 없으면 '문서에서 확인할 수 없습니다'라고 답하세요.

context:
{context}

question: {question}
"""
)


def format_docs(documents) -> str:
    """Milvus가 찾은 Top-k Document를 EXAONE이 읽을 문자열로 바꾼다."""
    return "\n\n".join(
        f"[{index}] {doc.page_content}" for index, doc in enumerate(documents, 1)
    )


def build_runtime(top_k: int = 4):
    vector_store = create_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )
    llm = ChatOllama(
        model=LLM_MODEL,
        temperature=0.1,
        num_ctx=4096,
        num_predict=384,
        keep_alive="30m",
    )
    chain = PROMPT | llm | StrOutputParser()
    return retriever, chain


def ask(question: str, retriever, chain) -> tuple[str, list[dict]]:
    # E5 질문 벡터로 Milvus를 검색하지만 EXAONE에는 벡터를 보내지 않는다.
    documents = retriever.invoke(question)
    # 검색된 page_content와 원문 질문을 프롬프트 문자열로 전달한다.
    answer = chain.invoke(
        {"context": format_docs(documents), "question": question}
    )
    sources = []
    for doc in documents:
        metadata = doc.metadata
        sources.append(
            {
                "source": metadata.get("source"),
                "page": metadata.get("page_number", metadata.get("page")),
                "source_type": metadata.get("source_type"),
            }
        )
    return answer, sources


def main() -> None:
    retriever, chain = build_runtime()
    print("종료하려면 exit를 입력하세요.")
    while True:
        question = input("\n질문> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        answer, sources = ask(question, retriever, chain)
        print("\n답변:", answer)
        print("출처:")
        for source in sources:
            print("-", source)


if __name__ == "__main__":
    main()
