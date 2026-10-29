"""Local retrieval: TF-IDF vector search over curated career-guidance passages."""
from dataclasses import dataclass
from pathlib import Path
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "knowledge_base"


@dataclass(frozen=True)
class Passage:
    source: str
    text: str
    score: float = 0.0


def load_passages(directory: Path = KB_DIR) -> list[Passage]:
    passages = []
    for path in sorted(directory.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        for chunk in re.split(r"\n\s*---\s*\n", raw):
            chunk = chunk.strip()
            if chunk:
                passages.append(Passage(source=path.name, text=chunk))
    return passages


def retrieve(query: str, top_k: int = 3, directory: Path = KB_DIR) -> list[Passage]:
    passages = load_passages(directory)
    if not passages or not query.strip():
        return []
    corpus = [p.text for p in passages]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(corpus)
        query_vec = vectorizer.transform([query[:6000]])
        scores = cosine_similarity(query_vec, matrix).ravel()
    except ValueError:
        return []
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [Passage(passages[i].source, passages[i].text, float(scores[i]))
            for i in ranked[:top_k] if scores[i] > 0]


def format_context(passages: list[Passage]) -> str:
    if not passages:
        return "No matching knowledge-base passages were retrieved."
    return "\n\n".join(f"[Source: {p.source}]\n{p.text}" for p in passages)
