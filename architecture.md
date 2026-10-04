# EvidenceBench Architecture

```text
                         ┌─────────────────────┐
                         │      User / UI      │
                         │     Streamlit       │
                         └──────────┬──────────┘
                                    │
                           Upload / Question
                                    │
                    ┌───────────────▼───────────────┐
                    │         Ingestion Layer       │
                    │                               │
                    │ PDF / Text / Markdown         │
                    │ Metadata + Page Information   │
                    │ Hash + Version Detection      │
                    └───────────────┬───────────────┘
                                    │
                              Chunking Layer
                         ┌──────────┴──────────┐
                         │                     │
                  Fixed/Recursive         Alternative
                     Chunking              Chunking
                         │                     │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │       Retrieval Layer         │
                    │                               │
                    │ Dense Vector Retrieval        │
                    │ Keyword/BM25 Retrieval        │
                    └───────────────┬───────────────┘
                                    │
                           Hybrid Fusion
                         Dense + Keyword
                                    │
                    ┌───────────────▼───────────────┐
                    │        Candidate Set          │
                    │      Top-N wider pool         │
                    └───────────────┬───────────────┘
                                    │
                              Reranking
                                    │
                    ┌───────────────▼───────────────┐
                    │       Evidence Selection      │
                    │                               │
                    │ Scores + document + page      │
                    └───────────────┬───────────────┘
                                    │
                         Evidence Strength Check
                              /           \
                           Strong         Weak
                             │              │
                             ▼              ▼
                       LLM Generation    Abstain
                             │
                             ▼
                    ┌──────────────────────┐
                    │ Answer + Citations   │
                    │ Page-level Sources    │
                    └──────────────────────┘