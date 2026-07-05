"""
tools/chroma_tool.py
=====================
Thin wrapper around ChromaDB providing:
- collection initialization / ingestion of faculty documents
- semantic search returning (Faculty, similarity_score) pairs

Embeddings default to a local Sentence-Transformers model so the whole
system runs fully offline with no API key. If EMBEDDING_PROVIDER=openai
and OPENAI_API_KEY is set, OpenAI embeddings are used instead.
"""

from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from typing import List, Tuple

import chromadb
import numpy as np
from chromadb.utils import embedding_functions

from config import settings
from models.faculty import Faculty
from utils.ingest import load_faculty
from utils.logger import get_logger

logger = get_logger()

_HASH_DIM = 384  # matches all-MiniLM-L6-v2 dimensionality, for drop-in parity


class HashingEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """
    Fully offline, dependency-free embedding function used as a last-resort
    fallback when no network is available to download a sentence-transformers
    or OpenAI embedding model (e.g. an air-gapped or sandboxed environment).

    It is a simple hashed bag-of-words vectorizer: not as semantically rich
    as a real embedding model, but deterministic, fast, and good enough to
    keep semantic search functional (keyword/overlap driven) when nothing
    else is reachable.
    """

    def __call__(self, input: List[str]) -> List[List[float]]:  # noqa: A002 - chromadb's expected signature
        return [self._embed(text) for text in input]

    @staticmethod
    def _embed(text: str) -> List[float]:
        vec = np.zeros(_HASH_DIM, dtype=float)
        tokens = re.findall(r"[a-zA-Z0-9\-]{2,}", text.lower())
        for tok in tokens:
            digest = hashlib.md5(tok.encode("utf-8")).hexdigest()
            idx = int(digest, 16) % _HASH_DIM
            sign = 1.0 if int(digest, 16) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    @staticmethod
    def name() -> str:
        return "hashing-fallback-embedding"


@lru_cache(maxsize=1)
def _get_embedding_function():
    if settings.embedding_provider == "openai" and settings.has_openai:
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name="text-embedding-3-small",
        )
    # Default: local sentence-transformers model, no network/API key needed
    # once the model weights are cached. If it can't be loaded (e.g. no
    # network on first run in an offline environment), fall back to a
    # deterministic hashing embedder so the system never hard-fails.
    try:
        fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )
        fn(["healthcheck"])  # force model load now, not on first real query
        return fn
    except Exception as exc:
        logger.warning(
            "Could not load sentence-transformers model '%s' (%s). "
            "Falling back to offline hashing embeddings.",
            settings.embedding_model,
            exc,
        )
        return HashingEmbeddingFunction()


@lru_cache(maxsize=1)
def _get_client():
    return chromadb.PersistentClient(path=str(settings.chroma_dir))


def get_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=settings.chroma_collection_name,
        embedding_function=_get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def ingest_faculty(force: bool = False) -> int:
    """
    Populate the Chroma collection with every faculty profile.
    Idempotent: skips ingestion if the collection is already populated
    unless force=True (in which case it is rebuilt from scratch).
    """
    collection = get_collection()

    if force:
        existing_ids = collection.get()["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)

    if collection.count() > 0 and not force:
        return collection.count()

    faculty_list = load_faculty()
    documents = [f.to_document_text() for f in faculty_list]
    ids = [f.id for f in faculty_list]
    metadatas = [{"name": f.name, "department": f.department} for f in faculty_list]

    collection.add(documents=documents, ids=ids, metadatas=metadatas)
    return collection.count()


def _faculty_by_id(faculty_id: str) -> Faculty | None:
    for f in load_faculty():
        if f.id == faculty_id:
            return f
    return None


def semantic_search(query: str, top_k: int | None = None) -> List[Tuple[Faculty, float, str]]:
    """
    Returns a list of (Faculty, similarity_score in [0,1], distance-based reason)
    ordered by descending similarity.
    """
    top_k = top_k or settings.top_k_faculty
    collection = get_collection()
    if collection.count() == 0:
        ingest_faculty()
        collection = get_collection()

    results = collection.query(query_texts=[query], n_results=min(top_k, max(collection.count(), 1)))

    out: List[Tuple[Faculty, float, str]] = []
    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for fid, dist in zip(ids, distances):
        faculty = _faculty_by_id(fid)
        if faculty is None:
            continue
        # Chroma cosine distance -> similarity in [0, 1]
        similarity = max(0.0, 1.0 - dist / 2.0)
        reason = (
            f"Strong semantic overlap with '{query}' across research areas "
            f"({', '.join(faculty.research_areas[:2])})."
        )
        out.append((faculty, round(similarity, 4), reason))
    return out


def get_faculty_by_name(name_fragment: str) -> Faculty | None:
    """Fuzzy-ish lookup by (partial, case-insensitive) name match."""
    name_fragment = name_fragment.lower().strip()
    for f in load_faculty():
        if name_fragment in f.name.lower():
            return f
    return None
