# EvidenceBench Failure Log

This document records retrieval and generation failures observed during
development and evaluation.

The purpose is to identify failure causes and improvements rather than
hide incorrect results.

| ID | Failure Type | Example / Scenario | Cause | Impact | Planned Fix |
|---|---|---|---|---|---|
| F01 | Retrieval | Query uses different wording from document | Lexical mismatch | Relevant chunk may rank lower | Hybrid retrieval |
| F02 | Retrieval | Keyword query misses semantic meaning | Exact terms absent | Relevant evidence not retrieved | Dense retrieval |
| F03 | Retrieval | Dense search misses exact terminology | Embedding similarity limitation | Correct chunk may rank lower | Hybrid fusion |
| F04 | Ranking | Relevant result appears below unrelated result | Ranking noise | Lower Recall@K | Reranking |
| F05 | Ranking | Several chunks contain similar information | Duplicate semantic content | Redundant context | Deduplication |
| F06 | Citation | Answer contains evidence but citation is missing | Citation alignment failure | Lower citation coverage | Citation validation |
| F07 | Citation | Citation points to wrong page | Metadata mismatch | Incorrect evidence reference | Page-level metadata |
| F08 | Abstention | Question has no supporting evidence | No relevant retrieval | Hallucination risk | Abstention threshold |
| F09 | Abstention | Weak evidence receives a response | Threshold too permissive | Potential hallucination | Confidence threshold |
| F10 | Versioning | Same file uploaded again | Exact duplicate | Duplicate index entries | Hash-based duplicate detection |
| F11 | Versioning | Updated document uploaded | Content hash changed | Old information can become stale | Document versioning |
| F12 | Conflict | Two versions contain different dates | Conflicting evidence | Ambiguous answer | Version-aware retrieval |
| F13 | Chunking | Important information split between chunks | Poor chunk boundary | Retrieval loses context | Alternative chunking strategy |
| F14 | Chunking | Chunk is too large | Excess irrelevant text | Lower precision | Smaller chunks |
| F15 | Chunking | Chunk is too small | Context loss | Lower answer quality | Overlap / semantic chunking |
| F16 | Query | User asks an ambiguous question | Insufficient context | Wrong interpretation | Clarification / abstention |
| F17 | Generation | LLM adds unsupported information | Generation beyond evidence | Hallucination | Strict grounding prompt |
| F18 | Retrieval | Relevant document is not active | Version filtering | Evidence unavailable | Active-version index |
| F19 | Performance | Reranking increases response time | Cross-encoder computation | Higher latency | Candidate-size tuning |
| F20 | Performance | Embedding retrieval is slow | Large candidate set | Higher latency | Index optimization |

## Observed Failures

Only failures actually observed during testing should be added below.

### F-OBS-01
- Question:
- Expected:
- Actual:
- Retrieved evidence:
- Failure cause:
- Fix:

### F-OBS-02
- Question:
- Expected:
- Actual:
- Retrieved evidence:
- Failure cause:
- Fix:

### F-OBS-03
- Question:
- Expected:
- Actual:
- Retrieved evidence:
- Failure cause:
- Fix:

## Notes

The failure categories above represent anticipated failure modes.
The observed-failure section should contain real failures produced during
benchmark execution.