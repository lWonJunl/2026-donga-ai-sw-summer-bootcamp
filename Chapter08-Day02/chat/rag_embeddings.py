from functools import lru_cache

from django.conf import settings
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings


class E5Embeddings(Embeddings):
    """Apply multilingual-E5's asymmetric query/passage prefixes."""

    def __init__(self):
        self.base = HuggingFaceEmbeddings(
            model_name=settings.RAG_EMBED_MODEL,
            model_kwargs={
                "device": settings.RAG_EMBED_DEVICE,
                # The model is installed locally during initial setup. Avoid
                # network retries delaying every RAG query when offline.
                "local_files_only": True,
            },
            encode_kwargs={"normalize_embeddings": True},
        )

    def embed_documents(self, texts):
        return self.base.embed_documents([f"passage: {text}" for text in texts])

    def embed_query(self, text):
        return self.base.embed_query(f"query: {text}")


@lru_cache(maxsize=1)
def get_embeddings():
    return E5Embeddings()
