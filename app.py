import streamlit as st
import rag_engine as rag


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="EvidenceBench",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.caption(
    "Retrieval-Augmented Generation with evidence, citations and reranking"
)

st.title("📊 Knowledge Base")


# ============================================================
# SIDEBAR - DOCUMENT UPLOAD
# ============================================================

with st.sidebar:

    st.header("📁 Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True
    )

    chunk_method = st.selectbox(
        "Chunking method",
        [
            "paragraph",
            "fixed"
        ]
    )

    index_button = st.button(
        "📥 Index Documents",
        use_container_width=True
    )


# ============================================================
# INDEX DOCUMENTS
# ============================================================

if index_button:

    if not uploaded_files:

        st.warning(
            "Please upload at least one PDF document."
        )

    else:

        for uploaded_file in uploaded_files:

            with st.spinner(
                f"Indexing {uploaded_file.name}..."
            ):

                try:

                    result = rag.add_document(
                        uploaded_file,
                        uploaded_file.name,
                        chunk_method
                    )

                    # ----------------------------------------
                    # DUPLICATE
                    # ----------------------------------------

                    if result["status"] == "duplicate":

                        st.warning(
                            f"⚠️ {result['message']}"
                        )

                    # ----------------------------------------
                    # UPDATED VERSION
                    # ----------------------------------------

                    elif result["status"] == "updated":

                        st.info(
                            f"🔄 {result['message']}"
                        )

                    # ----------------------------------------
                    # NEW DOCUMENT
                    # ----------------------------------------

                    else:

                        st.success(
                            f"✅ {result['message']}"
                        )

                except Exception as e:

                    st.error(
                        f"❌ Error indexing "
                        f"{uploaded_file.name}: {e}"
                    )

        st.rerun()


# ============================================================
# KNOWLEDGE BASE STATISTICS
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Documents",
        len(rag.documents)
    )

with col2:

    st.metric(
        "Chunks",
        len(rag.chunks)
    )


# ============================================================
# INDEXED DOCUMENTS
# ============================================================

st.subheader("📚 Indexed Documents")


if not rag.documents:

    st.info(
        "No documents indexed yet. "
        "Upload a PDF from the sidebar."
    )

else:

    with st.expander(
        "View indexed documents",
        expanded=True
    ):

        for i, doc in enumerate(rag.documents):

            col1, col2 = st.columns(
                [5, 1]
            )

            # --------------------------------------------
            # DOCUMENT INFORMATION
            # --------------------------------------------

            with col1:

                st.write(
                    f"📄 **{doc['filename']}**"
                )

                st.caption(
                    f"Version: {doc.get('version', 1)}  |  "
                    f"Pages: {doc['pages']}  |  "
                    f"Chunks: {doc['chunks']}  |  "
                    f"Method: {doc.get('chunk_method', 'paragraph')}"
                )

                st.caption(
                    f"Indexed: "
                    f"{doc.get('indexed_at', 'Unknown')}"
                )

            # --------------------------------------------
            # DELETE BUTTON
            # --------------------------------------------

            with col2:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{i}",
                    use_container_width=True
                ):

                    rag.delete_document(
                        doc["filename"]
                    )

                    st.success(
                        f"Deleted {doc['filename']}"
                    )

                    st.rerun()


# ============================================================
# ASK DOCUMENTS
# ============================================================

st.divider()

st.header("💬 Ask your documents")

query = st.text_input(
    "Enter your question",
    placeholder=(
        "Ask something about your uploaded documents..."
    )
)


# ============================================================
# ASK BUTTON
# ============================================================

if st.button("🔎 Ask"):

    # --------------------------------------------------------
    # EMPTY QUESTION
    # --------------------------------------------------------

    if not query.strip():

        st.warning(
            "Please enter a question."
        )

    # --------------------------------------------------------
    # NO DOCUMENTS
    # --------------------------------------------------------

    elif not rag.chunks:

        st.warning(
            "Please upload and index documents first."
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    else:

        with st.spinner(
            "Searching evidence and generating answer..."
        ):

            try:

                # Retrieve evidence
                results = rag.retrieve(
                    query,
                    top_k=5
                )

                # Generate answer
                answer = rag.generate_answer(
                    query,
                    results
                )

            except Exception as e:

                st.error(
                    f"❌ Error while answering: {e}"
                )

                results = []
                answer = None

        # ----------------------------------------------------
        # ANSWER
        # ----------------------------------------------------

        if answer:

            st.header("🤖 Answer")

            st.write(answer)

        # ----------------------------------------------------
        # RETRIEVED EVIDENCE
        # ----------------------------------------------------

        st.header("📑 Retrieved Evidence")

        if not results:

            st.warning(
                "No relevant evidence was found."
            )

        else:

            for i, result in enumerate(results):

                document = result.get(
                    "document",
                    "Unknown document"
                )

                page = result.get(
                    "page",
                    "Unknown"
                )

                chunk_number = result.get(
                    "chunk_number",
                    "Unknown"
                )

                hybrid_score = result.get(
                    "hybrid_score",
                    0
                )

                reranker_score = result.get(
                    "rerank_score",
                    0
                )

                # ----------------------------------------
                # SOURCE EXPANDER
                # ----------------------------------------

                with st.expander(
                    f"📄 Source {i + 1}: "
                    f"{document} — Page {page}"
                ):

                    st.write(
                        f"**Document:** {document}"
                    )

                    st.write(
                        f"**Page:** {page}"
                    )

                    st.write(
                        f"**Chunk:** {chunk_number}"
                    )

                    st.write(
                        f"**Hybrid score:** "
                        f"{hybrid_score:.4f}"
                    )

                    st.write(
                        f"**Reranker score:** "
                        f"{reranker_score:.4f}"
                    )

                    st.divider()

                    st.write(
                        result.get(
                            "text",
                            "Evidence text unavailable."
                        )
                    )


# ============================================================
# RAG PIPELINE
# ============================================================

st.divider()

st.subheader("⚙️ RAG Pipeline")

st.markdown(
    """
**PDF Document**
→ **Text Extraction**
→ **Chunking**
→ **Dense Retrieval + Keyword Retrieval**
→ **Hybrid Fusion**
→ **Reranking**
→ **Evidence Selection**
→ **LLM Generation**
→ **Citations**
"""
)