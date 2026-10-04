import os
import re
import hashlib
from datetime import datetime

import pymupdf
import faiss
import numpy as np

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


# ============================================================
# MODELS
# ============================================================

embedding_model = SentenceTransformer(EMBEDDING_MODEL)
reranker = CrossEncoder(RERANKER_MODEL)


# ============================================================
# OPENAI
# ============================================================

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


# ============================================================
# STORAGE
# ============================================================

documents = []
chunks = []

faiss_index = None
bm25_index = None

# Only active chunks are placed into the search indexes.
indexed_chunks = []


# ============================================================
# FILE HASH
# ============================================================

def calculate_file_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf(file_bytes, filename):

    doc = pymupdf.open(
        stream=file_bytes,
        filetype="pdf"
    )

    pages = []

    for page_number, page in enumerate(doc):

        text = page.get_text("text")

        # Keep paragraph breaks
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        if text:
            pages.append({
                "text": text,
                "page": page_number + 1,
                "document": filename
            })

    doc.close()

    return pages


# ============================================================
# FIXED CHUNKING
# ============================================================

def fixed_chunking(
    text,
    chunk_size=800,
    overlap=150
):

    words = text.split()

    result = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk.strip():
            result.append(chunk)

        start += chunk_size - overlap

    return result


# ============================================================
# PARAGRAPH / SENTENCE CHUNKING
# ============================================================

def paragraph_chunking(
    text,
    max_words=800
):

    paragraphs = re.split(
        r"\n\s*\n+|(?<=[.!?])\s+(?=[A-Z0-9])",
        text
    )

    result = []

    current = []
    current_words = 0

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        words = paragraph.split()

        # If a single paragraph is too large,
        # split it using fixed chunking.
        if len(words) > max_words:

            if current:
                result.append(" ".join(current))
                current = []
                current_words = 0

            result.extend(
                fixed_chunking(
                    paragraph,
                    chunk_size=max_words,
                    overlap=100
                )
            )

            continue

        if current_words + len(words) > max_words:

            if current:
                result.append(" ".join(current))

            current = [paragraph]
            current_words = len(words)

        else:

            current.append(paragraph)
            current_words += len(words)

    if current:
        result.append(" ".join(current))

    return result


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks(
    pages,
    method="paragraph",
    version=1
):

    output = []

    for page in pages:

        if method == "fixed":
            page_chunks = fixed_chunking(page["text"])
        else:
            page_chunks = paragraph_chunking(page["text"])

        for chunk_number, chunk_text in enumerate(page_chunks):

            chunk_id = hashlib.md5(
                (
                    f"{page['document']}_"
                    f"{version}_"
                    f"{page['page']}_"
                    f"{chunk_number}_"
                    f"{chunk_text}"
                ).encode()
            ).hexdigest()

            output.append({

                "id": chunk_id,

                "text": chunk_text,

                "document": page["document"],

                "page": page["page"],

                "chunk_number": chunk_number,

                "version": version,

                "active": True

            })

    return output


# ============================================================
# ADD / UPDATE DOCUMENT
# ============================================================

def add_document(
    file_bytes,
    filename,
    chunk_method="paragraph"
):

    global documents
    global chunks

    # --------------------------------------------------------
    # Streamlit UploadedFile support
    # --------------------------------------------------------

    if hasattr(file_bytes, "getvalue"):
        file_bytes = file_bytes.getvalue()

    elif hasattr(file_bytes, "read"):
        file_bytes = file_bytes.read()

    if not isinstance(file_bytes, bytes):
        file_bytes = bytes(file_bytes)

    filename = os.path.basename(filename)

    file_hash = calculate_file_hash(file_bytes)

    # --------------------------------------------------------
    # Find previous versions
    # --------------------------------------------------------

    previous_versions = [
        doc
        for doc in documents
        if doc["filename"] == filename
    ]

    # --------------------------------------------------------
    # EXACT DUPLICATE
    # --------------------------------------------------------

    for doc in previous_versions:

        if doc.get("file_hash") == file_hash:

            return {
                "status": "duplicate",
                "message":
                    f"{filename} is already indexed "
                    f"as version {doc.get('version', 1)}."
            }

    # --------------------------------------------------------
    # VERSION NUMBER
    # --------------------------------------------------------

    if previous_versions:

        version = max(
            doc.get("version", 1)
            for doc in previous_versions
        ) + 1

        # Old versions remain stored,
        # but are no longer searchable.
        for doc in documents:

            if doc["filename"] == filename:
                doc["active"] = False

        for chunk in chunks:

            if chunk["document"] == filename:
                chunk["active"] = False

        status = "updated"

    else:

        version = 1
        status = "success"

    # --------------------------------------------------------
    # EXTRACT
    # --------------------------------------------------------

    pages = extract_pdf(
        file_bytes,
        filename
    )

    if not pages:

        return {
            "status": "error",
            "message":
                f"No readable text found in {filename}."
        }

    # --------------------------------------------------------
    # CREATE NEW CHUNKS
    # --------------------------------------------------------

    new_chunks = create_chunks(
        pages,
        method=chunk_method,
        version=version
    )

    # --------------------------------------------------------
    # DOCUMENT METADATA
    # --------------------------------------------------------

    document_id = hashlib.sha256(
        f"{filename}_{file_hash}".encode()
    ).hexdigest()[:16]

    document_info = {

        "document_id": document_id,

        "filename": filename,

        "pages": len(pages),

        "chunks": len(new_chunks),

        "version": version,

        "file_hash": file_hash,

        "chunk_method": chunk_method,

        "active": True,

        "indexed_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }

    # --------------------------------------------------------
    # STORE NEW VERSION
    # --------------------------------------------------------

    documents.append(document_info)

    chunks.extend(new_chunks)

    # --------------------------------------------------------
    # REBUILD ACTIVE INDEX
    # --------------------------------------------------------

    rebuild_indexes()

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if status == "updated":

        return {
            "status": "updated",
            "message":
                f"{filename} updated successfully "
                f"to Version {version}. "
                f"Version {version - 1} has been retained."
        }

    return {
        "status": "success",
        "message":
            f"{filename} indexed successfully "
            f"as Version 1."
    }


# ============================================================
# DELETE ALL VERSIONS OF A DOCUMENT
# ============================================================

def delete_document(filename):

    global documents
    global chunks

    documents = [
        doc
        for doc in documents
        if doc["filename"] != filename
    ]

    chunks = [
        chunk
        for chunk in chunks
        if chunk["document"] != filename
    ]

    rebuild_indexes()


# ============================================================
# REBUILD INDEXES
# ============================================================

def rebuild_indexes():

    global faiss_index
    global bm25_index
    global indexed_chunks

    # --------------------------------------------------------
    # ONLY ACTIVE VERSION
    # --------------------------------------------------------

    indexed_chunks = [
        chunk
        for chunk in chunks
        if chunk.get("active", True)
    ]

    if not indexed_chunks:

        faiss_index = None
        bm25_index = None

        return

    texts = [
        chunk["text"]
        for chunk in indexed_chunks
    ]

    # --------------------------------------------------------
    # DENSE EMBEDDINGS
    # --------------------------------------------------------

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # --------------------------------------------------------
    # FAISS
    # --------------------------------------------------------

    dimension = embeddings.shape[1]

    faiss_index = faiss.IndexFlatIP(
        dimension
    )

    faiss_index.add(
        embeddings.astype("float32")
    )

    # --------------------------------------------------------
    # BM25
    # --------------------------------------------------------

    tokenized_documents = [
        text.lower().split()
        for text in texts
    ]

    bm25_index = BM25Okapi(
        tokenized_documents
    )


# ============================================================
# VECTOR SEARCH
# ============================================================

def vector_search(
    query,
    top_k=10
):

    if faiss_index is None:
        return []

    if not indexed_chunks:
        return []

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = faiss_index.search(
        query_embedding.astype("float32"),
        min(top_k, len(indexed_chunks))
    )

    results = []

    for score, index in zip(
        scores[0],
        indices[0]
    ):

        if index == -1:
            continue

        result = indexed_chunks[index].copy()

        result["vector_score"] = float(score)

        results.append(result)

    return results


# ============================================================
# BM25 SEARCH
# ============================================================

def bm25_search(
    query,
    top_k=10
):

    if bm25_index is None:
        return []

    if not indexed_chunks:
        return []

    tokenized_query = query.lower().split()

    scores = bm25_index.get_scores(
        tokenized_query
    )

    top_indices = np.argsort(
        scores
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        result = indexed_chunks[index].copy()

        result["bm25_score"] = float(
            scores[index]
        )

        results.append(result)

    return results


# ============================================================
# NORMALIZE SCORES
# ============================================================

def normalize_scores(
    results,
    key
):

    if not results:
        return results

    scores = [
        r.get(key, 0)
        for r in results
    ]

    minimum = min(scores)
    maximum = max(scores)

    for result in results:

        score = result.get(
            key,
            0
        )

        if maximum == minimum:

            result[
                f"{key}_normalized"
            ] = 0.0

        else:

            result[
                f"{key}_normalized"
            ] = (
                (score - minimum)
                /
                (maximum - minimum)
            )

    return results


# ============================================================
# HYBRID SEARCH
# ============================================================

def hybrid_search(
    query,
    top_k=10
):

    # Wider candidate pool
    vector_results = vector_search(
        query,
        top_k=20
    )

    keyword_results = bm25_search(
        query,
        top_k=20
    )

    vector_results = normalize_scores(
        vector_results,
        "vector_score"
    )

    keyword_results = normalize_scores(
        keyword_results,
        "bm25_score"
    )

    combined = {}

    # Dense = 60%
    for result in vector_results:

        result_id = result["id"]

        combined[result_id] = result

        combined[result_id]["hybrid_score"] = (
            0.6 *
            result.get(
                "vector_score_normalized",
                0
            )
        )

    # BM25 = 40%
    for result in keyword_results:

        result_id = result["id"]

        if result_id not in combined:

            combined[result_id] = result

            combined[result_id]["hybrid_score"] = 0.0

        combined[result_id]["hybrid_score"] += (
            0.4 *
            result.get(
                "bm25_score_normalized",
                0
            )
        )

    results = list(
        combined.values()
    )

    results.sort(
        key=lambda x:
            x.get(
                "hybrid_score",
                0
            ),
        reverse=True
    )

    return results[:top_k]


# ============================================================
# RERANK
# ============================================================

def rerank(
    query,
    candidates,
    top_k=5
):

    if not candidates:
        return []

    pairs = [
        [
            query,
            candidate["text"]
        ]
        for candidate in candidates
    ]

    scores = reranker.predict(
        pairs
    )

    for candidate, score in zip(
        candidates,
        scores
    ):

        candidate["rerank_score"] = float(
            score
        )

    candidates.sort(
        key=lambda x:
            x.get(
                "rerank_score",
                -999
            ),
        reverse=True
    )

    return candidates[:top_k]


# ============================================================
# FULL RETRIEVAL PIPELINE
# ============================================================

def retrieve(
    query,
    top_k=5
):

    candidates = hybrid_search(
        query,
        top_k=20
    )

    final_results = rerank(
        query,
        candidates,
        top_k=top_k
    )

    return final_results


# ============================================================
# EVIDENCE CHECK
# ============================================================

def has_sufficient_evidence(
    results,
    threshold=-999
):

    if not results:
        return False

    best_score = results[0].get(
        "rerank_score",
        -999
    )

    return best_score >= threshold


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(results):

    context = []

    for i, result in enumerate(results):

        context.append(
            f"""
SOURCE [{i + 1}]

Document: {result['document']}

Page: {result['page']}

Version: {result.get('version', 1)}

Chunk: {result['chunk_number']}

Hybrid Score: {result.get('hybrid_score', 0):.4f}

Reranker Score: {result.get('rerank_score', 0):.4f}

Evidence:
{result['text']}
"""
        )

    return "\n".join(context)


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    query,
    results
):

    if not results:

        return (
            "I could not find enough evidence "
            "in the uploaded documents to answer "
            "this question."
        )

    if client is None:

        return (
            "Evidence was retrieved successfully, "
            "but the OpenAI API key is not configured."
        )

    context = build_context(results)

    prompt = f"""
You are EvidenceBench, a citation-grounded question answering system.

Answer the user's question ONLY using the supplied evidence.

Rules:

1. Do not invent information.
2. Do not use outside knowledge.
3. If the evidence is insufficient, say that clearly.
4. Every important factual statement must have a citation.
5. Use citations in this format:
   [Source 1]
   [Source 2]
6. If sources conflict, explicitly mention the conflict.
7. Prefer evidence with stronger retrieval scores.
8. Give a concise answer.
9. Do not mention information that is not supported by the supplied evidence.

USER QUESTION:

{query}

SUPPLIED EVIDENCE:

{context}
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    return response.output_text