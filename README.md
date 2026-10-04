# EvidenceBench 🔎

EvidenceBench is a full-stack Retrieval-Augmented Generation (RAG) research workspace designed to answer questions from uploaded documents using retrievable and verifiable evidence.

Instead of relying only on an LLM's internal knowledge, EvidenceBench retrieves relevant document chunks, reranks them, and uses the retrieved evidence to generate grounded answers with page-level source citations.

## 🚀 Live Demo

Streamlit App:
PASTE-YOUR-STREAMLIT-LINK-HERE

## 📌 Project Overview

Large Language Models can generate fluent answers, but they may sometimes provide information that is not supported by the available documents.

EvidenceBench addresses this problem using a Retrieval-Augmented Generation pipeline.

The system allows a user to:

1. Upload research documents.
2. Extract text and page-level metadata.
3. Split documents into searchable chunks.
4. Index chunks using dense vector embeddings and keyword retrieval.
5. Retrieve relevant evidence for a question.
6. Combine retrieval results using hybrid fusion.
7. Rerank the retrieved candidates.
8. Generate an answer using the retrieved evidence.
9. Display page-level citations.
10. Abstain when sufficient evidence is not available.
11. Detect duplicate documents.
12. Maintain different versions of updated documents.

## ✨ Features

### 📄 1. Document Ingestion

EvidenceBench supports document ingestion through PDF files.

During ingestion, the system:

- Extracts text from the document.
- Preserves page information.
- Generates document metadata.
- Creates searchable chunks.
- Calculates a document hash.
- Detects duplicate uploads.
- Detects updated versions of documents.

Each chunk retains information such as:

- Document name
- Version
- Page number
- Chunk ID
- Chunk text

### 🔄 2. Duplicate Detection

EvidenceBench calculates a hash for each uploaded document.

If the exact same document is uploaded again, the system detects it as a duplicate instead of creating another copy.

Example:

Upload 1:
Student_Handbook.pdf
Hash: ABC123

Upload 2:
Student_Handbook.pdf
Hash: ABC123

Result:
Duplicate document detected.

This prevents unnecessary duplicate documents from being indexed.

### 🗂️ 3. Document Versioning

If a document with the same filename is changed, EvidenceBench creates a new version instead of deleting the previous version.

Example:

Student_Handbook.pdf

Version 1
Version 2

The previous version is preserved, while the latest version becomes the active version used for retrieval.

This makes it possible to track document updates and maintain historical versions.

### ✂️ 4. Multiple Chunking Strategies

EvidenceBench supports multiple strategies for splitting documents into smaller searchable pieces.

#### Fixed-Size Chunking

The document is divided into chunks of a fixed size.

#### Sentence-Based Chunking

The document is divided based on sentence boundaries.

Different chunking strategies can affect retrieval quality because they determine how much context is available in each retrieved chunk.

### 🔍 5. Hybrid Retrieval

EvidenceBench combines two retrieval approaches.

#### Dense Vector Retrieval

The document chunks are converted into semantic embeddings using Sentence Transformers.

FAISS is then used to perform vector similarity search.

Dense retrieval is useful when the question and document use different wording but have similar meanings.

#### Keyword Retrieval

BM25 is used for keyword-based retrieval.

BM25 is useful when important words or phrases from the question appear directly in the document.

#### Hybrid Fusion

The two retrieval scores are combined:

Hybrid Score = 0.6 × Vector Score + 0.4 × BM25 Score

This allows the system to combine semantic matching and keyword matching.

### 🎯 6. Candidate Retrieval and Reranking

Instead of immediately using only the top result, EvidenceBench retrieves a wider candidate set.

The candidate chunks are then reranked using a Cross-Encoder.

Reranking model:

cross-encoder/ms-marco-MiniLM-L-6-v2

The pipeline is:

Question
↓
Dense Retrieval + BM25
↓
Hybrid Fusion
↓
Candidate Set
↓
Cross-Encoder Reranking
↓
Best Evidence

This helps improve the relevance of the evidence provided to the LLM.

### 🤖 7. Retrieval-Augmented Generation

After retrieving relevant evidence, the selected document chunks are provided to the LLM together with the user's question.

The LLM is instructed to generate an answer based on the retrieved evidence.

The overall process is:

User Question
↓
Retrieve Evidence
↓
Rerank Evidence
↓
Build Context
↓
LLM
↓
Grounded Answer

The goal is to reduce unsupported or hallucinated responses.

### 📌 8. Page-Level Citations

EvidenceBench preserves page metadata during document ingestion.

Therefore, retrieved evidence can be shown with its document and page information.

Example:

Source 1
Document: Student_Handbook.pdf
Page: 1
Version: 2

This allows users to trace the generated answer back to the original document.

### 🛑 9. Evidence-Based Abstention

A reliable RAG system should not answer every question.

If relevant evidence cannot be found in the uploaded documents, EvidenceBench can abstain instead of generating an unsupported answer.

Example:

Question:
What is the population of Mars?

Result:
Insufficient evidence found in the uploaded documents.

This prevents the system from pretending to know information that is not supported by the available evidence.

## 🧪 Testing

The current system has been tested for the following core behaviours.

### PDF Ingestion

PDF
↓
Text Extraction
↓
Chunk Creation
↓
Indexing

### Question Answering

Questions related to uploaded documents can be answered using retrieved evidence.

### Page-Level Citation

Retrieved answers display the corresponding document and page.

### Abstention

Questions unrelated to the uploaded documents can result in an evidence-unavailable response.

### Duplicate Detection

Uploading the same document again is detected as a duplicate.

### Document Versioning

Uploading an updated document with the same filename creates a new version while preserving the previous version.

## 🏗️ System Architecture

                         ┌───────────────────┐
                         │       User        │
                         └─────────┬─────────┘
                                   │
                                   ↓
                         ┌───────────────────┐
                         │    Streamlit UI   │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ↓                             ↓
            Document Upload                 User Question
                    │                             │
                    ↓                             ↓
           ┌─────────────────┐          ┌─────────────────┐
           │ Text Extraction │          │    Retrieval    │
           │    (PyMuPDF)    │          │     Engine      │
           └────────┬────────┘          └────────┬────────┘
                    │                            │
                    ↓                            │
           ┌─────────────────┐                    │
           │     Chunking    │                    │
           └────────┬────────┘                    │
                    │                            │
              ┌─────┴─────┐                      │
              ↓           ↓                      │
       ┌────────────┐ ┌────────────┐             │
       │ Embeddings │ │    BM25    │             │
       └─────┬──────┘ └─────┬──────┘             │
             ↓              ↓                     │
       ┌────────────┐ ┌────────────┐             │
       │    FAISS   │ │  Keyword   │             │
       │   Search   │ │   Search   │             │
       └─────┬──────┘ └─────┬──────┘             │
             │              │                     │
             └──────┬───────┘                     │
                    ↓                             │
             ┌──────────────┐                     │
             │ Hybrid Fusion│◄────────────────────┘
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │  Reranking   │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │   Evidence   │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │     LLM      │
             └──────┬───────┘
                    ↓
          ┌─────────────────────┐
          │ Answer + Citations  │
          └─────────────────────┘

## 🔄 Complete RAG Pipeline

Document
↓
PDF Text Extraction
↓
Metadata Creation
↓
Duplicate / Version Detection
↓
Chunking
↓
Embeddings + BM25
↓
FAISS + Keyword Retrieval
↓
Hybrid Fusion
↓
Candidate Set
↓
Reranking
↓
Best Evidence
↓
Context Builder
↓
LLM
↓
Answer + Page Citation

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| PDF Processing | PyMuPDF |
| Embeddings | Sentence Transformers |
| Vector Search | FAISS |
| Keyword Retrieval | BM25 |
| Reranking | Cross-Encoder |
| LLM | OpenAI API |
| Numerical Computing | NumPy |
| Data Processing | Pandas |
| Environment Variables | python-dotenv |

## 📁 Project Structure

EvidenceBench/
│
├── app.py
├── rag_engine.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/

### app.py

The Streamlit application.

It handles:

- User interface
- PDF upload
- Chunking selection
- Document indexing
- Question input
- Answer display
- Evidence display
- Document/version display

### rag_engine.py

Contains the core RAG pipeline.

It handles:

- PDF text extraction
- Metadata creation
- Hash generation
- Duplicate detection
- Document versioning
- Chunking
- Embedding generation
- FAISS retrieval
- BM25 retrieval
- Hybrid retrieval
- Reranking
- Context construction
- LLM answer generation
- Evidence handling

### requirements.txt

Contains the Python libraries required to run EvidenceBench.

### .gitignore

Prevents sensitive and unnecessary files from being uploaded to GitHub.

Example:

.env
__pycache__/
*.pyc
data/
*.pkl

## ⚙️ Installation

### 1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL

cd EvidenceBench

### 2. Install Dependencies

pip install -r requirements.txt

## 🔐 Environment Variables

Create a .env file in the project directory.

OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-6-luna

The .env file should never be uploaded to GitHub.

Make sure .env is included in .gitignore.

## ▶️ Run the Application Locally

Start the Streamlit application using:

python -m streamlit run app.py

The application will open in the browser.

## 📖 How to Use

### Step 1 — Upload a Document

Upload a supported PDF document through the Streamlit interface.

### Step 2 — Select Chunking Strategy

Choose one of the available chunking strategies.

### Step 3 — Index the Document

The document is processed and indexed.

The system:

Extracts text
↓
Creates chunks
↓
Generates embeddings
↓
Builds FAISS index
↓
Builds BM25 index

### Step 4 — Ask a Question

Enter a question related to the uploaded document.

### Step 5 — Retrieve Evidence

The system retrieves candidate chunks using:

Dense Retrieval + Keyword Retrieval

The results are combined using hybrid fusion.

### Step 6 — Rerank

The retrieved candidates are reranked using the Cross-Encoder.

### Step 7 — Generate Answer

The selected evidence is passed to the LLM.

The final response contains the answer and source information.

## 📊 Evaluation Plan

The project will evaluate different retrieval configurations.

The main configurations are:

Dense Retrieval
vs
Keyword Retrieval
vs
Hybrid Retrieval
vs
Hybrid + Reranker

The purpose is to measure how different retrieval strategies affect the quality of evidence and generated answers.

## 📈 Evaluation Metrics

The benchmark will use retrieval and answer-grounding metrics including:

### Recall@K

Measures whether the relevant evidence appears within the top K retrieved results.

### MRR

Mean Reciprocal Rank measures how highly the first relevant result appears.

### nDCG

Measures ranking quality while considering the relevance of retrieved documents.

### Citation Precision

Measures whether generated citations actually support the answer.

### Citation Coverage

Measures how much of the answer is supported by the cited evidence.

### Abstention Quality

Measures whether the system correctly refuses questions when sufficient evidence is unavailable.

### Latency

Measures the time taken by different stages of the RAG pipeline.

## 🧪 Benchmark Dataset

The project benchmark will contain approximately 40–60 questions.

The questions will include:

### Direct Questions

Questions whose answers are explicitly present in the documents.

### Paraphrased Questions

Questions asking for the same information using different wording.

### Multi-Document Questions

Questions requiring evidence from multiple documents.

### Conflicting Questions

Questions where different documents or versions contain conflicting information.

### Unclear Questions

Questions where the available documents do not provide sufficient evidence.

## 🔬 Experimental Comparison

The retrieval pipeline can be compared using:

Experiment 1:
Dense Retrieval

Experiment 2:
Keyword Retrieval

Experiment 3:
Hybrid Retrieval

Experiment 4:
Hybrid Retrieval + Reranker

The results can then be compared using the benchmark metrics.

## 📝 Failure Analysis

A major part of the project is analysing cases where the system fails.

Potential failure categories include:

- Incorrect retrieval
- Missing evidence
- Poor chunking
- Incorrect ranking
- Conflicting documents
- Unsupported generation
- Incorrect citation
- Abstention failure

The final experiment report will document retrieval/generation failures and their causes.

## 🔎 Observability

The RAG pipeline is designed to make important retrieval information visible.

Important information includes:

Question
↓
Retrieved Chunks
↓
Hybrid Scores
↓
Reranker Scores
↓
Selected Evidence
↓
Generated Answer
↓
Citations

This makes it easier to debug retrieval and generation failures.

## 🔐 Security

API keys and other secrets should never be committed to GitHub.

Use environment variables locally:

OPENAI_API_KEY=your_api_key

For deployment, use the platform's secret management system.

## ☁️ Deployment

EvidenceBench can be deployed using Streamlit Community Cloud.

General deployment process:

GitHub Repository
↓
Streamlit Community Cloud
↓
Configure Secrets
↓
Deploy
↓
Public Streamlit Application

The OpenAI API key should be stored using Streamlit Secrets rather than being written directly into the source code.

Example:

OPENAI_API_KEY = "your_api_key_here"
OPENAI_MODEL = "gpt-6-luna"

## ⚠️ Important Deployment Note

Documents uploaded during a local session may not automatically appear in the deployed application.

The deployed application should therefore be tested independently after deployment.

Recommended deployment tests:

✓ Application loads
✓ PDF can be uploaded
✓ Document can be indexed
✓ Question can be asked
✓ Relevant evidence is retrieved
✓ Citation is displayed
✓ Unsupported question triggers abstention
✓ Duplicate detection works
✓ Versioning works

## 🎯 Project Goals

The main goals of EvidenceBench are:

- Build a complete RAG pipeline.
- Improve retrieval quality using hybrid search.
- Improve ranking using reranking.
- Provide verifiable page-level citations.
- Detect duplicate and updated documents.
- Preserve document versions.
- Avoid unsupported answers.
- Evaluate retrieval performance using a benchmark.
- Analyse retrieval and generation failures.
- Make the RAG pipeline observable and explainable.

## 🚧 Current Status

### Core System

- [x] PDF ingestion
- [x] Page-level metadata
- [x] Document hashing
- [x] Duplicate detection
- [x] Document versioning
- [x] Multiple chunking strategies
- [x] Dense vector retrieval
- [x] Keyword retrieval
- [x] Hybrid retrieval
- [x] Candidate reranking
- [x] LLM answer generation
- [x] Page-level citations
- [x] Evidence-based abstention
- [x] Basic end-to-end testing

### Evaluation

- [ ] 40–60 question benchmark
- [ ] Retrieval metrics
- [ ] Citation metrics
- [ ] Abstention evaluation
- [ ] Dense vs keyword vs hybrid comparison
- [ ] Reranker comparison
- [ ] Failure analysis

### Final Project Package

- [ ] Automated tests and failure log
- [ ] Architecture diagram
- [ ] Final experiment report
- [ ] 5–8 minute project demonstration
- [ ] Final GitHub repository

## 🌟 Why EvidenceBench?

Traditional LLM applications often focus mainly on generating an answer.

EvidenceBench focuses on an additional question:

"Can we verify where the answer came from?"

The project therefore combines:

Retrieval
+
Reranking
+
Evidence
+
Citations
+
Abstention
+
Evaluation

The objective is to create a RAG system that is not only capable of answering questions, but also makes its evidence traceable and verifiable.

## 👨‍💻 Project Information

Project: EvidenceBench

Domain: Retrieval-Augmented Generation / AI / NLP

Type: Full-Stack AI Research Workspace

Primary Language: Python

Interface: Streamlit

## 📜 License

This project is developed for educational and research purposes.