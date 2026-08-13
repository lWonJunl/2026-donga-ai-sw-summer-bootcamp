from functools import lru_cache
import socket
from urllib.parse import urlparse

from django.conf import settings
from langchain_milvus import Milvus

from .rag_embeddings import get_embeddings


def _ensure_milvus_available():
    parsed = urlparse(settings.RAG_MILVUS_URI)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 19530
    try:
        with socket.create_connection((host, port), timeout=0.35):
            return
    except OSError as error:
        raise ConnectionError("Milvus가 실행 중이 아닙니다.") from error


@lru_cache(maxsize=1)
def get_vector_store():
    # Avoid loading the embedding model (and attempting network downloads) when
    # the local vector database is not running.
    _ensure_milvus_available()
    return Milvus(
        embedding_function=get_embeddings(),
        connection_args={"uri": settings.RAG_MILVUS_URI},
        collection_name=settings.RAG_MILVUS_COLLECTION,
        partition_key_field="user_id",
        index_params={"metric_type": "COSINE"},
        enable_dynamic_field=True,
        auto_id=True,
        drop_old=False,
    )


def search_user_documents(user_id: int, question: str):
    normalized_user_id = str(int(user_id))
    return get_vector_store().similarity_search(
        question,
        k=settings.RAG_TOP_K,
        expr=f'user_id == "{normalized_user_id}"',
    )
