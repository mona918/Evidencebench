"""
EvidenceBench Evaluation Runner

Runs the benchmark and records retrieval/answering results.

IMPORTANT:
This file is an evaluation framework. Do not manually enter fake scores.
Run it against the actual system and report the resulting numbers.
"""

import csv
import time
from pathlib import Path


BENCHMARK_FILE = Path("benchmark.csv")
RESULT_FILE = Path("evaluation_results.csv")


def load_benchmark():
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def normalize(text):
    return " ".join(str(text).lower().split())


def keyword_match(answer, expected):
    answer = normalize(answer)
    expected = normalize(expected)

    if not expected:
        return False

    return expected in answer or answer in expected


def calculate_basic_metrics(results):
    total = len(results)

    if total == 0:
        return {}

    correct = sum(r["correct"] for r in results)

    return {
        "total_questions": total,
        "correct_answers": correct,
        "answer_accuracy": round(correct / total, 4),
    }


def run_evaluation():
    benchmark = load_benchmark()

    print(f"Loaded {len(benchmark)} benchmark questions.")
    print("Connect the retrieval/answer function from rag_engine.py below.")
    print()

    results = []

    for item in benchmark:
        question = item["question"]

        # ---------------------------------------------------------
        # Replace this section with your actual EvidenceBench call.
        #
        # Example:
        # result = answer_question(question)
        # answer = result["answer"]
        # ---------------------------------------------------------

        answer = ""
        retrieved = []
        citation = ""

        start = time.perf_counter()

        # Placeholder until connected to your actual RAG function.
        # This prevents fake evaluation results.
        status = "NOT_RUN"

        latency = time.perf_counter() - start

        correct = (
            keyword_match(answer, item["expected_answer"])
            if answer
            else False
        )

        results.append({
            "id": item["id"],
            "type": item["type"],
            "question": question,
            "expected_answer": item["expected_answer"],
            "actual_answer": answer,
            "citation": citation,
            "retrieved_chunks": len(retrieved),
            "latency_seconds": round(latency, 4),
            "correct": int(correct),
            "status": status,
            "should_abstain": item["should_abstain"],
        })

    with open(RESULT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    metrics = calculate_basic_metrics(results)

    print("Evaluation file created:", RESULT_FILE)
    print(metrics)


if __name__ == "__main__":
    run_evaluation()