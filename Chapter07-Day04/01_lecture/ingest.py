"""문서를 청킹하고 multilingual-E5 벡터를 Milvus에 저장하는 예제."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from langchain_core.documents import Document
from langchain_milvus import Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ai02_embeddings import create_embeddings
from ai02_loaders import DEFAULT_DATA_DIR, load_all_sources


MILVUS_URI = "http://127.0.0.1:19530"
COLLECTION_NAME = "ai02_korean_docs"


def split_and_tag(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for chunk in chunks:
        source = str(chunk.metadata.get("source", "unknown"))
        raw = f"{source}\n{chunk.page_content}".encode("utf-8")
        chunk.metadata["chunk_id"] = hashlib.sha256(raw).hexdigest()
    return chunks


def create_vector_store(drop_old: bool = False) -> Milvus:
    return Milvus(
        embedding_function=create_embeddings(),
        connection_args={"uri": MILVUS_URI},
        collection_name=COLLECTION_NAME,
        index_params={"metric_type": "COSINE"},
        auto_id=True,
        drop_old=drop_old,
    )


def ingest(data_dir: Path, web_urls: list[str], drop_old: bool = False) -> int:
    documents = load_all_sources(data_dir, web_urls)
    if not documents:
        raise RuntimeError("수집된 문서가 없습니다. data 폴더 또는 --url을 확인하세요.")
    chunks = split_and_tag(documents)
    ids = create_vector_store(drop_old=drop_old).add_documents(chunks)
    print(f"documents: {len(documents)}")
    print(f"indexed: {len(ids)}")
    return len(ids)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--drop-old", action="store_true")
    args = parser.parse_args()
    ingest(args.data_dir, args.url, args.drop_old)


if __name__ == "__main__":
    main()
