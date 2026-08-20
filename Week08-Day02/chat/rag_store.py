from functools import lru_cache
import json
import re
import socket
from urllib.parse import urlparse

from django.conf import settings
from langchain_milvus import Milvus
from pymilvus import MilvusClient, connections

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
    # langchain-milvus 0.2 uses PyMilvus's ORM APIs for collection operations,
    # while its internal MilvusClient connection is not registered there.
    # Register the matching alias once so both APIs share the same connection.
    client = MilvusClient(uri=settings.RAG_MILVUS_URI)
    connections.connect(alias=client._using, uri=settings.RAG_MILVUS_URI)
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
    candidates = get_vector_store().similarity_search(
        question,
        # Retrieve a wider semantic candidate set, then prefer FAQ entries
        # that also share the user's concrete terms.
        k=max(settings.RAG_TOP_K * 3, 48),
        expr=f'user_id == "{normalized_user_id}"',
    )
    keywords = set(re.findall(r"[가-힣A-Za-z0-9]{2,}", question))

    def lexical_score(document):
        content = document.page_content.casefold()
        metadata_keywords = str(document.metadata.get("keywords", "")).casefold()
        return sum(keyword.casefold() in content for keyword in keywords) + 2 * sum(
            keyword.casefold() in metadata_keywords for keyword in keywords
        )

    candidates.sort(key=lexical_score, reverse=True)
    return candidates[: settings.RAG_TOP_K]


def delete_source_documents(user_id: int, source: str):
    normalized_user_id = str(int(user_id))
    user_literal = json.dumps(normalized_user_id, ensure_ascii=False)
    source_literal = json.dumps(str(source), ensure_ascii=False)
    vector_store = get_vector_store()
    deleted = vector_store.delete(
        expr=f"user_id == {user_literal} and source == {source_literal}"
    )
    if deleted:
        return

    # A recreated or cleared Milvus volume can leave SQLite source records
    # behind while the collection (and therefore all of its vectors) is gone.
    # In that case there is nothing left to delete in Milvus, so allow the
    # caller to remove the stale source record and any uploaded original.
    if not vector_store.client.has_collection(settings.RAG_MILVUS_COLLECTION):
        return

    if not deleted:
        raise RuntimeError("Milvus에서 자료 벡터를 삭제하지 못했습니다.")
