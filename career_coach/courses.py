"""Local TF-IDF RAG retrieval over the UA 2026–2027 Eller-subject catalog.

Data comes from a CSV export filtered by the subject prefixes listed by the
Eller College. `offering_unit` makes it possible to exclude cross-listed courses
owned by another department without confusing subject prefixes and ownership.
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import json
import re
from .retrieval import Passage, rank_passages

CATALOG_PATH = Path(__file__).resolve().parents[1] / "course_catalog" / "eller_courses_2026_2027.json"
ELLER_SUBJECT_CODES = frozenset((
    "ACCT", "BCOM", "BNAD", "BNAN", "ECON", "ENTR", "FIN",
    "MGMT", "MIS", "MKTG", "OSCM",
))
CODE_PATTERN = re.compile(r"\b[A-Za-z]{2,6}\s*[- ]?\s*\d{3}[A-Za-z]?\b")


@dataclass(frozen=True)
class Course:
    code: str
    title: str
    level: str
    credits: float
    description: str
    index_terms: str
    url: str
    offering_unit: str = ""
    course_id: str = ""
    requisites: str = ""
    eller_owned: bool = True


@lru_cache(maxsize=4)
def load_courses(path: Path = CATALOG_PATH) -> list[Course]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [Course(**course) for course in payload["courses"]]


def parse_completed_courses(raw: str) -> set[str]:
    """Normalize 'MIS545, MIS 531' to {'MIS545', 'MIS531'}."""
    return {re.sub(r"\s|-", "", match.group(0)).upper()
            for match in CODE_PATTERN.finditer(raw)}


def retrieve_courses(query: str, level: str = "All", completed: str = "", top_k: int = 5,
                     catalog_path: Path = CATALOG_PATH,
                     subjects: tuple[str, ...] | None = None,
                     strict_ownership: bool = False) -> list[tuple[Course, float]]:
    """Filter the Eller dataset first, then retrieve courses relevant to a career goal."""
    if not query.strip():
        return []
    allowed_subjects = (set(subjects) if subjects is not None else ELLER_SUBJECT_CODES)
    completed_codes = parse_completed_courses(completed)
    candidates = [c for c in load_courses(catalog_path)
                  if c.code.upper() not in completed_codes
                  and (level == "All" or c.level == level)
                  and re.match(r"^[A-Z]+", c.code).group(0) in allowed_subjects
                  and (not strict_ownership or c.eller_owned)]
    by_code = {course.code: course for course in candidates}
    passages = [Passage(
        source=course.code,
        text=(f"{course.code} {course.title}; {course.offering_unit}. "
              f"{course.description[:2600]}\n"
              f"Search terms (editorial, not catalog facts): {course.index_terms}"))
        for course in candidates]
    ranked = rank_passages(query, passages, top_k=top_k)
    return [(by_code[p.source], p.score) for p in ranked]


def format_course_context(matches: list[tuple[Course, float]]) -> str:
    if not matches:
        return "No Eller catalog courses were retrieved for this query."
    return "\n\n".join(
        f"[Course: {c.code}; Catalog record: {c.url}; level: {c.level}; "
        f"minimum credits: {c.credits}; offering unit: {c.offering_unit}]\n"
        f"Title: {c.title}\nCatalog description (excerpt): {c.description[:2300]}\n"
        f"Catalog requisites (if listed): {c.requisites[:450] or 'Not stated in export'}"
        for c, _ in matches)
