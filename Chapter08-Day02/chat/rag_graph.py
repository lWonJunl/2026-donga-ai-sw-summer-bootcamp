from __future__ import annotations

import re
from collections import Counter
from hashlib import sha256
from typing import TypedDict

from django.conf import settings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph


_TOKEN_RE = re.compile(r"[가-힣A-Za-z0-9]{2,}")
_STOPWORDS = {"그리고", "하지만", "대한", "있는", "있습니다", "합니다", "통해", "에서", "으로"}


class PreprocessState(TypedDict, total=False):
    documents: list[Document]
    chunks: list[Document]
    user_id: int
    source_type: str
    display_name: str


def _summary(text: str) -> str:
    sentences = re.split(r"(?<=[.!?。！？])\s+", " ".join(text.split()))
    return " ".join(sentences[:2])[:180] or text[:180]


def _keywords(text: str) -> list[str]:
    counts = Counter(token for token in _TOKEN_RE.findall(text) if token not in _STOPWORDS)
    return [token for token, _ in counts.most_common(8)]


def _split_node(state: PreprocessState):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=getattr(settings, "RAG_CHUNK_SIZE", 600),
        chunk_overlap=getattr(settings, "RAG_CHUNK_OVERLAP", 100),
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return {"chunks": splitter.split_documents([doc for doc in state["documents"] if doc.page_content.strip()])}


def _enrich_node(state: PreprocessState):
    enriched = []
    for chunk in state["chunks"]:
        original = chunk.page_content.strip()
        keywords = _keywords(original)
        summary = _summary(original)
        chunk.metadata.update(
            {
                "summary": summary,
                "keywords": ", ".join(keywords),
                "chunk_chars": len(original),
            }
        )
        chunk.page_content = f"키워드: {', '.join(keywords)}\n요약: {summary}\n\n본문:\n{original}"
        enriched.append(chunk)
    return {"chunks": enriched}


def _tag_node(state: PreprocessState):
    tagged = []
    for chunk in state["chunks"]:
        source = str(chunk.metadata.get("source", state["display_name"]))
        chunk.metadata.update(
            {
                "user_id": str(int(state["user_id"])),
                "source_type": state["source_type"],
                "display_name": state["display_name"][:255],
                "chunk_id": sha256(f"{state['user_id']}\n{source}\n{chunk.page_content}".encode("utf-8")).hexdigest(),
            }
        )
        tagged.append(chunk)
    return {"chunks": tagged}


def _build_graph():
    graph = StateGraph(PreprocessState)
    graph.add_node("split", _split_node)
    graph.add_node("enrich", _enrich_node)
    graph.add_node("tag", _tag_node)
    graph.add_edge(START, "split")
    graph.add_edge("split", "enrich")
    graph.add_edge("enrich", "tag")
    graph.add_edge("tag", END)
    return graph.compile()


_PREPROCESS_GRAPH = _build_graph()


def preprocess_documents(documents, user_id: int, source_type: str, display_name: str):
    result = _PREPROCESS_GRAPH.invoke(
        {"documents": list(documents), "user_id": user_id, "source_type": source_type, "display_name": display_name}
    )
    return result["chunks"]
