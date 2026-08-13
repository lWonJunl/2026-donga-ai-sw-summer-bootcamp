from __future__ import annotations

import hashlib
from pathlib import Path

from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .models import KnowledgeSource
from .rag_loaders import load_file, load_url
from .rag_store import get_vector_store


def _tag_and_split(documents, user_id: int, source_type: str, display_name: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents([doc for doc in documents if doc.page_content.strip()])
    for chunk in chunks:
        source = str(chunk.metadata.get("source", display_name))
        chunk.metadata.update(
            {
                # LangChain Milvus creates partition keys as VARCHAR fields.
                # Normalize through int first so only a server-derived numeric ID is stored.
                "user_id": str(int(user_id)),
                "source_type": source_type,
                "display_name": display_name[:255],
                "chunk_id": hashlib.sha256(
                    f"{user_id}\n{source}\n{chunk.page_content}".encode("utf-8")
                ).hexdigest(),
            }
        )
    return chunks


def ingest_url(user, url: str):
    source = KnowledgeSource.objects.create(user=user, source_type="url", source=url, display_name=url)
    try:
        chunks = _tag_and_split(load_url(url), user.id, "url", url)
        if not chunks:
            raise ValueError("색인할 본문이 없습니다.")
        get_vector_store().add_documents(chunks)
        source.chunk_count = len(chunks)
        source.status = "ready"
    except Exception as error:
        source.status = "failed"
        source.error = str(error)[:1000]
        source.save(update_fields=["status", "error"])
        raise
    source.save(update_fields=["chunk_count", "status"])
    return source


def ingest_uploaded_file(user, uploaded):
    safe_name = Path(uploaded.name).name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in {".pptx", ".docx"}:
        raise ValueError("PPTX와 DOCX 파일만 업로드할 수 있습니다.")
    if uploaded.size > settings.RAG_MAX_UPLOAD_BYTES:
        raise ValueError("업로드 파일은 20MB 이하여야 합니다.")
    user_dir = Path(settings.RAG_UPLOAD_DIR) / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    # Store by digest so two files with the same name cannot overwrite each other.
    temporary_path = user_dir / f"uploading-{safe_name}"
    with temporary_path.open("wb") as output:
        for chunk in uploaded.chunks():
            digest.update(chunk)
            output.write(chunk)
    path = user_dir / f"{digest.hexdigest()}{suffix}"
    temporary_path.replace(path)
    source = KnowledgeSource.objects.create(
        user=user,
        source_type=suffix.lstrip("."),
        source=str(path),
        display_name=safe_name,
        content_hash=digest.hexdigest(),
    )
    try:
        chunks = _tag_and_split(load_file(path), user.id, source.source_type, safe_name)
        if not chunks:
            raise ValueError("색인할 본문이 없습니다.")
        get_vector_store().add_documents(chunks)
        source.chunk_count = len(chunks)
        source.status = "ready"
    except Exception as error:
        source.status = "failed"
        source.error = str(error)[:1000]
        source.save(update_fields=["status", "error"])
        raise
    source.save(update_fields=["chunk_count", "status"])
    return source
