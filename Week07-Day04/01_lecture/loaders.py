"""웹·PPTX·DOCX를 LangChain Document 목록으로 통합하는 예제."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path

import bs4
from langchain_community.document_loaders import (
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
)
from langchain_core.documents import Document


DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data"


def _tag(documents: Iterable[Document], source_type: str) -> list[Document]:
    result = list(documents)
    for doc in result:
        source = str(doc.metadata.get("source", ""))
        doc.metadata["source_type"] = source_type
        doc.metadata.setdefault("title", Path(source).name or "제목 없음")
    return result


def load_web(urls: list[str], body_classes: tuple[str, ...] | None = None) -> list[Document]:
    if not urls:
        return []
    kwargs = {}
    if body_classes:
        kwargs["parse_only"] = bs4.SoupStrainer(class_=body_classes)
    loader = WebBaseLoader(
        web_paths=tuple(urls),
        header_template={"User-Agent": "AI02-RAG-Class/1.0"},
        bs_kwargs=kwargs,
    )
    return _tag(loader.load(), "web")


def load_pptx(path: Path) -> list[Document]:
    loader = UnstructuredPowerPointLoader(str(path), mode="elements")
    return _tag(loader.load(), "pptx")


def load_docx(path: Path) -> list[Document]:
    loader = UnstructuredWordDocumentLoader(str(path), mode="elements")
    return _tag(loader.load(), "docx")


def load_all_sources(data_dir: Path = DEFAULT_DATA_DIR, web_urls: list[str] | None = None) -> list[Document]:
    documents = load_web(web_urls or [])
    if data_dir.exists():
        for path in sorted(data_dir.glob("*.pptx")):
            documents.extend(load_pptx(path))
        for path in sorted(data_dir.glob("*.docx")):
            documents.extend(load_docx(path))
    return [doc for doc in documents if doc.page_content.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--url", action="append", default=[])
    args = parser.parse_args()
    documents = load_all_sources(args.data_dir, args.url)
    print("documents:", len(documents))
    for doc in documents[:5]:
        print(doc.metadata.get("source_type"), doc.metadata.get("source"))


if __name__ == "__main__":
    main()
