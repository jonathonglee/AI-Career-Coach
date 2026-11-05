"""Retrieval-augmented comparisons against *fictional*, project-authored resume examples.

These profiles illustrate skills people might bring to a role. They are not
real applicants, market measurements, or a representation of hiring odds.
"""
from pathlib import Path
from .retrieval import load_passages, rank_passages, Passage

BENCHMARK_DIR = Path(__file__).resolve().parents[1] / "benchmark_resumes"


def retrieve_benchmarks(job: str, target_role: str = "", top_k: int = 3) -> list[Passage]:
    """Find examples relevant to a job description/role, not the student's identity."""
    query = f"{target_role.strip()} {job[:5000].strip()}".strip()
    if not query:
        return []
    return rank_passages(query, load_passages(BENCHMARK_DIR), top_k=top_k)
