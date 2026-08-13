"""multilingual-E5-small을 LangChain Embeddings로 사용하는 예제."""

from __future__ import annotations

import math
import os

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings


EMBED_MODEL = "intfloat/multilingual-e5-small"


class E5Embeddings(Embeddings):
    """질문에는 query:, 문서에는 passage: 접두어를 자동 적용한다."""

    def __init__(self, model_name: str = EMBED_MODEL, device: str = "cpu") -> None:
        self.base = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True},
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        passages = [f"passage: {text}" for text in texts]
        return self.base.embed_documents(passages)

    def embed_query(self, text: str) -> list[float]:
        return self.base.embed_query(f"query: {text}")


def create_embeddings() -> E5Embeddings:
    device = os.getenv("E5_DEVICE", "cpu")
    return E5Embeddings(device=device)


def self_test() -> None:
    embeddings = create_embeddings()
    vector = embeddings.embed_query("RAG란 무엇인가요?")
    norm = math.sqrt(sum(value * value for value in vector))
    print("model:", EMBED_MODEL)
    print("dimension:", len(vector))
    print("L2 norm:", round(norm, 4))


if __name__ == "__main__":
    self_test()
