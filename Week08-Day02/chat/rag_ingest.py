from __future__ import annotations

from pathlib import Path

from django.conf import settings

from .models import KnowledgeSource
from .rag_loaders import load_file, load_url
from .rag_graph import preprocess_documents
from .rag_store import get_vector_store
from .rag_urls import normalize_url, url_fingerprint


def _tag_and_split(documents, user_id: int, source_type: str, display_name: str):
    return preprocess_documents(documents, user_id, source_type, display_name)


def ingest_url(user, url: str):
    normalized_url = normalize_url(url)
    fingerprint = url_fingerprint(normalized_url)
    existing = KnowledgeSource.objects.filter(
        user=user,
        source_type="url",
        status="ready",
    ).filter(content_hash=fingerprint).first()
    if not existing:
        # Supports URL rows created before fingerprints were introduced.
        existing = KnowledgeSource.objects.filter(
            user=user,
            source_type="url",
            status="ready",
            source__in=[url, normalized_url],
        ).first()
    if existing:
        if not existing.content_hash:
            existing.content_hash = fingerprint
            existing.source = normalized_url
            existing.display_name = normalized_url
            existing.save(update_fields=["content_hash", "source", "display_name"])
        return existing

    source = KnowledgeSource.objects.create(
        user=user,
        source_type="url",
        source=normalized_url,
        display_name=normalized_url,
        content_hash=fingerprint,
    )
    try:
        chunks = _tag_and_split(
            load_url(normalized_url), user.id, "url", normalized_url
        )
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
    if suffix not in {".pdf", ".pptx", ".docx"}:
        raise ValueError("PDF, PPTX, DOCX 파일만 업로드할 수 있습니다.")
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


def delete_knowledge_source(source: KnowledgeSource):
    """Delete vectors, a safely scoped upload, then the SQLite record."""
    from .rag_store import delete_source_documents

    if source.status == "ready":
        delete_source_documents(source.user_id, source.source)
    elif source.status == "failed":
        # A failed batch can still have partial vectors. Clean them when Milvus
        # is available, but do not make a failed record impossible to remove.
        try:
            delete_source_documents(source.user_id, source.source)
        except Exception:
            pass

    if source.source_type in {"pdf", "pptx", "docx"}:
        upload_root = (Path(settings.RAG_UPLOAD_DIR) / str(source.user_id)).resolve()
        file_path = Path(source.source).resolve()
        if not file_path.is_relative_to(upload_root):
            raise ValueError("안전하지 않은 업로드 파일 경로입니다.")
        if file_path.exists():
            file_path.unlink()
    source.delete()
